################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
#                                                                              #
# This file is part of UltimateSmashFriends                                    #
#                                                                              #
# UltimateSmashFriends is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation, either version 3 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# UltimateSmashFriends is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.#
################################################################################

import os
import sys
import pygame
import logging

import loaders
import time
from config import Config
from usf import skin
config = Config()

from memoize import memoize
from debug_utils import draw_rect

# different in python 2.4 and 2.5
try:
    from xml.etree import ElementTree
except:
    logging.warning(
            "your python version seems quite old, you should consider"
            " upgrading")

    from elementtree import ElementTree


class Decorum(object):
    """
    A simple class to represent decorum in levels.
    A decorum is an element displayed, but non interractive, as opposed to a
    block, it can be at any depth between background and camera, and will be
    diplayed with the appropriate zoom at the appromirate moment. It can be
    animated, by containing several frames, and move, by providing dx and dy
    update functions. which can use time and random.

    frames are (image, time) couples, time being the END of the display of the
    corresponding image (and thus, begin display of the next), image is the
    path to the image, relative to the data directory.

    depth is [-1, 1[, 0 meaning the place of the level, a negative value mean
    behind the level and a positive, before.
    """

    def __init__(self, frames, coords, depth, update_fctn):
        self.frames = frames
        self.coords = coords
        self.depth = depth
        self.update_fctn = update_fctn
        self.duration = max(map(lambda x: x[1], frames))
        self.update(1)

    def update(self, time):
        self.texture = filter(
                lambda x: x[1] > time % self.duration, self.frames)[0][0]

        self.coords = self.update_fctn(self.coords, time)

    def draw(self, surface, coords, zoom):
        middle = surface.get_size()[0] / 2, surface.get_size()[1] / 2
        real_coords = (int(self.coords[0] * zoom) + coords[0],
                int(self.coords[1] * zoom) + coords[1])

        surface.blit(
                loaders.image('data/'+self.texture, zoom=zoom)[0],
                real_coords)

    def __cmp__(self, other):
        return cmp(self.depth, other.depth)


class Block (object):
    """
    An abstraction class to define methods shared by some level objects.
    """

    def __init__(self):
        """
        Not much to do here.
        """
        pass

    def draw(self, surface, coords=(0, 0), zoom=1):
        """
        Draw this moving bloc on the passed surface, taking account of zoom and
        placement of camera.

        """
        real_coords = (int(self.position[0] * zoom) + coords[0],
                int(self.position[1] * zoom) + coords[1])

        surface.blit(loaders.image(self.texture, zoom=zoom)[0], real_coords)

    def collide_rect(self, rect):
        """
        Return True if the point at (x, y) collide this bloc's rects.

        """
        return rect.collidelist(self.collide_rects) != -1


class VectorBloc (Block):
    """
    This define a bloc that apply a vector to any entity falling/walking on it.
    """

    def __init__(self, rects, position, vector, relative, texture,
            server=False, levelname='biglevel'):
        Block.__init__(self)
        self.rects = rects
        self.relative = relative
        try:
            self.texture = os.path.join(
                    config.sys_data_dir,
                    "levels",
                    levelname,
                    texture)
            loaders.image(self.texture)
        except pygame.error:
            logging.debug("No texture found here: " + str(file))
            try:
                self.texture = os.path.join(
                        config.sys_data_dir,
                        "levels",
                        "common",
                        texture)

            except pygame.error:
                logging.error("Can't load the texture: " + str(file))

        self.vector = vector
        self.position = position
        self.collide_rects = []
        for i in self.rects:
            self.collide_rects.append(
                    pygame.Rect(
                        i[0]+position[0],
                        i[1]+position[1],
                        i[2], i[3]))

    def apply_vector(self, entity):
        """
        This method simply add the bloc's vector to the passed player.
        """

        entity.vector = [entity.vector[0] + self.vector[0],
                entity.vector[1] + self.vector[1]]

    @memoize
    def collide_rect(self, rect):
        return Block.collide_rect(self, rect)


