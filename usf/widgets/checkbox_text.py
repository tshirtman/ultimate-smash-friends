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

#standards imports
import pygame
import os
from os.path import join

#our modules
from widget import Widget, get_scale, optimize_size
from usf import loaders
from usf.font import fonts
from box import HBox
from image import Image

from label import Label

config = loaders.get_config()


class TextCheckBox(HBox):
    """
    A checkbox widget.
    """

    def __init__(self, text):
        self.orientation = True
        self.height = 40
        self.text = text
        self.init()
        self.widgets = []
        self.widgets = []
        self.state = False
        self.checked = False
        
    def init(self):
        """
        This function can be rewritten in the others widget if the surface
        isn't empty.
        """
        w = self.width
        self.surface = pygame.Surface((self.width,self.height))
        self.widgets = []

        #left radius
        self.left_border = Image(join("gui",
                                      config.general['THEME'],
                                      "checkbox_left.png"))
        self.left_border.set_size((12, self.height))
        self.add(self.left_border, margin=0)

        
        self.center = Label(self.text + " ",
                            background=join("gui",
                                            config.general['THEME'],
                                            "checkbox_center.png"),
                            align="center")
            
        if(w < 12+37):
            w = 12+37 + self.center.width
        self.add(self.center, margin = 0, size=(w-12-37, self.height))
        #print self.center.get_text()

        self.check = Image(join("gui",
                                config.general['THEME'],
                                "checkbox_empty_right.png"))

        self.add(self.check, margin = 0, size=(37, self.height))
        self.update_pos()
        self.update_size()

    def set_size(self, (w,h)):
        """
        Set the size of the widget.
        """
        self.height = h
        self.width = w
        self.init()

    def handle_mouse(self,event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.checked:
                self.checked = False
            else:
                self.checked = True
            self.update_image()

            return self,False

        else:
            x = event.dict['pos'][0]
            y = event.dict['pos'][1]

            if self.state == True:
                x -= self.parentpos[0] + self.x
                y -= self.parentpos[1] + self.y

            if 0 < x < self.width and 0 < y < self.height:
                self.state = True
                self.update_image()

                return False,self

            self.state = False
            self.update_image()

            return False,False

    def get_value(self):
        """
        Get the value of the checkbox, it returns a boolean.
        (true of checked and false if unchecked)
        """
        return self.checked

    def set_value(self, value):
        """
        Set the value of the checkbox, it must be a boolean.
        """
        self.checked = value

    def update_image(self):
        if self.state:
            self.left_border.setImage(join("gui",
                                           config.general['THEME'],
                                           "checkbox_left_hover.png"
                                           )
                                     )
            self.center.background_path = join("gui",
                                               config.general['THEME'],
                                               "checkbox_center_hover.png"
                                              )
            if self.checked:
                self.check.setImage(join("gui",
                                         config.general['THEME'],
                                         "checkbox_full_right_hover.png"
                                        )
                                   )
            else:
                self.check.setImage(join("gui",
                                         config.general['THEME'],
                                         "checkbox_empty_right_hover.png"))
            self.center.init()
        
        else:
            self.left_border.setImage(join("gui",
                                           config.general['THEME'],
                                           "checkbox_left.png"))
            self.center.background_path = join("gui",
                                               config.general['THEME'],
                                               "checkbox_center.png")
            if self.checked:
                self.check.setImage(join("gui",
                                         config.general['THEME'],
                                         "checkbox_full_right.png"))
            else:
                self.check.setImage(join("gui",
                                         config.general['THEME'],
                                         "checkbox_empty_right.png"))
            self.center.init()
