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
A button widget, with a label.
'''
import pygame
from os.path import join

from usf import CONFIG
from usf.widgets.label import Label


class Button(Label):
    """
    A simple button.
    It returns a callback when we click on it.
    """

    def __init__(self, text):
        background_path = join(
                'gui',
                CONFIG.general.THEME,
                'back_button.png')

        super(Button, self).__init__(
                text,
                align="center",
                background=background_path,
                background_expand=True)

        self.properties["size_request"] = (220, 50)
        self.dynamic_size = [False, False]

    def set_size(self, (w, h)):
        """
        Set the size of the widget.
        This function is usually called by the container, HBox or VBox.
        """
        self.height = h
        self.width = w
        super(Button, self).set_size((w, h))

        #center the text vertically
        #self.posy = self.height/2-self.surface_text.get_height()/2

        #center the text horizontally
        #self.posx = self.width/2-self.surface_text.get_width()/2

    def hover(self):
        self.background_path = join(
                'gui',
                CONFIG.general.THEME,
                'back_button_hover.png')
        self.set_text(self.text)

    def out(self):
        self.background_path = join(
                'gui',
                CONFIG.general.THEME,
                'back_button.png')
        self.set_text(self.text)

    def handle_mouse(self, event):
        """
        This function handles mouse event. It returns a callback when we
        click on it.
        """
        if event.type == pygame.MOUSEBUTTONUP:
            self.state = False
            self.out()
            return self, False
        else:
            x = event.dict['pos'][0]
            y = event.dict['pos'][1]
            if self.state:
                x -= self.parentpos[0] + self.x
                y -= self.parentpos[1] + self.y
            if 0 < x < self.width and 0 < y < self.height:
                self.state = True
                self.hover()
                return False, self
            self.out()
            self.state = False
            return False, False


    def handle_keys(self, event):
        if (
                event.dict["key"] == pygame.K_DOWN or
                event.dict["key"] == pygame.K_UP) and not self.state:
            self.state = True
            return False, self

        if event.dict["key"] == pygame.K_RETURN:
            return self, self

        self.state = False
        return False, False

