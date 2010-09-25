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
from os.path import join

from widget import Widget, get_scale, optimize_size
from usf import loaders
from usf.font import fonts
config = loaders.get_config()


class Label(Widget):
    """
    A simple label widget
    """

    def init(self):
        self.surface_text  = loaders.text(self.text, fonts['sans']['normal'])
        if self.align == "center":
            self.indent = self.width/2-self.surface_text.get_width()/2

        self.horizontal_indent = self.height/2-self.surface_text.get_height()/2

        try:
            self.background = loaders.image(join(config.sys_data_dir, self.background_path),
                scale=(self.width,self.height))[0]
            self.surface = loaders.image_layer(self.background,self.surface_text,(self.txtmargin+self.indent, self.horizontal_indent))
        except AttributeError:
            self.surface = self.surface_text
        self.screen = pygame.display.get_surface()

    def __init__(self, text, *args, **kwargs):
        self.text = text
        self.indent = 0
        self.horizontal_indent = 0
        self.state = False
        self.txtmargin = 0
        self.align = ""
        self.surface_text  = loaders.text(self.text, fonts['sans']['normal'])

        self.height = self.surface_text.get_height()
        self.width = self.surface_text.get_width()

        if "margin" in kwargs:
            self.txtmargin= kwargs['margin']
        else:
            margin = 0
        if "align" in kwargs and kwargs['align'] == "center":
            self.align = "center"
            self.indent = self.width/2-self.surface_text.get_width()/2
        if "background" in kwargs:
            self.background_path = kwargs['background']
            
        self.init()

    def set_text(self,text):
        """
        Change the text of the widget.
        """
        self.text = text
        self.init()

    def get_text(self):
        """
        Get the current text of the widget.
        """
        return self.text


