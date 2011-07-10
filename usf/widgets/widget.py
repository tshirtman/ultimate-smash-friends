################################################################################
# copyright 2010 Lucas Baudin <xapantu@gmail.com>                              #
#                                                                              #
# This file is part of Ultimate Smash Friends.                                 #
#                                                                              #
# Ultimate Smash Friends is free software: you can redistribute it and/or      #
# modify it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or (at your   #
# option) any later version.                                                   #
#                                                                              #
# Ultimate Smash Friends is distributed in the hope that it will be useful, but#
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or#
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# You should have received a copy of the GNU General Public License along with #
# Ultimate Smash Friends.  If not, see <http://www.gnu.org/licenses/>.         #
################################################################################

'''
The base widget object. Probably not tu use directly, but used as base for all
other widgets.

'''

import pygame
import time

from usf import loaders

CONFIG = loaders.get_config()


class Widget(object):
    """
    This class is the base of all other widget.
    """

    width = 0
    height = 0
    x = 0
    y = 0
    margin = 0
    margin_left = 0
    parentpos = (0, 0)
    text = ""
    widget_id = ""
    animation_speed = 1.0
    last_animation = 0.0
    properties = {}
    focusable = False

    def __init__(self):
        """
        This function can be rewritten in the others widgets to
        have a custom argument lists.
        """
        self.surface = pygame.Surface((self.width, self.height))
        self.screen = pygame.display.get_surface()

    def draw(self):
        """
        Return the widget surface. This fonction is often overrided.
        """
        self.screen.blit(
                self.surface, (
                    self.parentpos[0] + self.x,
                    self.parentpos[1] + self.y))

    def set_size(self, (w, h)):
        """
        This function is used to resize a widget.
        """
        self.height = h
        self.width = w

    def handle_mouse(self, event):
        """
        This function is used for mouse events.
        """
        return False, False

    def set_align(self, align):
        pass

    def update_pos(self):
        pass

    def update_size(self):
        pass

    def handle_keys(self, event):
        return False, False

    def set_id(self, value):
        self.widget_id = value

    def get_id(self):
        return self.widget_id

    def start_anim(self):
        if self.animation_speed:
            self.animation()

        elif(self.last_animation + self.animation_speed <= time.time()):
            self.last_animation = time.time()
            self.animation()

    def animation(self):
        pass


#these functions are used to handle the others screen resolutions
#FIXME : maybe they could go to loaders ?


#XXX WTF? still useful?
def optimize_size(size):
    return size


def get_scale(surface):
    return (
            surface.get_width() * 800 / CONFIG.general['WIDTH'],
            surface.get_height()*480/CONFIG.general['HEIGHT'])


