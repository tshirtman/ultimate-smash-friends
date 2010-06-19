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


class Label(Widget):
    """
    A simple label widget
    """

    def init(self):
        pass

    def __init__(self, text, *args, **kwargs):
        self.text = text
        self.indent = 0
        self.state = False
        #self.init()
        self.surface_text  = loaders.text(self.text, fonts['sans']['25'])

        if "height" in kwargs:
            self.height = kwargs['height']
        else:
            self.height = self.surface_text.get_height()
        if "width" in kwargs:
            self.width = kwargs['width']
        else:
            self.width = self.surface_text.get_width()
        if "margin" in kwargs:
            self.txtmargin= kwargs['margin']
        else:
            margin = 0
        if "background" in kwargs:
            self.background = loaders.image(join(config.sys_data_dir, kwargs['background']),
                scale=(self.width,self.height))[0]
            self.surface = loaders.image_layer(self.background,self.surface_text,(self.txtmargin,0))
        else:
            self.background = None
            self.surface = self.surface_text

    def draw(self):
        return self.surface

    def setText(self,text):
        """
        Change the text of the widget
        """
        self.text = text
        self.surface_text  = game_font.render(
            _(self.text),
            True,
            pygame.color.Color("white")
            )
        if self.background != None:
            self.surface = loaders.image_layer(self.background,self.surface_text,(self.txtmargin,0))
        else:
            self.surface = self.surface_text
