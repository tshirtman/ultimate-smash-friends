################################################################################
# copyright 2009 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
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
from usf_modules.widget import Widget
from usf_modules import loaders
from usf_modules.new_config import Config
config = Config()
general = config.general
keyboard_config = config.keyboard
sound_config = config.audio
MEDIA_DIRECTORY = config.data_dir
import pygame
import os
class WidgetCheckbox(Widget):
    """
    A simple button image.
    """
    text = ""
    state = "norm"
    def drawSimple(self):
        self.screen.blit(
            self.image,
        (self.posx, self.posy)
        )
    def drawHover(self):
        self.screen.blit(
            self.image,
        (self.posx, self.posy)
        )
    def draw(self):
        if (self.state == "norm"):
            self.drawSimple()
        elif (self.state == "click"):
            self.drawClick()
        elif (self.state == "hover"):
            self.drawHover()
    def setText(self, value):
        if(value.split(':')[0] == "config"):
            if(value.split(':')[1] == "keyboard"):
                numcle=0
                try:
                    while keyboard_config.keys()[numcle] != value.split(':')[2]:
                        numcle += 1

                    self.text = pygame.key.name(eval(keyboard_config.values()[numcle]))
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
        if(self.sizex == 0):
            self.sizex = self.sizey
        if self.text == "True" :
            self.image = loaders.image(
                MEDIA_DIRECTORY+
                os.sep+
                'gui'+
                os.sep+
                general['THEME']+
                os.sep+
                "checkbox_full.png", scale=(self.sizex, self.sizey)
                )[0]
        else :
            self.image = loaders.image(
                MEDIA_DIRECTORY+
                os.sep+
                'gui'+
                os.sep+
                general['THEME']+
                os.sep+
                "checkbox_empty.png", scale=(self.sizex, self.sizey)
                )[0]
        
