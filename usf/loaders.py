# -*- coding: utf-8 -*-
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
pygame_loaders is a set of classes/functions, to use mainly for image
loadings/processing with pygame, it uses memoization to accelerate successive
loadings of images, and repeating the same process on the same images, acting
as a real cache for image loading and manipulations, it help to load tracks and
such too.

This module was originaly a simple syntaxic sugar for a pygame project,

for performances sake it quickly gained memoization, allowing you to call for
images, not carring if you already loaded them or not. As you may need to do
that for result of process on those images, the image loader gained a lot of
keywords, that allow to call images with a zooms, blending, reversing, scaling,
rotating, and all sort of combinations, everytime doing only the required parts
of those processings, and using previous results of processings. Okay, it can
takes up big memory amounts, but well, i found it's most of the time less of
the problem than CPU, so if you agree, you will probably agree that for games,
it's an acceptable tradeoff.

Oh, for convenience sakes, it can load bunch of text and musics, too, the
processing part is less developped on these ones, but contributions are
welcomed, and memoization is done for them too.

Anyway, using it is quite simple, simply import the needed loaders from
loaders.py, and for an image filepath, image() will return a tupple containing
the image and it's size, no need to store it away, calling the loader a second
time or more is basically free, thanks to memoization.

pygame must be loaded and display_mode set to perform most image operations.

>>> from pygame_loaders import image
>>> image('myimage.png') # actual loading
(<Surface(491x546x32 SW)>, <rect(0, 0, 491, 546)>)

>>> image('myimage.png') # returning same result, without any loading
>>> image("myimage.png", zoom=1.5) # only performing zoom
(<Surface(736x819x32 SW)>, <rect(0, 0, 736, 819)>)

>>> image("myimage.png", zoom=1.5, alpha=0.4) # only changing alpha
(<Surface(736x819x32 SW)>, <rect(0, 0, 736, 819)>)

