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
import logging
from os.path import join

#our modules
from usf.widgets.widget import optimize_size
from usf.widgets.imagebutton import ImageButton
from usf.widgets.label import Label
from usf.widgets.box import HBox
from usf import loaders

CONFIG = loaders.get_config()


class Spinner(HBox):
    """
    A spinner widget. (which could be called "select" too)
    It looks like this:
    <- text ->

    It can be used to select an option (like a character, a game
    mode, etc...).
    """

    def __init__(self, values, width=100):
        """
        values is an array of string. Each string is an option.
        """
        super(Spinner, self).__init__()
        self.focusable = False
        self.parentpos = (0, 0)
        self.extend = False
        self.values = values
        self.orientation = True
        self.center_width = width
        self.surface = pygame.Surface((self.width, self.height))
        self.widgets = []
        self.left_arrow = ImageButton(
                join("gui", CONFIG.general.THEME, "spinner_left.png"),
                join("gui", CONFIG.general.THEME, "spinner_left_hover.png"))

        self.left_arrow.set_size((37, 45))
        self.add(self.left_arrow, margin = 0)
        self.center = Label('',
            background=join(
                "gui",
                CONFIG.general.THEME,
                "spinner_center.png"),
            align="center",
            width=100,
            height=35)

        self.add(self.center, margin = 0, size=(self.center_width, 45))
        self.right_arrow = ImageButton(
                join("gui", CONFIG.general.THEME, "spinner_right.png"),
                join("gui", CONFIG.general.THEME, "spinner_right_hover.png"))
        self.right_arrow.set_size((37, 45))
        self.add(self.right_arrow, margin = 0)
        self.update_pos()
        self.update_size()

        self.text = values[0]
        self.state = False
        self.height = optimize_size((250, 30))[1]
        self.width = (
                optimize_size((25, 30))[0] * 2 +
                optimize_size((self.center_width, 30))[0])
        self.set_index(0)

    def handle_mouse(self, event):
        if self.state:
            event.dict['pos'] = (
                    event.dict['pos'][0] - self.parentpos[0] - self.x,
                    event.dict['pos'][1] - self.parentpos[1] - self.y)

        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        self.left_arrow.state = False
        self.right_arrow.state = False
        if (
                0 < event.dict['pos'][0] < self.width and
                0 < event.dict['pos'][1] < self.height):
            self.state = True
            for widget in self.widgets:
                if (
                        widget.x < x < widget.x + widget.width and
                        widget.y < y < widget.y+widget.height):
                    if widget == self.left_arrow or widget == self.right_arrow:
                        widget.state = True
                        if event.type == pygame.MOUSEBUTTONUP:
                            if widget == self.right_arrow:
                                self.index += 1
                                if self.index > len(self.values)-1:
                                    self.index = 0
                            else:
                                self.index -= 1
                                if self.index < 0:
                                    self.index = len(self.values)-1
                            self.text = self.values[self.index]
                            self.center.set_text(self.text)
                            return (self, False)
            return False, self
        self.state = False
        return (False, False)

    def get_value(self):
        """
        Get the current value of the spinner.
        """
        return self.values[self.index]

    def get_index(self):
        """
        Get the index (the range of the current value).
        """
        return self.index

    def set_index(self, index):
        """
        Set the index (the range of the current value) of the spinner.
        """
        try:
            self.index = index
            self.text = self.values[self.index]
            self.center.set_text(self.text)

        except IndexError:
            logging.warning("Not enough value in the spinner: " + str(index))

    def set_value(self, value):
        """
        Set the value of the spinner. The value must be in the array that was
        passed in the __init__ function.
        """
        try:
            self.set_index(self.values.index(value))
        except ValueError:
            logging.warning("No entry named: " + str(value))

    def handle_keys(self, event):
        if (
                event.dict["key"] == pygame.K_DOWN or
                event.dict["key"] == pygame.K_UP) and not self.state:
            self.state = True
            self.right_arrow.state = True
            self.left_arrow.state = True
            return False, self

        if event.dict["key"] == pygame.K_RIGHT:
            if self.get_index() + 1 < len(self.values):
                self.set_index(self.get_index() + 1)
            return self, self

        if event.dict["key"] == pygame.K_LEFT:
            if self.get_index() > 0:
                self.set_index(self.get_index() - 1)
            return self, self

        self.right_arrow.state = False
        self.left_arrow.state = False
        self.state = False
        return False, False
