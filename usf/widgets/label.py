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
A label widget, to place text.
'''

import pygame
from os.path import join

from usf.widgets.widget import Widget
import usf
from usf import loaders
from usf.font import fonts
CONFIG = loaders.get_config()


class Label(Widget):
    """
    A simple label widget
    """

    def __init__(self, text, **kwargs):
        super(Label, self).__init__()

        if "margin" in kwargs:
            self.txtmargin = kwargs['margin']
        else:
            self.txtmargin = 0

        if "align" in kwargs and kwargs['align'] == "center":
            self.align = "center"
        else:
            self.align = ''

        if "background" in kwargs:
            self.background_path = kwargs['background']
        
        if "background_expand" in kwargs:
            self.background_expand = kwargs['background_expand']
        else:
            self.background_expand = False

        self.dynamic_size = [True, True]

        if "width" in kwargs:
            self.dynamic_size[0] = False
            self.width = kwargs['width']
        if "height" in kwargs:
            self.dynamic_size[1] = False
            self.height = kwargs['height']

        self.set_text(text)

        self.state = False

    def set_size(self, (w, h)):
        """
        Set the size of the widget.
        This function is usually called by the container, HBox or VBox.
        """
        super(Label, self).set_size((w, h))
        self.set_text(self.text)

    def set_text(self, text):
        """ update the text surface
        """
        self.text = text
        self.surface_text  = loaders.text(self.text, fonts['sans']['normal'])

        if self.dynamic_size[0]:
            self.height = self.surface_text.get_height() + self.txtmargin * 2

        if self.dynamic_size[1]:
            self.width = self.surface_text.get_width() + self.txtmargin * 2

        if self.align == "center":
            self.indent = self.width / 2 - self.surface_text.get_width() / 2
        else:
            self.indent = 0

        self.horizontal_indent = (
                self.height / 2 - self.surface_text.get_height() / 2)

        try:
            if self.background_expand:
                self.background = loaders.image(
                    join(
                        CONFIG.sys_data_dir, self.background_path),
                    expand=(self.width, self.height, 10))[0]
            else:
                self.background = loaders.image(
                    join(
                        CONFIG.sys_data_dir, self.background_path),
                    scale=(self.width, self.height))[0]

            self.surface = loaders.image_layer(
                    self.background,
                    self.surface_text,
                    (self.txtmargin + self.indent, self.horizontal_indent))

        except AttributeError:
            self.surface = self.surface_text
        self.screen = pygame.display.get_surface()

    def get_text(self):
        """
        Get the current text of the widget.
        """
        return self.text

