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

#standarts imports
import pygame
import os
from os.path import join

#our modules
from widget import Widget, get_scale, optimize_size
from usf import loaders
from usf.font import fonts
from label import Label

config = loaders.get_config()


class Button(Label):
    """
    A simple button.
    It returns a callback when we click on it.
    """
    posy = 0

    def set_size(self, (w,h)):
        """
        Set the size of the widget.
        This function is usually called by the container, HBox or VBox.
        """
        self.height = h
        self.width = w
        
        #center the text vertically
        self.posy = self.height/2-self.surface_text.get_height()/2

        #center the text horizontally
        self.posx = self.width/2-self.surface_text.get_width()/2

    def draw(self):
        """
        Draw the widget.
        """
        #mouse over
        if self.state == True:
            surf = loaders.image_layer(loaders.image(join(config.sys_data_dir,
                                                          'gui',
                                                          config.general['THEME'],
                                                          'back_button_hover.png'),
                                                     scale=(self.width, self.height))[0],
                                       self.surface_text,
                                       (self.posx, self.posy))

        #normal
        else:
            surf = loaders.image_layer(loaders.image(join(config.sys_data_dir,
                                                          'gui',
                                                          config.general['THEME'],
                                                          'back_button.png'),
                                                     scale=(self.width, self.height))[0],
                                       self.surface_text,
                                       (self.posx, self.posy))
        self.screen.blit(surf, (self.parentpos[0] + self.x, self.parentpos[1] + self.y))

    def handle_mouse(self,event):
        """
        This function handles mouse event. It returns a callback when we
        click on it.
        """
        if event.type == pygame.MOUSEBUTTONUP:
            self.state = False
            return self,False
        else:
            x = event.dict['pos'][0]
            y = event.dict['pos'][1]
            if self.state == True:
                x -= self.parentpos[0] + self.x
                y -= self.parentpos[1] + self.y
            if 0 < x < self.width and 0 < y < self.height:
                self.state = True
                return False,self
            self.state = False
            return False,False
    
    
    def handle_keys(self,event):
        if (event.dict["key"] == pygame.K_DOWN or event.dict["key"] == pygame.K_UP) and not self.state:
            self.state = True
            return False,self
        
        if event.dict["key"] == pygame.K_RETURN:
            return self, self
        
        self.state = False
        return False, False

