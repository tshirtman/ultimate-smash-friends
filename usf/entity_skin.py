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

import pygame
import logging

from animations import Frame, PreciseTimedAnimation
import loaders
import game
import timed_event

from config import Config

config = Config()
SIZE = (config.general['WIDTH'],
        config.general['HEIGHT'])

# different in python 2.4 and 2.5
# more pythonic
try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

import os
import sys
import random


class Entity_skin (object):
    """
    An Entity_skin contains all information about a player or an item, which is
    mainly animations frames, with their timings and vectors, and less
    importants information as the character/item name and such details.
    """

    def __init__(self, dir_name, server=False, xml_from_str=None,
            keep_xml=False, animation='static'):
        """
        The dir_name is the relative path of the directory where the item/player
        is defined, the class search for an xml file of the same name as the
        directory there.

        """
        self.animations = {}
        if xml_from_str is not None:
            a = ElementTree.ElementTree()
            # FIXME this is DIRTY
            f = open('/tmp/erf', 'w')
            f.write(xml_from_str)
            f.close()
            a.parse('/tmp/erf')

        else:
            file = os.path.join(
                        config.sys_data_dir,
                        dir_name,
                        dir_name.split(os.sep)[-1]
                        +os.extsep+'xml')
            #logging.debug(file)
            a = ElementTree.ElementTree(
                    None,
                    file)
        if keep_xml:
            # keep this to use it for editors
            self.xml = a

        attribs = a.getroot().attrib

        self.filename = dir_name
        self.name = attribs['name']

        self.image = os.path.join(
                    config.sys_data_dir,
                    dir_name,
                    attribs['image'])

        self.weight = attribs['weight']
        if 'armor' in attribs:
            self.armor = int(attribs['armor'])
        else:
            self.armor = 0

        self.action_events = {}
        self.sounds = {}
        self.vectors = {}

        self.hardshape = self.load_hardshape(attribs)
        self.shield_center = self.load_shield_center(attribs)
        self.load_movements(a, dir_name, server)

        # FIXME: this is about the state of the player, should be in the entity
        # class
        self.current_animation = animation
        self.animation = self.animations[self.current_animation]
        self.animation_change = True

    def load_hardshape(self, attribs):
        return pygame.Rect([int(i) for i in attribs['hardshape'].split(' ')])

    def load_shield_center(self, attribs):
        if 'shield_center' in attribs:
            return [int(i) for i in attribs['shield_center'].split(' ')]
        else:
            logging.warning(
                'warning, entity '+self.name+' has no attribute shield_center'+
                ', guessing from hardshape')

            return (
                self.hardshape[0] + .5 * self.hardshape[2],
                self.hardshape[1] + .5 * self.hardshape[3])

    def load_movements(self, a, dir_name, server):
        for movement in a.findall('movement'):
            frames = []
            events = []
            sounds = []
            vectors = []

            for event in movement.findall('vector'):
                #logging.debug('vector found')
                x, y = [int(n) for n in event.attrib['vector'].split(',')]
                vectors.append(
                        (
                        (x, y),
                         int(event.attrib['time'])))

            self.vectors[movement.attrib['name']] = vectors

            for event in movement.findall('event'):
                events.append(
                        (
                            event.attrib['action'],
                            [int(i) for i in
                                event.attrib['period'].split(',')]))

            self.action_events[movement.attrib['name']] = events

            for sound in movement.findall('sound'):
                sounds.append(
                        os.path.join(
                            config.sys_data_dir,
                            dir_name,
                            sound.attrib['filename']))

            self.sounds[movement.attrib['name']] = sounds

            for frame in movement.findall('frame'):
                image = os.path.join(
                            config.sys_data_dir,
                            dir_name,
                            frame.attrib['image'])

                frames.append(
                        Frame(
                            image,
                            frame.attrib['time'],
                            ('hardshape' in frame.attrib
                             and frame.attrib['hardshape']
                             or self.hardshape),
                            name=frame.attrib['image']))

                for agressiv in frame.findall('agressiv-point'):
                    coords = agressiv.attrib['coords'].split(',')
                    vector = agressiv.attrib['vector'].split(',')
                    frames[-1].addAgressivPoint([int(i) for i in coords],
                                                [int(i) for i in vector])

            self.animations[movement.attrib['name']] = PreciseTimedAnimation(
                    frames,
                    movement.attrib,
                    server)

    def valid_animation(self, anim_name):
        return (
                anim_name in self.animations
                and (
                    anim_name == 'static' or
                    anim_name != self.current_animation))

    #FIXME: this should be in the entity class
    def change_animation(self, anim_name, game=None, params={}):
        """
        Change animation of the entity skin, updating hardshape and agressiv
        points. Add associated events to game.

        """
        if self.valid_animation(anim_name):
            if 'entity' in params and params['entity'].upgraded:
                if anim_name + '_upgraded' in self.animations:
                    self.current_animation = anim_name + '_upgraded'
                else:
                    logging.debug(
                            ' '.join((self.name,
                                'character has no upgraded version of ',
                                anim_name, 'falling back to normal version')))

                    self.current_animation = anim_name
            else:
                self.current_animation = anim_name

            self.animation_change = True
            params['world'] = game
            params['gametime'] = game is not None or 0
            self.add_events(anim_name, game, params)

            #logging.debug(self.vectors[anim_name])
            self.add_vectors(anim_name, game, params)

            if self.sounds[anim_name] != []:
                try:
                    loaders.track(random.choice(self.sounds[anim_name])).play()
                except e:
                    logging.warning(e)
        else:
            #logging.debug( "entity_skin "+self.name+" has no "+anim_name+"\
#animation.")
            pass

    def backup(self):
        return (self.current_animation, self.animation,
                self.animation.playing, self.animation._start_time)

    def restore(self, backup):
        (self.current_animation, self.animation, self.animation.playing,
                self.animation._start_time) = backup

    def add_vectors(self, anim_name, game, params):
        for vector in self.vectors[anim_name]:
            #logging.debug('vector added')
            params2 = params.copy() # because we want to change some of
                                    # them for this time.
            params2['vector'] = vector[0]
            params2['anim_name'] = anim_name
            game.events.add_event(
                    'VectorEvent',
                    period=(None, game.gametime+vector[1]/1000.0),
                    params=params2)

    def add_events(self, anim_name, game, params):
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
                game.events.add_event(
                        event[0],
                         period=(p1, p2),
                         params=params)

            except AttributeError:
                logging.debug((self.name, game), 3)
                raise

    def update(self, t, reversed=False, upgraded=False, server=False):
        """
        Update the skin's animation if necessary.

        """
        if self.animation_change:
            self.animation = self.animations[self.current_animation]
            self.animation_change = False
            self.animation.start(t)

        if self.animation.playing == 0:
            a = 'static' + upgraded * '_upgraded'
            if 'upgraded' in a and a not in self.animations:
                a = 'static'
            self.current_animation = a
            self.animation = self.animations[self.current_animation]
            self.animation.start(t)

        self.animation.update(t, reversed, server)
        self.hardshape = self.animation.hardshape

