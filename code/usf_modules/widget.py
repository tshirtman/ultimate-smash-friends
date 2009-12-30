################################################################################
# copyright 2009 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
#                                                                              #
# This file is part of Ultimate Smash Friends                                  #
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
import pygame
from usf_modules.config import (
        config,
        sound_config,
        save_conf,
        load_config,
        save_sound_conf,
        load_sound_config,
        save_keys_conf,
        load_key_config
        )
import os
class Widget (object):
    """
    This class is the base of all other widget.
    """
    sizex = 0
    sizey = 0
    posx = 0
    posy = 0
    name = "name"
    action = "print 'click'"
    selectable = False
    def __init__(self, screen):
        self.game_font = pygame.font.Font(None, screen.get_height()/20)
        self.screen = screen
        self.load()
    def load(self):
        pass
    def drawSimple(self):
        pass
    def drawHover(self):
        self.drawSimple()
    def set_sizex(self, size):
        self.sizex =size
        self.load()
    def set_sizey(self, size):
        self.sizey =size
        self.load()
