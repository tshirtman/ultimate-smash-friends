################################################################################
# copyright 2008-2011 Gabriel Pettier <gabriel.pettier@gmail.com>              #
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

'''
This module provide animations for entities, animations are composed of frames,
which are a bit more than an image...

'''

import pygame
import logging

from usf import loaders


class Frame (object):
    """
    A Frame is an image of n animations, plus some information on the player
    when on this instant of the animation:

    * The hardshape is an inner rectangle than delimitate the area that can
          collide the world.

    * The agressiv points are the damaginds points of a player/entity when it
      hit some other player.

    * The Vector indicate the speed and direction taken by the entity when in
      this state, this combine with the current direction/speed of the entity.
    """

    def __init__(self, image, gametime, hardshape, trails=None):
        """
        Load a frame from an image, the current gametime, the deplacement/s of
        the player in this frame, it's hardshape.

        """
        self.image = image
        self.trails = trails
        self.time = int(gametime)
        if type(hardshape) is str:
            self.hardshape = pygame.Rect([int(i) for i in hardshape.split(' ')])
        elif type(hardshape) is pygame.Rect:
            self.hardshape = hardshape
        else:
            logging.error('incorrect type for hardshape: ', hardshape)

        self.hardshape_reverse = (
            loaders.image(self.image)[1][2]
                - self.hardshape[0] - self.hardshape[2],
            self.hardshape[1],
            self.hardshape[2],
            self.hardshape[3])

        self.agressivpoints = []
        self.agressivpoints_reverse = []


    def add_agressiv_point(self, (c_x, c_y), (vect_x, vect_y)):
        """
        add an agressive points of coords, and vector specified, to the list of
        agressivpoints of the frame
        """
        self.agressivpoints.append(((c_x, c_y), (vect_x, vect_y)))
        self.agressivpoints_reverse.append(
                ((self.hardshape[2] - c_x, c_y), (vect_x, vect_y)))


class PreciseTimedAnimation(object):
    """
    This object store the frames of an animation and update the image of the
    entity skin.
    """

    def __init__(self, frames, attribs, server=False):
        self.frames = frames
        self.image = frames[0].image
        self.rect = loaders.image(self.image, nodisplay=server)[1]
        self._start_time = 0
        self.playing = 0

        self.repeat = int('repeat' in attribs and attribs['repeat'])
        self.duration = int('duration' in attribs and attribs['duration'])
        self.hardshape = (
                ('hardshape' in attribs) and
                    pygame.Rect(
                        [int(i) for i in attribs['hardshape'].split(' ')]) or 0)

        self.update(0, server=server)
        self.agressivpoints = []

    @property
    def start_time(self):
        return self._start_time

    def start(self, gametime):
        """
        set the animation start as now, and the animation as started.
        """
        self._start_time = gametime
        self.playing = 1

    def frame(self, anim_time):
        """
        return the current frame depending on the time since the beggining of
        the animation.
        """
        try:
            return filter(lambda x: x.time/1000.0 <= anim_time, self.frames)[-1]

        except IndexError:
            return self.frames[0]

    def update(self, gametime, reverse=False, server=False):
        """
        update the state of the animation.
        """
        if self.playing:
            if (self.duration != 0
                    and gametime - self._start_time > self.duration/1000.0):
                self.playing = 0
                if self.repeat is not 0:
                    #FIXME: repeat will not reset properly
                    self.repeat = max(-1, self.repeat - 1)
                    self.start(gametime)
            else:
                frame = self.frame(gametime - self._start_time)
                self.image = frame.image
                self.trails = frame.trails

                if reverse:
                    self.agressivpoints = frame.agressivpoints_reverse
                    self.hardshape = frame.hardshape_reverse

                else:
                    self.agressivpoints = frame.agressivpoints
                    self.hardshape = frame.hardshape

            self.rect = loaders.image(self.image, nodisplay=server)[1]

