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
Some Box widgets as base for the GUI classes

'''

from usf.widgets.widget import Widget, optimize_size
from usf.widgets.button import Button

from usf import loaders
CONFIG = loaders.get_config()


class Container(Widget):
    """
    This widget is never used directly, it is used to be a base for the HBox
    and VBox widget.
    """
    focusable = True

    def __init__(self, orientation):
        super(Container, self).__init__()
        self.orientation = orientation
        self.widgets = []

    def update_size(self):
        """
        This function is used to update the container size after adding a
        widget.
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
            if self.orientation:
                sizex += widget.margin
            else:
                sizey += widget.margin
            #widget.init() #XXX probably to replace by something :/

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
            widget.parentpos = (
                    self.parentpos[0] + self.x, self.parentpos[1] + self.y)
            widget.update_size()
            widget.update_pos()

    def draw(self):
        """
        This method draw all widgets surfaces in a surface and return it
        """
        for widget in self.widgets:
            widget.draw()

    def add(self, widget, **kwargs):
        """
        This function is used to add a widget in the conatiner
        """
        self.current_focus = -1
        self.widgets.append(widget)
        if 'size' in kwargs or type(widget) == Button:
            if 'size' in kwargs:
                size = kwargs['size']
            else:
                size = (220, 50)
            widget.set_size((size[0], size[1]))
        if 'margin' in kwargs:
            margin = kwargs['margin']
        else:
            margin = optimize_size((0, 10))[1]
        if self.orientation:
            widget.margin = margin*CONFIG.general['WIDTH']/800
        else:
            widget.margin = margin*CONFIG.general['HEIGHT']/480
        if 'margin_left' in kwargs:
            widget.margin_left = kwargs['margin_left']
        if 'align' in kwargs:
            if not self.orientation and kwargs['align'] == "center":
                widget.margin_left = self.width/2 - widget.width/2
            #widget.set_align(kwargs['align'])
        self.update_size()
        self.update_pos()

    def handle_mouse(self, event):
        """
        This function is used for mouse events.
        """
        #print event.dict['pos']
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]

        for widget in self.widgets:
            if (
                    widget.x < x < widget.x+widget.width and
                    widget.y < y < widget.y+widget.height):
                event.dict['pos'] = (x-widget.x, y-widget.y)
                return widget.handle_mouse(event)

        return (False, False)

    def handle_keys(self, event):
        """
        This function is used for keyboard events.
        """


class HBox(Container):
    """
    A widget which is able to contain others widgets and align them
    horizontally.
    """

    def __init__(self):
        super(HBox, self).__init__(orientation=True)


class VBox(Container):
    """
    A widget which is able to contain others widgets and align them
    vertically.
    """

    def __init__(self):
        super(VBox, self).__init__(orientation=False)

