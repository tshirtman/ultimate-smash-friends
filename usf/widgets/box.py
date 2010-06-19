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
from button import Button

from usf import loaders
from usf.font import fonts
config = loaders.get_config()

class Container(Widget):
    """
    This widget is never used directly, it is used to be a base for the HBox and VBox widget
    """

    def update_size(self):
        """
        This function is used to update the container size after adding a widget.
        """
        sizex = 0
        sizey = 0
        for widget in self.widgets:
            if self.orientation:
                sizex += widget.width
                if sizey < widget.height:
                    sizey = widget.height
            else:
                sizey += widget.height
                if sizex < widget.width:
                    sizex = widget.width
            if type(self) == HBox:
                sizex += widget.margin
            else:
                sizey += widget.margin
            widget.init()
        self.width = sizex
        self.height = sizey

    def update_pos(self):
        """
        updating the position of all widgets in the container
        """
        posx = 0
        posy = 0
        for widget in self.widgets:
            if self.orientation:
                posx += widget.margin
            else:
                posy += widget.margin
            widget.y = posy
            widget.x = posx + widget.margin_left
            if self.orientation:
                posx += widget.width
            else:
                posy += widget.height
            widget.parentpos = (self.parentpos[0] + self.x, self.parentpos[1] + self.y)
            widget.update_size()
            widget.update_pos()

    def draw(self):
        """
        This method draw all widgets surfaces in a surface and return it
        """
        self.surface = self.surface.convert().convert_alpha()
        for widget in self.widgets:
            self.surface.blit(widget.draw(),(widget.x,widget.y))
        return self.surface

    def add(self, widget, *args, **kwargs):
        """
        This function is used to add a widget in the conatiner
        """
        self.widgets.append(widget)
        if 'size' in kwargs or type(widget) == Button:
            if 'size' in kwargs:
                size = kwargs['size']
            else:
                size = (220,50)
            widget.set_size((optimize_size(size)[0], optimize_size(size)[1]))
        if 'margin' in kwargs:
            margin = kwargs['margin']
        else:
            margin = optimize_size((0, 10))[1]
        if self.orientation:
            widget.margin = margin*config.general['WIDTH']/800
        else:
            widget.margin = margin*config.general['HEIGHT']/480
        if 'margin_left' in kwargs:
            widget.margin_left = kwargs['margin_left']*config.general['WIDTH']/800
        if 'align' in kwargs:
            widget.align(kwargs['align'])
        self.update_size()
        self.update_pos()
    

class HBox(Container):
    """
    A widget which is able to contain others widgets and align them horizontally
    """

    def __init__(self):
        self.init()
        self.widgets = []
        self.orientation = True


class VBox(Container):
    """
    A widget which is able to contain others widgets and align them vertically
    """

    def __init__(self):
        self.init()
        self.widgets = []
        self.orientation = False