'''

import copy
import logging
import math
import os
from ConfigParser import SafeConfigParser

import pygame
from pygame.locals import BLEND_RGB_MAX, BLEND_RGBA_MULT

from usf import CONFIG
from usf.memoize import memoize

try:
    from pygame.locals import BLEND_RGBA_MAX
except ImportError:
    logging.info("old version of pygame no BLEND_RGBA_MAX")
    BLEND_RGBA_MAX = None

@memoize
def get_gconfig():
    parser = SafeConfigParser()
    parser.optionxform = str
    parser.read(os.path.join(CONFIG.system_path, 'game.cfg'))

    return parser

def _zoom(name, kwargs):
    """ takes care of the zoom argument, and pass the rest to image()
    zoom is used as a multiplication in size on both dimension of the image.
    return the end result.
    """
    zoom = kwargs['zoom']
    kwargs['zoom'] = None
    #logging.debug('scaling image '+name+' :'+str(zoom))
    if CONFIG.general.SMOOTHSCALE:
        img = pygame.transform.smoothscale(
                image(name, **kwargs)[0],
                (
                 int(image(name, **kwargs)[1][2]*zoom),
                 int(image(name, **kwargs)[1][3]*zoom)))
    else:
        img = pygame.transform.scale(
                image(name, **kwargs)[0],
                (
                 int(image(name, **kwargs)[1][2]*zoom),
                 int(image(name, **kwargs)[1][3]*zoom)))

    return img


def _expand(name, kwargs):
    """
    This feature can be used for buttons, which have a rounded border. But
    if we just scale them, the borders look bad, because the rounded corner
    are also scaled

    So, we have to split it to keep a consistent image.
    """
    if len(kwargs['expand']) is not 3:
        raise ValueError(
            "expand parameter should be a tuple of three integers: width,"
            " height, corner")

    expand = kwargs['expand']
    corner = expand[2]
    width = expand[0]
    height = expand[1]
    kwargs['expand'] = None
    img = pygame.Surface((expand[0], expand[1]), pygame.locals.SRCALPHA)

    # Get source image dimensions
    img_from = image(name)[0]
    width_image = img_from.get_width()
    height_image = img_from.get_height()

    # Top left corner
    img_source = image(name,
                       crop=(corner, corner, 0, 0))[0]
    img.blit(img_source, (0, 0))

    # Bottom right corner
    img_source = image(name,
            crop=(corner, corner, width_image - corner, 0))[0]

    img.blit(img_source, (width - corner, 0))

    # Bottom left corner
    img_source = image(name,
            crop=(
                corner,
                corner,
                width_image - corner,
                height_image - corner))[0]

    img.blit(img_source, (width - corner, height - corner))

    # Top right corner
    img_source = image(name,
                       crop=(corner, corner, 0, height_image - corner))[0]
    img.blit(img_source, (0, height - corner))

    # Left part
    img_source = image(name,
                       crop=(corner, height_image - corner*2, 0, corner),
                       scale=(corner, height - 2*corner))[0]
    img.blit(img_source, (0, corner))

    # Right part
    img_source = image(name,
            crop=(
                corner,
                height_image - corner*2,
                width_image - corner, corner),
            scale=(corner, height - 2*corner))[0]
    img.blit(img_source, (width - corner, corner))

    # Top part
    img_source = image(name,
                       crop=(width_image - 2*corner, corner, corner, 0),
                       scale=(width - 2*corner, corner))[0]
    img.blit(img_source, (corner, 0))

    # Bottom part
    img_source = image(name,
            crop=(
                width_image - 2*corner,
                corner,
                corner,
                height_image - corner),
            scale=(width - 2*corner, corner))[0]
    img.blit(img_source, (corner, height - corner))

    # Center
    img_source = image(name,
            crop=(width_image - 2 * corner,
                height_image - 2 * corner,
                corner,
                corner),
            scale=(width - 2 * corner, height - 2 * corner))[0]
    img.blit(img_source, (corner, corner))
    return img


def _crop(name, kwargs):
    """
    return a portion of an image.
    crop parameter should be a tuple of four integers:
    width, height, x, y
    """

    if len(kwargs['crop']) is not 4:
        raise ValueError(
            "crop parameter should be a tuple of four integers: width,"
            "height, x, y")

    crop = kwargs['crop']
    kwargs['crop'] = None
    img_src = image(name, **kwargs)[0]
    img = pygame.Surface((crop[0], crop[1]), pygame.locals.SRCALPHA)
    rect = pygame.Rect(crop[2], crop[3], crop[0], crop[1])
    img.blit(img_src, (0, 0), rect)
    return img


def _lighten(name, kwargs):
    """ return the image with a all visible pixels saturated in white
    """
    #logging.debug('lightened: '+name)
    kwargs['lighten'] = False
    img = image(name, **kwargs)[0].copy()
    if BLEND_RGBA_MAX is not None:
        img.fill(
                pygame.Color('lightgrey'),
                None,
                BLEND_RGB_MAX)
    else:
        # this mean this version of pygame is to old to use the effect
        # above, an equivalent method would be a good thing
        logging.warning('pygame version < 1.9 no alpha blend.')
    return img


def _scale(name, kwargs):
    """ XXX: Difference with zoom?
    """
    if len(kwargs['scale']) is not 2:
        raise ValueError(
            "scale parameter should be a tuple of two integers")

    scale = kwargs['scale']
    kwargs['scale'] = None
    if CONFIG.general.SMOOTHSCALE:
        img = pygame.transform.smoothscale(
            image(name, **kwargs)[0],
            scale)
    else:
        img = pygame.transform.scale(
            image(name, **kwargs)[0], scale)
    return img


def _alpha(name, kwargs):
    """ use BLEND_RGBA_MULT to produce images with different alpha
    """
    alpha = kwargs['alpha']
    if not 0 <= alpha <= 1:
        logging.warning('bad alpha value:'+ str(alpha))
        alpha = min(1, max(0, alpha))

    kwargs['alpha'] = None
    img = image(name, **kwargs)[0].copy()
    img.fill(
            pygame.Color(255, 255, 255, int(alpha*255)),
            image(name, **kwargs)[1],
            BLEND_RGBA_MULT)
    return img


def _load(name):
    """ Load an image and convert it for faster blit operations, always
    consider the image to have an alpha channel.
    """
    try:
        img = pygame.image.load(name)
    except pygame.error:
        logging.debug('Cannot load image:'+str(name), 2)
        raise
    return img.convert_alpha()


def _reverse(name, kwargs):
    """ return the image flipped horizontaly.
    """
    kwargs['reversed'] = False
    return pygame.transform.flip(
        image(name, **kwargs)[0],
        True, #flip horizontaly
        False) #not verticaly


def _rotate(name, kwargs):
    """ rotate the image of an arbitraty angle.
    """
    angle = kwargs['rotate']
    kwargs['rotate'] = None
    return pygame.transform.rotate(
            image(name, **kwargs)[0], angle * 180/math.pi)


@memoize
def image(name, *args, **kwargs):
    """
    A function to load an image, memoized, and with manipulation capabilities:
        scale, zoom
        reverse horizontaly,
        produce a lightened version of an image,
        change alpha of an image,
        crop
        and extand an image.
    """
    keywords = {
            'reversed': _reverse,
            'lighten': _lighten,
            'alpha': _alpha,
            'scale': _scale,
            'crop': _crop,
            'expand': _expand,
            'zoom': _zoom,
            'rotate': _rotate,
            }

    for kw in keywords:
        if kw in kwargs and kwargs[kw]:
            img = keywords[kw](name, kwargs)
            break
    else:
        img = _load(name)

    return img, img.get_rect()


@memoize
def image_layer(first, second, pos=(0, 0)):
    """ return a copy of the first image, with the second one blitted on it
    """
    surface = copy.copy(first)
    surface.blit(second, pos)
    return surface


@memoize
def text(text_send, font, red=240, green=240, blue=240, alpha=250):
    """ return a surface with the text rendered on it, in the color passed in
    parameter
    """
    return font.render(text_send.decode('utf-8'),
            True,
            pygame.color.Color(red, green, blue, alpha))


@memoize
def paragraph(text_send, font):
    """ Load a bunch of text in a surface, formated depending on it's length
    """

    max_len = text("", font)
    for texte in text_send.split('\n'):
        if text(texte, font).get_width() > max_len.get_width():
            max_len = text(texte, font)

    text_re = pygame.surface.Surface(
            (max_len.get_width(),
                len(text_send.split('\n'))*text("", font).get_height()))

    i = -1
    for texte in text_send.split('\n'):
        i += 1
        surf = text(texte, font)
        text_re.blit(surf, (text_re.get_width()/2 - surf.get_width()/2,
            i * surf.get_height()))
    return text_re


@memoize
def track(name):
    """
    Load an audio file to play in the game
    """

    try:
        freq, bitsize, channels, buff = (44100, -16, 2, 1024)
        pygame.mixer.init(freq, bitsize, channels, buff)
        return pygame.mixer.Sound(name)
    except (pygame.error):
        # no sound
        logging.info("Unable to initialize audio.")
        return None


