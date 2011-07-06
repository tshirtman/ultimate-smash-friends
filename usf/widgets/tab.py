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
#from widget import Widget, get_scale, optimize_size
#from usf import loaders
#from usf.font import fonts

from box import HBox, VBox


class Tab(VBox):
    """
    /!\ This widget isn't finished at all
    TODO
    """
    def __init__(self):
        self.init()
        self.widgets = []
        self.orientation = False
        self.tab = TabBar()
        self.add(self.tab)
        self.tab_list = []
        self.tab_content = []

    def add_tab(self, tab, box):
        self.tab.add(tab)
        self.tab_list.append(tab)
        box_content = HBox()
        box_content.add(box)
        self.tab_content.append(box_content)
        if len(self.tab_content) == 1:
            self.add(box_content)
            print self.widgets.index(box_content)
        self.update_pos()
        self.update_size()

    def handle_mouse(self, event):
        try:
            self.widgets
        except:
            self.widgets = []

        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        for widget in self.widgets:
            if widget.x < x < widget.x+widget.width and widget.y < y < widget.y+widget.height:
                event.dict['pos'] = (x-widget.x, y-widget.y)
                if widget == self.tab:
                    for wid in widget.widgets:
                        wid.state=False
                    widget_ = widget.handle_mouse(event)
                    if event.type == pygame.MOUSEBUTTONUP:
                        self.widgets[1] = self.tab_content[self.tab_list.index(widget_)]
                        self.update_pos()
                        self.update_size()
                    elif widget_:
                        widget_.state=True
                else:
                    return widget.handle_mouse(event)
                break

        return (False, False)


class TabBar(HBox):
    """
    Used in the Tab widget
    """

    def handle_mouse(self, event):
        try:
            self.widgets
        except:
            self.widgets = []
        #print event.dict['pos']
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        for widget in self.widgets:
            if widget.x < x < widget.x+widget.width and widget.y < y < widget.y+widget.height:
                return widget
                break

