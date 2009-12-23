###############################################################################
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
###############################################################################

import pygame
from pygame.sprite import Sprite

import loaders
from debug_utils import LOG

class Frame (object):
    """
    A Frame is an image of n animation, plus some information on the player
    when on this instant of the animation:

    * The hardshape is an inner rectangle than delimitate the area that can
          collide the world.

    * The agressiv points are the damaginds points of a player/entity when it
      hit some other player.

    * The Vector indicate the speed and direction taken by the entity when in
      this state, this combine with the current direction/speed of the entity.

    """
    def __init__(self, image, gametime, hardshape, name):
        """
        Load a frame from an image, the current gametime, the deplacement/s of
        the player in this frame, it's hardshape.

        """
        self.image = image
        self.time = int(gametime)
        if type(hardshape) is str:
            self.hardshape = pygame.Rect([int(i) for i in hardshape.split(' ')])
        else:
            self.hardshape = hardshape
        self.agressivpoints = []
        self.agressivpoints_reverse = []
        self.LOG = LOG()

    def addAgressivPoint(self, (x,y),(v,j)):
        self.agressivpoints.append(((x,y),(v,j)))
        self.agressivpoints_reverse.append(((self.hardshape[2] - x,y),(v,j)))

class EmptyAnimationException(Exception):
    pass

class PreciseTimedAnimation(Sprite):
    def __init__( self, timedFrames, attribs, server=False ):
        Sprite.__init__(self)
        self.frames = timedFrames
        self.server_mode = server
        try:
            self.image = timedFrames[0].image
        except IndexError:
            raise EmptyAnimationException
        self.rect = loaders.image(self.image, nodisplay=server)[1]
        self._start_time = 0
        self.playing = 0

        self.repeat = int ('repeat' in attribs and attribs ['repeat'])
        self.duration = int ('duration' in attribs and attribs ['duration'])
        self.hardshape = ('hardshape' in attribs) and\
                        pygame.Rect([int(i) for i in attribs['hardshape'].split(' ')])\
                        or 0
        self.update(0, server=server)

    def __del__(self):
        del(self)

    def start(self, gametime):
        self._start_time = gametime
        self.playing = 1

    def update(self, gametime, reversed=False, server=False):
       if self.playing:
           if self.duration != 0 and gametime - self._start_time > self.duration/1000.0:
               self.playing = 0
               if self.repeat is not 0:
                   #FIXME: repeat will not reset properly
                   self.repeat = max( -1, self.repeat - 1 )
                   self.start( gametime )
           else:
               try:
                   frame = [
                   i for i in self.frames
                   if i.time/1000.0 < gametime - self._start_time
                   ][-1]
               except:
                   frame = self.frames[0]
               self.image = frame.image
               if reversed:
                   self.agressivpoints = frame.agressivpoints_reverse
               else:
                   self.agressivpoints = frame.agressivpoints
               self.hardshape = frame.hardshape
       self.rect = loaders.image(self.image, nodisplay=server)[1]

