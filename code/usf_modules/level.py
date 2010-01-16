####################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>
#
# This file is part of UltimateSmashFriends
#
# UltimateSmashFriends is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UltimateSmashFriends is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.
##################################################################################

import os, sys
import pygame
import Image

import loaders
import time
from config import config

from debug_utils import LOG, draw_rect

# different in python 2.4 and 2.5
if sys.version_info[0] == 2 and sys.version_info[1] >= 5:
    from xml.etree import ElementTree
else:
    from elementtree import ElementTree

class Block (object):
    """
    An abstraction class to define methods shared by some level objects.

    """
    def __init__(self):
        """
        Not much to do here.
        """
        pass

    def __str__(self):
        return ' '.join(str(self.rects),)

    def draw(self, surface, coords=(0,0), zoom=1):
        """
        Draw this moving bloc on the passed surface, taking account of zoom and
        placement of camera.

        """
        real_coords = (
                int(self.position[0]*zoom)*(config['SIZE'][0]/800.0)+coords[0],
                int(self.position[1]*zoom)*(config['SIZE'][1]/480.0)+coords[1]
                )

        surface.blit(loaders.image(self.texture, zoom=zoom)[0], real_coords)

    def collide_rect(self, (x,y), (h,w)=(1,1)):
        """
        Return True if the point at (x,y) collide this bloc's rects.

        """
        return pygame.Rect(x,y,h,w).collidelist(self.collide_rects) != -1

class VectorBloc (Block):
    """
    This define a bloc that apply a vector to any entity falling/walking on it.

    """
    def __init__(self, rects, position, vector, relative, texture, server=False):
        Block.__init__(self)
        self.rects = rects
        self.relative = relative
        self.texture = os.path.join(
                config['MEDIA_DIRECTORY'],
                "levels",
                texture
                )
        self.vector = vector
        self.position = position
        self.collide_rects = []
        for i in self.rects:
            self.collide_rects.append(
                    pygame.Rect(
                        i[0]+position[0],
                        i[1]+position[1],
                        i[2],
                        i[3]
                        )
                    )

    def apply_vector(self, entity):
        """
        This method simply add the bloc's vector to the passed player.

        """
        entity.vector = [
        entity.vector[0] + self.vector[0],
        entity.vector[1] + self.vector[1]
        ]

class MovingPart (Block):
    """
    This define a level bloc that move, with a defined texture, and a defined
    set of collision rects. It moves following a pattern of (position(x,y):
    time( % maxtime)).

    """
    def __init__(self, rects, texture, patterns, server=False):
        Block.__init__(self)
        #LOG().log('moving block created')
        self.rects = rects
        self.texture = os.path.join(
                config['MEDIA_DIRECTORY'],
                "levels",
                texture
                )
        self.patterns = patterns
        self.position = self.patterns[0]['position']

    def get_movement(self):
        """
        Return the movement between the position at the precedent frame, and
        now, usefull to communicate this movement to another entity.

        """
        return (
                self.position[0] - self.old_position[0],
                self.position[1] - self.old_position[1]
               )

    def update(self, level_time):
        """
        Update the position of the moving bloc, based on time since the bigginig
        of the game, calculating the percentage of time we are between two
        positions. And update the coords of colliding rects.

        """
        # [:] is necessary to get values, instead of copying the object
        # reference.
        self.old_position = self.position[:]
        # get the precedant position of pattern we got by.
        last = (
                self.patterns[-1:]+
                filter(
                    lambda(x):
                    x['time'] <= level_time * 10000 % self.patterns[-1]['time'],
                    self.patterns
                    )
               )[-1]

        # get the next position of pattern we will get by.
        next = filter(
                        lambda(x): x['time'] >= level_time * 10000 %
                                    self.patterns[-1]['time'],
                        self.patterns
                     )[0]
        #LOG().log((level_time, last,next))
        # get the proportion of travel between last and next we should have
        # done.
        percent_bettween = (
                            level_time*10000 % self.patterns[-1]['time']
                                                          - last['time']
                           ) / (next['time'] - last['time'])

        self.position[0] = int(last['position'][0] * (1 - percent_bettween)\
                               +next['position'][0] * (percent_bettween))
        self.position[1] = int(last['position'][1] * (1 - percent_bettween)\
                               +next['position'][1] * (percent_bettween))

        # maybe usefull to cache thoose result too.
        self.collide_rects = map(
                                    lambda(rect):
                                        pygame.Rect(
                                                    rect[0]+self.position[0],
                                                    rect[1]+self.position[1],
                                                    rect[2],
                                                    rect[3]
                                            ),
                                     self.rects
                                 )

