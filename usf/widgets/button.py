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

import pygame
from widget import Widget, get_scale, optimize_size
from usf import loaders
from usf.font import fonts

from label import Label

class Button(Label):
    posy = 0
    def set_size(self, (w,h)):
        self.height = h
        self.width = w
        #center the text vertically
        self.posy = self.height/2-self.surface_text.get_height()/2
        #center the text horizontally
        self.posx = self.width/2-self.surface_text.get_width()/2
        #   self.posy = 0
    def draw(self):
        #TODO : a @memoize function, and a config file with the color
        if self.state == True:
            return loaders.image_layer(loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    'gui'+
                    os.sep+
                    config.general['THEME']+
                    os.sep+
                    'back_button_hover.png', scale=(self.width, self.height))[0], self.surface_text, (self.posx, self.posy))
        else:
            return loaders.image_layer(loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    'gui'+
                    os.sep+
                    config.general['THEME']+
                    os.sep+
                    'back_button.png', scale=(self.width, self.height))[0], self.surface_text, (self.posx, self.posy))
    def handle_mouse(self,event):
        if event.type == pygame.MOUSEBUTTONUP:
            self.state = False
            return self,False
        else:
            if self.state == True:
                event.dict['pos'] =(event.dict['pos'][0] - self.parentpos[0]-self.x, event.dict['pos'][1] - self.parentpos[1] - self.y)
            if 0 < event.dict['pos'][0] < self.width and 0 < event.dict['pos'][1] < self.height:
                self.state = True
                return False,self
            self.state = False
            return False,False
