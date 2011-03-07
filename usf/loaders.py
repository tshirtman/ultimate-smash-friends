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
import os
import sys
import copy
import pygame
import logging
import math

from config import Config
config = Config()
from ConfigParser import SafeConfigParser

try:
    from pygame.locals import BLEND_RGBA_MAX
    from pygame.locals import BLEND_RGBA_ADD
    from pygame.locals import BLEND_RGBA_SUB
    from pygame.locals import BLEND_RGBA_MULT
    from pygame.locals import BLEND_RGBA_MIN
except:
    Log().log("old version of pygame no BLEND_RGBA_MAX")
    BLEND_RGBA_MAX = None

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
        img = pygame.transform.flip(
            image(name,*args, **kwargs)[0],
            True, #flip horizontaly
            False #not verticaly
            )

    elif 'lighten' in kwargs and kwargs['lighten']:
        #logging.debug('lightened: '+name)
        kwargs['lighten'] = False
        img = image(name, *args, **kwargs)[0].copy()
        if BLEND_RGBA_MAX is not None:
            img.fill(
                    pygame.Color('lightgrey'),
                    None,
                    BLEND_RGBA_MAX
                    )
        else:
            # this mean this version of pygame is to old to use the effect
            # above, an equivalent method would be a good thing
            logging.warning('pygame version < 1.9 no alpha blend.')
            pass #nothing for the moment

    elif 'alpha' in kwargs and kwargs['alpha'] is not None:
        alpha = kwargs['alpha']
        if not 0 <= alpha <= 1:
            logging.warning('bad alpha value: %s' % alpha)
            alpha = min(1, max(0, alpha))

        kwargs['alpha'] = None
        img = image(name, *args, **kwargs)[0].copy()
        img.fill(
                pygame.Color(255, 255, 255, int(alpha*255)),
                image(name, *args, **kwargs)[1],
                BLEND_RGBA_MULT
                )

    elif 'scale' in kwargs and kwargs['scale'] is not None:
        if len(kwargs['scale']) is not 2:
            raise Exception.ValueError(
                "scale parameter should be a tuple of two integers"
                )
        scale = kwargs['scale']
        kwargs['scale'] = None
        if config.general['SMOOTHSCALE']:
            img = pygame.transform.smoothscale(
                image(name, *args, **kwargs)[0],
                scale
                )
        else:
            img = pygame.transform.scale(
                image(name, *args, **kwargs)[0],
                scale
                )


    elif 'zoom' in kwargs and kwargs['zoom'] not in (None, 1):
        zoom = kwargs['zoom']
        kwargs['zoom'] = None
        #logging.debug('scaling image '+name+' :'+str(zoom))
        if config.general['SMOOTHSCALE']:
            img = pygame.transform.smoothscale(
                    image(name, **kwargs)[0],
                    (
                     int(image(name, *args, **kwargs)[1][2]*zoom),
                     int(image(name, *args, **kwargs)[1][3]*zoom)
                    )
                    )
        else:
            img = pygame.transform.scale(
                    image(name, **kwargs)[0],
                    (
                     int(image(name, *args, **kwargs)[1][2]*zoom),
                     int(image(name, *args, **kwargs)[1][3]*zoom)
                    )
                    )

    elif 'rotate' in kwargs and kwargs['rotate'] not in (None, 0):
        angle = kwargs['rotate']
        kwargs['rotate'] = None
        img = pygame.transform.rotate(image(name, **kwargs)[0], angle *180/math.pi)

    else:
        try:
            img = pygame.image.load(name)
        except pygame.error, message:
            logging.debug('Cannot load image:'+str(name), 2)
            raise# SystemExit, message
        img = img.convert_alpha()
    return img, img.get_rect()

@memoize
def image_layer(first, second, pos=(0,0)):
    surface = copy.copy(first)
    surface.blit(second, pos)
    return surface

@memoize
def text(text_send, font, r=240, g=240, b=240, a=250):
    return font.render(text_send.decode('utf-8'),
            True,
            pygame.color.Color(r, g, b, a))

@memoize
def paragraph(text_send, font):
    max_len = text("", font)
    for texte in text_send.split('\n'):
        if text(texte, font).get_width() > max_len.get_width():
            max_len = text(texte, font)

    text_re = pygame.surface.Surface((max_len.get_width(), len(text_send.split('\n'))*text("", font).get_height()))

    i = -1
    for texte in text_send.split('\n'):
        i += 1
        surf = text(texte, font)
        text_re.blit(surf, (text_re.get_width()/2 - surf.get_width()/2, i*surf.get_height()))
    return text_re

@memoize
def track(name):
    try:
        FREQ, BITSIZE, CHANNELS, BUFFER = (44100, -16, 2, 1024)
        pygame.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
        return pygame.mixer.Sound(name)
    except (pygame.error):
        # no sound
        logging.info("Unable to initialize audio.")
        return None

@memoize
def get_config():
    return Config()

@memoize
def get_gconfig():
    parser = SafeConfigParser()
    parser.optionxform = str
    parser.read(get_config().sys_data_dir + "game.cfg")
    return parser