class Level ( object ):
    """
    This object contain information about the world within the characters move,
    it contains the textures of background, stage and foreground, the coords of
    collision rects, the size of the leve;t.
    """
    def __init__(self, levelname='baselevel', server=False):
        """
        This constructor is currently using two initialisation method, the old,
        based on a map file, and the new based on an xml file.

        """
        #test if there is an xml file for this level (new format)
        self.moving_blocs = []
        self.vector_blocs = []
        self.map = []
        if os.access(
                os.path.join(
                    config['MEDIA_DIRECTORY'],
                    'levels',
                    levelname+os.extsep+'xml'
                    ),
                os.F_OK
                ):
            xml = ElementTree.ElementTree(
                    None,
                    os.path.join(
                        config['MEDIA_DIRECTORY'],
                        'levels',
                        levelname+os.extsep+'xml'
                        )
                    )

            attribs = xml.getroot().attrib

            self.name = attribs['name']

            self.background = os.path.join(
                        config['MEDIA_DIRECTORY'],
                        'levels',
                        attribs['background']
                        )

            self.level = os.path.join(
                        config['MEDIA_DIRECTORY'],
                        'levels',
                        attribs['middle']
                        )

            self.foreground = os.path.join(
                        config['MEDIA_DIRECTORY'],
                        'levels',
                        attribs['foreground']
                        )

            tmp = Image.open(self.level)
            self.rect = pygame.Rect(0,0, *tmp.size)

            if 'margins' in attribs:
                margins = [int(i) for i in attribs['margins'].split(',')]
                self.border = pygame.Rect(
                    self.rect[0] - margins[0],
                    self.rect[1] - margins[1],
                    self.rect[2] + margins[0] + margins[2],
                    self.rect[3] + margins[1] + margins[3]
                    )
            else:
                self.border = self.rect.inflate(self.rect[2]/2, self.rect[3]/2)


            self.entrypoints = []
            for point in xml.findall('entry-point'):
                x,y = point.attrib['coords'].split(' ')
                self.entrypoints.append([ int(x), int(y) ])

            #LOG().log(self.entrypoints)

            for block in xml.findall('block'):
                nums = block.attrib['coords'].split(' ')
                nums = [ int(i) for i in nums ]
                self.map.append(pygame.Rect(nums))

            for block in xml.findall('moving-block'):
                texture = block.attrib['texture']

                rects = []

                for rect in block.findall('rect'):
                    rects.append(
                            pygame.Rect(
                                [
                                int(i) for i in rect.attrib['coords'].split(' ')
                                ]
                                )
                            )

                patterns = []
                for pattern in block.findall('pattern'):
                    patterns.append(
                            {
                            'time': int(pattern.attrib['time']),
                            'position': [ int(i) for i in
                            pattern.attrib['position'].split(' ')]
                            }
                            )

                self.moving_blocs.append(
                        MovingPart(
                            rects,
                            texture,
                            patterns,
                            server
                            )
                        )

            for block in xml.findall('vector-block'):
                texture = block.attrib['texture']
                position = [int(i) for i in block.attrib['position'].split(' ')]
                vector = [int(i) for i in block.attrib['vector'].split(' ')]

                relative = int(block.attrib['relative']) and True or False

                rects = []
                for rect in block.findall('rect'):
                    rects.append(
                            pygame.Rect(
                                [
                                int(i)
                                for i in
                                rect.attrib['coords'].split(' ')
                                ]
                                )
                            )

                    self.vector_blocs.append(
                            VectorBloc(
                                rects,
                                position,
                                vector,
                                relative,
                                texture,
                                server
                                )
                            )

        else:
            # else we use old loading method.
            if not server:
                self.background = os.path.join(
                            config['MEDIA_DIRECTORY'],
                            'levels',
                            levelname+'-background'+os.extsep+'png'
                            )

                self.level = os.path.join(
                            config['MEDIA_DIRECTORY'],
                            'levels',
                            levelname+'-middle'+os.extsep+'png'
                            )

                self.border = self.rect.inflate(self.rect[2]/2, self.rect[3]/2)

                self.foreground = os.path.join(
                            config['MEDIA_DIRECTORY'],
                            'levels',
                            levelname+'-foreground'+os.extsep+'png'
                            )

            for line in open(
                os.path.join(
                    config['MEDIA_DIRECTORY'],
                    'levels',
                    levelname+os.extsep+'map'
                )
            ).readlines():
                nums = line.split(' ')
                for i in range(len(nums)): nums[i]=int(nums[i])
                self.map.append(pygame.Rect(nums))

        LOG().log(self.rect)
        self.entrypoints = [
            [self.rect[2]/2, 50],
            [self.rect[2]/4, 50],
            [3*self.rect[2]/4, 50]
        ]

    def __del__(self):
        LOG().log('deleting level')

    def serialize(self):
        return (
                (
                    self.background,
                    self.foreground,
                    self.middle
                ),
                [
                    serialize(block) for block in
                        self.moving_blocs+self.vector_blocs
                ]
            )

    def draw_background(self, surface, coords=(0,0)):
        surface.blit( loaders.image(self.background,
            scale=config['SIZE'])[0], coords )

    def draw_level(self, surface, coords=(0,0), zoom=1):
        surface.blit( loaders.image(self.level, zoom=zoom)[0], coords)

    def draw_foreground(self, surface, coords=(0,0), zoom=1):
        surface.blit( loaders.image(self.foreground, zoom=zoom)[0], coords)

    def update(self, time):
        for block in self.moving_blocs:
            block.update(time)

    def collide_rect(self, (x,y), (h,w)=(1,1)):
        """
        This fonction return True if the rect at coords (x,y) collide one of
        the rects of the level, including the moving blocks and vector blocks.

        """
        list = self.moving_blocs+self.vector_blocs
        return (
                pygame.Rect(x,y,h,w).collidelist(self.map) != -1
                or self.moving_blocs+self.vector_blocs != []
                    and True in map(lambda(a): a.collide_rect((x,y), (h,w)), list)
               )

    collide_point = collide_rect # alias from the deprecated name to the new one.

