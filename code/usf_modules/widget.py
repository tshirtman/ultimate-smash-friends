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
        save_conf,
        load_config,
        save_sound_conf,
        load_sound_config,
        save_keys_conf,
        load_key_config,
        keyboard_config,
        reverse_keymap
        )
from usf_modules.new_config import Config
config_ = Config()
general = config_.general
sound_config = config_.audio
keyboard = config_.keys
MEDIA_DIRECTORY = config_.data_dir
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
    text = ""
    anim = False
    def __init__(self, screen):
        self.game_font = pygame.font.Font(
            MEDIA_DIRECTORY +
            os.sep +
            "gui" +os.sep + general['THEME'] + os.sep +
            "font.otf", screen.get_height()/20)
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
    def setText(self, value):
        if(value.split(':')[0] == "config"):
            if(value.split(':')[1] == "keyboard"):
                numcle=0
                try:
                    while(keyboard_config.values()[numcle] != value.split(':')[2]):
                        numcle += 1
                    exec("self.text = pygame.key.name(pygame." + reverse_keymap[keyboard_config.keys()[numcle]] + ")")
                except:
                    self.text ="not defined"
            elif(value.split(':')[1] == "sounds"):
                self.text = str(sound_config[value.split(':')[2]])
            else:
                if(general[value.split(':')[1]] == 0):
                    self.text = "False"
                else:
                    self.text = str(general[value.split(':')[1]])
        else:
            self.text = value
