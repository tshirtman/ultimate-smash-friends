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
from usf_modules.new_config import Config
config_ = Config()
general = config_.general
sound_config = config_.audio
MEDIA_DIRECTORY = config_.data_dir
import pygame
import os
class WidgetImageButton(Widget):
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
    def setText(self, text):
        self.text = text
        self.image = loaders.image(
            MEDIA_DIRECTORY+
            os.sep+
            'gui'+
            os.sep+
            "image"+
            os.sep+
            self.text
            )[0]
        if(self.sizex == 0):
            self.sizex = self.sizey
        self.image = pygame.transform.scale(self.image, (self.sizex, self.sizey))
        
