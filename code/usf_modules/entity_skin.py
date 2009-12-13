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

import sys
import pygame

from animations import Frame, PreciseTimedAnimation
import loaders
import game
import timed_event
from debug_utils import LOG
from config import config

# different in python 2.4 and 2.5
if sys.version_info[0] == 2 and sys.version_info[1] >= 5:
    from xml.etree import ElementTree
else:
    from elementtree import ElementTree

import os, sys
import random

class Entity_skin (object):
    """
    An Entity_skin contains all information about a player or an item, which is
    mainly animations frames, with their timings and vectors, and less 
    importants information as the character/item name and such details.

    """
    def __init__( self, dir_name="characters"+os.sep+"stick",
    server=False, xml_from_str=None):
        """
        The dir_name is the relative path of the directory where the item/player
        is defined, the class search for an xml file of the same name as the
        directory there.

        """
        #LOG().log(dir_name)
        self.animations = {}
        if xml_from_str is not None:
            a = ElementTree.ElementTree()
            # FIXME this is DIRTY
            f = open('/tmp/erf','w')
            f.write(xml_from_str)
            f.close()
            a.parse('/tmp/erf')

        else:
            file = os.path.join(
                        config['MEDIA_DIRECTORY'],
                        dir_name,
                        dir_name.split(os.sep)[-1]
                        +os.extsep+'xml'
                        )
            #LOG().log(file)
            a = ElementTree.ElementTree(
                    None,
                    file
                    )

        attribs = a.getroot().attrib

        self.filename = dir_name
        self.name = attribs['name']

        if not server:
            self.image = loaders.image(
                    os.path.join(
                        config['MEDIA_DIRECTORY'],
                        dir_name,
                        attribs['image']
                        )
                    )[0]

        self.weigh = attribs['weight']
        if 'armor' in attribs:
            self.armor = int(attribs['armor'])
        else:
            self.armor = 0
        self.action_events = {}
        self.sounds = {}
        self.vectors = {}

        self.hardshape = pygame.Rect(
                [
                int(i) for i
                in attribs['hardshape'].split(' ')
                ]
                )

        for movement in a.findall('movement'):
            frames = []
            events = []
            sounds = []
            vectors = []

            for event in movement.findall('vector'):
                #LOG().log('vector found')
                x,y = [int(n) for n in event.attrib['vector'].split(',')]
                vectors.append(
                        (
                        (x,y),
                         int(event.attrib['time'])
                        )
                        )

            self.vectors[movement.attrib['name']] = vectors

            for event in movement.findall('event'):
                events.append(
                        (
                         event.attrib['action'],
                         [
                         int(i)\
                         for i in event.attrib['period'].split(',')
                         ]
                        )
                        )

            self.action_events[movement.attrib['name']] = events

            for sound in movement.findall('sound'):
                sounds.append(
                        pygame.mixer.Sound(
                            os.path.join(
                                config['MEDIA_DIRECTORY'],
                                dir_name,
                                sound.attrib['filename']
                                )
                            )
                        )

            self.sounds[movement.attrib['name']] = sounds

            for frame in movement.findall('frame'):
                image = os.path.join(
                            config['MEDIA_DIRECTORY'],
                            dir_name,
                            frame.attrib['image']
                            )

                frames.append(
                        Frame(
                            image,
                            frame.attrib['time'],
                            ('hardshape' in frame.attrib
                             and frame.attrib ['hardshape']
                             or loaders.image(image)[1]),
                            name=frame.attrib['image']
                            )
                        )

                for agressiv in frame.findall( 'agressiv-point' ):
                    coords = agressiv.attrib[ 'coords' ].split( ',' )
                    vector = agressiv.attrib[ 'vector' ].split( ',' )
                    frames[-1].addAgressivPoint([int(i) for i in coords],
                                                [int(i) for i in vector])

            self.animations[movement.attrib['name']] = PreciseTimedAnimation(
                    frames,
                    movement.attrib,
                    server
                    )

        self.current_animation = "static"
        self.animation = self.animations[self.current_animation]
        self.animation_change = 1

    def __del__(self):
        del(self.__dict__)
        del(self)

    def change_animation( self, anim_name, game, params={}):
        """
        Change animation of the entity skin, updating hardshape and agressiv
        points. Add associated events to game.

        """
        #LOG().log(params,1)
        if (anim_name in self.animations
                and ( anim_name == "static"
                    or anim_name != self.current_animation )):
            if 'entity' in params and params['entity'].upgraded:
                if anim_name+'_upgraded' in self.animations:
                    self.current_animation = anim_name+'_upgraded'
                else:
                    LOG().log(self.name+' character has no upgraded \
version of '+anim_name+' falling back to normal version')
                    self.current_animation = anim_name
            else:
                self.current_animation = anim_name

            self.animation_change = 1
            params['world'] = game
            params['gametime'] = game.gametime
            for event in self.action_events[anim_name]:
                if event[1][0] is 0:
                    p1 = None
                else:
                    p1 = game.gametime+(event[1][0]/1000.0)

                if event[1][1] is 0:
                    p2 = None
                else:
                    p2 = game.gametime+(event[1][1]/1000.0)

                try:
                    game.events.append(
                            timed_event.event_names[event[0]]
                            (
                             period=(p1, p2),
                             params=params
                            )
                            )

                except AttributeError:
                    LOG().log((self.name, game), 3)
                    raise

            #LOG().log(self.vectors[anim_name])
            for vector in self.vectors[anim_name]:
                #LOG().log('vector added')
                params2 = params.copy() # because we want to change some of
                                        # them for this time.
                params2['vector'] = vector[0]
                params2['anim_name'] = anim_name
                game.events.append(
                        timed_event.VectorEvent(
                             period=(None, game.gametime+vector[1]/1000.0),
                             params=params2
                            )
                        )

            if self.sounds[anim_name] != []:
                random.choice(self.sounds[anim_name]).play()
        else:
            #LOG().log( "entity_skin "+self.name+" has no "+anim_name+"\
#animation.")
            pass

    def update(self, t, reversed=False):
        """
        Update the skin's animation if necessary.

        """
        if self.animation.playing == 0:
            self.current_animation = "static"
            self.animation_change = True
        if self.animation_change:
            self.animation = self.animations[self.current_animation]
            self.animation_change = False
            self.animation.start(t)
        self.animation.update(t, reversed)

