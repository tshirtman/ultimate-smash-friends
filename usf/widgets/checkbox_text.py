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
This module provide a checkbox with a label beside it.

'''

#standards imports
import pygame
from os.path import join

#our modules
from usf import loaders
from usf.widgets.box import HBox
from usf.widgets.image import Image
from usf.widgets.label import Label

CONFIG = loaders.get_config()


class TextCheckBox(HBox):
    """
    A checkbox widget.
    """

    def __init__(self, text):
        super(TextCheckBox, self).__init__()
        self.height = 40
        self.text = text
        self.widgets = []
        self.widgets = []
        self.state = False
        self.checked = False
        self.focusable = False

        w = self.width
        self.surface = pygame.Surface((self.width, self.height))
        self.widgets = []

        #left radius
        self.left_border = Image(join(
            "gui",
            CONFIG.general.THEME,
            "checkbox_left.png"))

        self.left_border.set_size((12, self.height))
        self.add(self.left_border, margin=0)


        self.center = Label(
                self.text + " ",
                background=join("gui",
                    CONFIG.general.THEME,
                    "checkbox_center.png"),
                align="center")

        if(w < 12+37):
            w = 12+37 + self.center.width
        self.add(self.center, margin = 0, size=(w-12-37, self.height))
        #print self.center.get_text()

        self.check = Image(join(
            "gui",
            CONFIG.general.THEME,
            "checkbox_empty_right.png"))

        self.add(self.check, margin = 0, size=(37, self.height))
        self.update_pos()
        self.update_size()
        self.update_image()

    def set_size(self, (w, h)):
        """
        Set the size of the widget.
        """
        self.height = h
        self.width = w

    def handle_mouse(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.checked:
                self.checked = False
            else:
                self.checked = True
            self.update_image()

            return self, False

        else:
            x = event.dict['pos'][0]
            y = event.dict['pos'][1]

            if self.state:
                x -= self.parentpos[0] + self.x
                y -= self.parentpos[1] + self.y

            if 0 < x < self.width and 0 < y < self.height:
                self.state = True
                self.update_image()

                return False, self

            self.state = False
            self.update_image()

            return False, False

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
            self.left_border.setImage(join(
                "gui",
                CONFIG.general.THEME,
                "checkbox_left_hover.png"))

            self.center.background_path = join(
                    "gui",
                    CONFIG.general.THEME,
                    "checkbox_center_hover.png")

            if self.checked:
                self.check.setImage(join(
                    "gui",
                    CONFIG.general.THEME,
                    "checkbox_full_right_hover.png"))

            else:
                self.check.setImage(join(
                    "gui",
                    CONFIG.general.THEME,
                    "checkbox_empty_right_hover.png"))

            #self.center.init()

        else:
            self.left_border.setImage(join(
                "gui",
                CONFIG.general.THEME,
                "checkbox_left.png"))

            self.center.background_path = join(
                    "gui",
                    CONFIG.general.THEME,
                    "checkbox_center.png")

            if self.checked:
                self.check.setImage(join(
                    "gui",
                    CONFIG.general.THEME,
                    "checkbox_full_right.png"))

            else:
                self.check.setImage(join(
                    "gui",
                    CONFIG.general.THEME,
                    "checkbox_empty_right.png"))

            #self.center.init()

    def handle_keys(self, event):
        if (event.dict["key"] == pygame.K_DOWN
                or event.dict["key"] == pygame.K_UP) and not self.state:
            self.state = True
            self.update_image()
            return False, self

        if event.dict["key"] == pygame.K_RETURN:
            if self.checked:
                self.checked = False
            else:
                self.checked = True
            self.update_image()
            return self, self

        self.state = False
        self.update_image()
        return False, False
