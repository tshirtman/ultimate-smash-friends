#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import os, sys, copy
import pygame
import logging

# my imports
import loaders
import music
import animations

try:
    from pygame.locals import BLEND_MAX
except:
    Log().log("old version of pygame no BLEND_MAX")
    BLEND_MAX = None


from config import Config

config = Config()
SIZE = (config.general['WIDTH'],
        config.general['HEIGHT'])

from debug_utils import draw_rect

def memoize(function):
    """
    Any function decorated with memoize will cache it's results and send them
    directly when called with same parameters as before, without calling the
    actual code, please only use with functions which result depend only of
    parameters (not time, state of the game or such).
    """
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

@memoize #the memoize is critical for performances!
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
    if 'nodisplay' in kwargs and kwargs['nodisplay']:
        return None, pygame.Rect((0, 0), pygame.image.load(name).get_size())

    if 'reversed' in kwargs and kwargs['reversed']:
        kwargs['reversed'] = False
        #logging.debug("reverse "+name)
        image = pygame.transform.flip(
            loaders.image(name,*args, **kwargs)[0],
            True, #flip horizontaly
            False #not verticaly
            )

    elif 'lighten' in kwargs and kwargs['lighten']:
        #logging.debug('lightened: '+name)
        kwargs['lighten'] = False
        image = loaders.image(name, *args, **kwargs)[0].copy()
        if BLEND_MAX is not None:
            image.fill(
                    pygame.Color('lightgrey'),
                    None,
                    BLEND_MAX
                    )
        else:
           # this mean this version of pygame is to old to use the effect
           # above, an equivalent method would be a good thing
           pass #nothing for the moment 

    elif 'scale' in kwargs and kwargs['scale'] is not None:
        if len(kwargs['scale']) is not 2:
            raise Exception.ValueError(
                "scale parameter should be a tuple of two integers"
                )
        scale = kwargs['scale']
        kwargs['scale'] = None
        if config.general['SMOOTHSCALE']:
            image = pygame.transform.smoothscale(
                loaders.image(name, *args, **kwargs)[0],
                scale
                )
        else:
            image = pygame.transform.scale(
                loaders.image(name, *args, **kwargs)[0],
                scale
                )


    elif 'zoom' in kwargs and kwargs['zoom'] not in (None, 1):
        zoom = kwargs['zoom']
        kwargs['zoom'] = None
        #logging.debug('scaling image '+name+' :'+str(zoom))
        if config.general['SMOOTHSCALE']:
            image = pygame.transform.smoothscale(
                    loaders.image(name, **kwargs)[0],
                    (
                     int(loaders.image(name, *args, **kwargs)[1][2]*zoom*
                         SIZE[0]/800.0),
                     int(loaders.image(name, *args, **kwargs)[1][3]*zoom*
                         SIZE[1]/480.0)
                    )
                    )
        else:
            image = pygame.transform.scale(
                    loaders.image(name, **kwargs)[0],
                    (
                     int(loaders.image(name, *args, **kwargs)[1][2]*zoom*
                         SIZE[0]/800.0),
                     int(loaders.image(name, *args, **kwargs)[1][3]*zoom*
                         SIZE[1]/480.0)
                    )
                    )
    else:
        try:
            image = pygame.image.load(name)
        except pygame.error, message:
            logging.debug('Cannot load image:'+str(name), 2)
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
def image_layer(first, second, pos=(0,0)):
    surface = copy.copy(first)
    surface.blit(second, pos)
    return surface
    
@memoize
def text(text_send, font):
    return font.render(text_send.decode('utf-8'),
            True,
            pygame.color.Color("white"))
@memoize
def track(name):
    try:
        FREQ, BITSIZE, CHANNELS, BUFFER = (44100, -16, 2, 1024)
        pygame.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
        return pygame.mixer.Sound(name)
    except (pygame.error):
        # no sound
        print "Unable to initialize audio."
        return None