class MovingPart (Block):
    """
    This define a level bloc that move, with a defined texture, and a defined
    set of collision rects. It moves following a pattern of (position(x, y):
    time( % maxtime)).
    """

    def __init__(self, rects, texture, patterns, server=False,
            levelname="biglevel"):
        Block.__init__(self)
        #logging.debug('moving block created')
        self.rects = rects
        try:
            self.texture = os.path.join(
                    config.sys_data_dir,
                    "levels",
                    levelname,
                    texture)
            loaders.image(self.texture)
        except pygame.error:
            logging.debug("No texture found here: " + str(file))
            try:
                self.texture = os.path.join(
                        config.sys_data_dir,
                        "levels",
                        "common",
                        texture)

            except pygame.error:
                logging.error("Can't load the texture: " + str(file))
        self.patterns = patterns
        self.position = self.patterns[0]['position']

    def get_movement(self):
        """
        Return the movement between the position at the precedent frame, and
        now, usefull to communicate this movement to another entity.

        """
        return (self.position[0] - self.old_position[0],
                self.position[1] - self.old_position[1])

    def update(self, level_time):
        """
        Update the position of the moving bloc, based on time since the
        bigining of the game, calculating the percentage of time we are
        between two positions. And update the coords of colliding rects.

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
                    self.patterns))[-1]

        # get the next position of pattern we will get by.
        # FIXME: maybe avoid filtering all, maybe using an itertool?
        next = filter(
                lambda(x): x['time'] >= level_time * 10000 %
                self.patterns[-1]['time'],
                self.patterns)[0]

        # get the proportion of travel between last and next we should have
        # done.
        percent_bettween = (
                level_time*10000 % self.patterns[-1]['time'] - last['time']) /(
                        next['time'] - last['time'])

        self.position[0] = (
            int(last['position'][0] * (1 - percent_bettween) +
            next['position'][0] * (percent_bettween)))

        self.position[1] = (
            int(last['position'][1] * (1 - percent_bettween)
            +next['position'][1] * (percent_bettween)))

        # maybe usefull to cache thoose result too.
        self.collide_rects = map(
            lambda(rect):
                pygame.Rect(
                    rect[0]+self.position[0],
                    rect[1]+self.position[1],
                    rect[2], rect[3]),
             self.rects)

    def backup(self):
        return (self.old_position, self.position)

    def restore(self, backup):
        self.old_position, self.position = backup


class Level(object):
    """
    This object contain information about the world within the characters move,
    it contains the textures of background, stage and foreground, the coords of
    collision rects, the size of the leve;t.
    """

    def __init__(self, levelname='baselevel', server=False, clone=None):
        """
        This constructor is currently using two initialisation method, the old,
        based on a map file, and the new based on an xml file.
        """
        self.SIZE = (config.general['WIDTH'],
            config.general['HEIGHT'])

        xml = self.getXML(levelname)
        attribs = xml.getroot().attrib
        self.name = attribs['name']

        self.load_images(attribs, levelname)
        self.load_borders(attribs)
        self.load_entrypoints(xml)
        self.load_layers(xml)
        self.load_blocs(xml)
        self.load_moving_blocs(xml, server, levelname)
        self.load_water_blocs(xml, server)
        self.load_vector_blocs(xml, server, levelname)
        self.load_decorums(xml)

    def getXML(self, levelname):
        return ElementTree.ElementTree(
                None,
                os.path.join(
                    config.sys_data_dir,
                    'levels',
                    levelname,
                    'level.xml'))

    def __del__(self):
        logging.debug('deleting level')

    def load_images(self, attribs, levelname):
        self.background = os.path.join(
                    config.sys_data_dir,
                    'levels',
                    levelname,
                    attribs['background'])

        self.level = os.path.join(
                    config.sys_data_dir,
                    'levels',
                    levelname,
                    attribs['middle'])

        if 'foreground' in attribs:
            self.foreground = os.path.join(
                        config.sys_data_dir,
                        'levels',
                        levelname,
                        attribs['foreground'])
        else:
            self.foreground = False

    def load_borders(self, attribs):
        #FIXME: should not depend on the initialisation of pygame
        self.rect = loaders.image(self.level)[1]

        if 'margins' in attribs:
            margins = [int(i) for i in attribs['margins'].split(',')]
            self.border = pygame.Rect(
                self.rect[0] - margins[0],
                self.rect[1] - margins[1],
                self.rect[2] + margins[0] + margins[2],
                self.rect[3] + margins[1] + margins[3])
        else:
            self.border = self.rect.inflate(self.rect[2]/2, self.rect[3]/2)

    def load_entrypoints(self, xml):
        self.entrypoints = []
        for point in xml.findall('entry-point'):
            x, y = point.attrib['coords'].split(' ')
            self.entrypoints.append([int(x), int(y)])

        if not self.entrypoints:
            logging.info('no entry point defined for this level')
            for x in xrange(4):
                self.entrypoints.append(
                        [int(x*self.rect[2]/5), self.rect[3]/5])

    def load_layers(self, xml):
        self.layers = []
        for layer in xml.findall('layer'):
            self.layers.append(skin.Layer(layer))

    def load_blocs(self, xml):
        self.map = []
        for block in xml.findall('block'):
            nums = block.attrib['coords'].split(' ')
            nums = [int(i) for i in nums]
            self.map.append(pygame.Rect(nums))

    def load_moving_blocs(self, xml, server, levelname):
        self.moving_blocs = []
        for block in xml.findall('moving-block'):
            texture = block.attrib['texture']
            rects = []

            for rect in block.findall('rect'):
                rects.append(
                        pygame.Rect([
                            int(i) for i in rect.attrib['coords'].split(' ')]))

            patterns = []
            for pattern in block.findall('pattern'):
                patterns.append({
                    'time': int(pattern.attrib['time']),
                    'position': [int(i) for i in
                        pattern.attrib['position'].split(' ')]})

            self.moving_blocs.append(
                    MovingPart(
                        rects,
                        texture,
                        patterns,
                        server,
                        levelname))

    def load_water_blocs(self, xml, server=False):
        self.water_blocs = []
        for block in xml.findall('water'):
            nums = block.attrib['coords'].split(' ')
            nums = [int(i) for i in nums]
            self.water_blocs.append(pygame.Rect(nums))

    def load_vector_blocs(self, xml, server, levelname):
        self.vector_blocs = []
        for block in xml.findall('vector-block'):
            texture = block.attrib['texture']
            position = [int(i) for i in block.attrib['position'].split(' ')]
            vector = [int(i) for i in block.attrib['vector'].split(' ')]

            relative = int(block.attrib['relative']) and True or False

            rects = []
            for rect in block.findall('rect'):
                rects.append(
                        pygame.Rect(
                            [int(i) for i in rect.attrib['coords'].split(' ')]))

                self.vector_blocs.append(
                        VectorBloc(
                            rects,
                            position,
                            vector,
                            relative,
                            texture,
                            server,
                            levelname))

    def load_decorums(self, xml):
        self.decorums = list()
        for d in xml.findall('decorum'):
            frames = list()
            for f in d.findall('frame'):
                frames.append((f.attrib['image'], float(f.attrib['time'])))

            coords = [int(x) for x in d.attrib['coords'].split(',')]
            depth = float(d.attrib['depth'])
            update_fctn = eval(d.attrib['update'])

            self.decorums.append(Decorum(frames, coords, depth, update_fctn))
        self.decorums.sort()

    def draw_before_players(self, surface, level_place, zoom, shapes=False):
        self.draw_background(surface, level_place, zoom)
        self.draw_level(surface, level_place, zoom, shapes)

        for block in self.moving_blocs:
            block.draw(surface, level_place, zoom)

        for block in self.vector_blocs:
            block.draw(surface, level_place, zoom)

    def draw_after_players(self, surface, level_place, zoom, levelmap=False):
        self.draw_foreground(surface, level_place, zoom)
        if levelmap or loaders.get_gconfig().get("game", "minimap") == "y":
            self.draw_minimap(surface)

    def draw_minimap(self, surface):
        for rect in self.map:
            draw_rect(
                    surface,
                    pygame.Rect(
                        rect[0] / 8,
                        rect[1] / 8,
                        rect[2] / 8,
                        rect[3] / 8),
                    pygame.Color('grey'))

    def draw_debug_map(self, surface, level_place, zoom):
        draw_rect(
                surface,
                pygame.Rect(
                level_place[0] + self.border[0] * zoom,
                level_place[1] + self.border[1] * zoom,
                self.border[2] * zoom,
                self.border[3] * zoom),
                pygame.Color('white'))

        draw_rect(
                surface,
                pygame.Rect(
                level_place[0],
                level_place[1],
                self.rect[2] * zoom,
                self.rect[3] * zoom),
                pygame.Color('lightblue'))

        for rect in self.map:
            draw_rect(
                    surface,
                    pygame.Rect(
                        int(level_place[0] + (rect[0]) * zoom),
                        int(level_place[1] + (rect[1]) * zoom),
                        int(rect[2] * zoom),
                        int(rect[3] * zoom)),
                    pygame.Color('green'))

        for rect in self.entrypoints:
            draw_rect(
                    surface,
                    pygame.Rect(
                        int(level_place[0] + (rect[0]) * zoom),
                        int(level_place[1] + (rect[1]) * zoom),
                        20, 20),
                    pygame.Color('blue'))

    def draw_background(self, surface, coords=(0, 0), zoom=1):
        surface.blit(loaders.image(
            self.background, scale=self.SIZE)[0], (0, 0))

        for layer in self.layers:
            surface.blit(layer.get_image(), layer.get_pos())

        for d in self.decorums:
            if d.depth < 0:
                d.draw(surface, coords, zoom)

    def draw_level(self, surface, coords, zoom, shapes=False):
        surface.blit(loaders.image(self.level, zoom=zoom)[0], coords)
        if shapes:
            self.draw_debug_map(surface, coords, zoom)

    def draw_foreground(self, surface, coords, zoom):
        if self.foreground:
            surface.blit(loaders.image(self.foreground, zoom=zoom)[0], coords)

        for d in self.decorums:
            if d.depth >= 0:
                d.draw(surface, coords, zoom)

    def backup(self):
        return (b.backup() for b in self.moving_blocs)

    def restore(self, backup):
        (bloc.restore(back) for bloc, back in zip(self.moving_blocs, backup))

    def update(self, time):
        for block in self.moving_blocs:
            block.update(time)

        for d in self.decorums:
            d.update(time)

    def collide_r(self, r):
        if r.collidelist(self.map) != -1:
            return True

        else:
            for i in self.vector_blocs + self.moving_blocs:
                if r.collidelist(i.collide_rects) != -1:
                    return True
            return False

    def collide_rect(self, (x, y), (h, w)=(1, 1)):
        """
        This fonction returns True if the rect at coords (x, y) collides one of
        the rects of the level, including the moving blocks and vector blocks.

        """
        r = pygame.Rect((x, y), (h, w))

        if r.collidelist(self.map) != -1:
            return True

        else:
            for i in self.vector_blocs + self.moving_blocs:
                if r.collidelist(i.collide_rects) != -1:
                    return True
            return False

