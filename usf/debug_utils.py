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
        """ this will be overwritten by the decorated function decorator
        """
        result = function(*args, **kwargs)
        logging.info(str(result))

        return result

    decorated.__name__ = function.__name__
    decorated.__doc__ = function.__doc__

    return decorated
