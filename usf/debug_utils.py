'''
This module provide functions made to make easier the debug work, may diseapear
in the future.

'''

import pygame
import logging


def draw_rect(surface, rect, color=pygame.Color('white')):
    ''' a simple function to draw a colored rect on a surface
    '''
    surface.fill(color, pygame.Rect(rect))


def log_result(function):
    """ this decorator will log the result of a function before returning it
    """

    def decorated(*args, **kwargs):
        result = function(*args, **kwargs)
        logging.info(str(result))
        return result

    decorated.__name__ = function.__name__
    decorated.__doc__ = function.__doc__
    return decorated


