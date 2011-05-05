import pygame
import logging


def draw_rect(surface, rect, color=pygame.Color('white')):
    surface.fill(color, pygame.Rect(rect))


def log_result(function):
    """ this decorator will log the result of a function before returning it
    """

    def decorated(*args, **kwargs):
        result = function(*args, **kwargs)
        logging.info(str(result))
        return result
    return decorated

