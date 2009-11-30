#!/usr/bin/env python
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

# standards imports
import os, sys
import pygame

# my imports
import loaders
import music
import animations
from pygame.locals import BLEND_MAX
import config
from debug_utils import LOG

def memoize(function):
    cache = {}
    def decorated_function(*args, **kwargs):
        params = (args)+tuple(zip(kwargs.keys(),kwargs.values()))
        try:
            return cache[params]
        except:
            val = function(*args, **kwargs)
            cache[params] = val
            return val
    return decorated_function

@memoize
def image(name, *args, **kwargs):
    """
    A function to load an image, shamelessly picked from pygame
    tutorial, and grossly adjusted for native transparency support of png.
    Can scale and reverse horizontaly an image, can produce a lightened version
    of an image.

    keywords arguments accepted are the followings:
        zoom=None, colorkey=None, server=False, lighten=False, reversed=False,
    """
    # FIXME: should not have to load the image in server mode, we just want
    # it's size!
    if 'reversed' in kwargs and kwargs['reversed'] == True:
        kwargs['reversed'] = False
        #LOG().log("reverse "+name)
        image = pygame.transform.flip(
            loaders.image(name,*args, **kwargs)[0],
            True, #flip horizontaly
            False #not verticaly
            )

    elif 'lighten' in kwargs and kwargs['lighten'] == True:
        #LOG().log('lightened: '+name)
        kwargs['lighten'] = False
        image = loaders.image(name, *args, **kwargs)[0].copy()
        image.fill(
                pygame.Color('lightgrey'),
                None,
                BLEND_MAX
                )

    elif 'zoom' in kwargs and kwargs['zoom'] not in (None, 1):
        zoom = kwargs['zoom']
        kwargs['zoom'] = None
        #LOG().log('scaling image '+name+' :'+str(zoom))
        image = pygame.transform.scale(
                loaders.image(name, **kwargs)[0],
                (
                 int(loaders.image(name, *args, **kwargs)[1][2]*zoom*
                     config.config['SIZE'][0]/800),
                 int(loaders.image(name, *args, **kwargs)[1][3]*zoom*
                     config.config['SIZE'][1]/480)
                )
                )
    else:
        try:
            image = pygame.image.load(name)
        except pygame.error, message:
            LOG().log('Cannot load image:'+str(name), 2)
            raise# SystemExit, message
        if 'colorkey' not in kwargs or kwargs['colorkey'] is None:
            image = image.convert_alpha()
        if 'colorkey' in kwargs and kwargs['colorkey'] is not None:
            image = image.convert()
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

@memoize
def track(name):
    return pygame.mixer.Sound(name)
