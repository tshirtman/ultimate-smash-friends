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

from box import HBox


class Spinner(HBox):

    def __init__(self, values, width=100):
        self.parentpos = (0,0)
        self.extend = False
        self.values = values
        self.orientation = True
        self.index = 0
        self.center_width = width
        self.init()
        self.state = False
        self.height = optimize_size((250,30))[1]
        self.width = optimize_size((25,30))[0]*2 + optimize_size((self.center_width,30))[0]

    def init(self):
        self.surface = pygame.Surface((self.width,self.height))
        self.widgets = []
        self.left_arrow = ImageButton("gui" + os.sep + config.general['THEME'] + os.sep + "spinner_left.png",
            "gui" + os.sep + config.general['THEME'] + os.sep + "spinner_left_hover.png")
        self.left_arrow.set_size(optimize_size((25,30)))
        self.add(self.left_arrow, margin = 0)
        self.center = Label(self.values[self.index],
            background="gui" + os.sep + config.general['THEME'] + os.sep + "spinner_center.png",
            height=optimize_size((self.center_width,30))[1],
            width=optimize_size((self.center_width,30))[0],
            margin=optimize_size((10,0))[0])
        self.add(self.center, margin = 0)
        self.right_arrow = ImageButton("gui" + os.sep + config.general['THEME'] + os.sep + "spinner_right.png",
            "gui" + os.sep + config.general['THEME'] + os.sep + "spinner_right_hover.png")
        self.right_arrow.set_size(optimize_size((25,30)))
        self.add(self.right_arrow, margin = 0)
        self.update_pos()
        self.update_size()

    def handle_mouse(self, event):
        if self.state:
            event.dict['pos'] =(event.dict['pos'][0] - self.parentpos[0] - self.x,
                                event.dict['pos'][1] - self.parentpos[1] - self.y)
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        self.left_arrow.state = False
        self.right_arrow.state = False
        if 0 < event.dict['pos'][0] < self.width and 0 < event.dict['pos'][1] < self.height:
            self.state = True
            for widget in self.widgets:
                if widget.x < x < widget.x+widget.width and widget.y < y < widget.y+widget.height:
                    if widget == self.left_arrow or widget == self.right_arrow:
                        widget.state = True
                        if event.type == pygame.MOUSEBUTTONUP:
                            if widget == self.right_arrow:
                                if self.index < len(self.values)-1:
                                    self.index +=1
                            else:
                                if self.index > 0:
                                    self.index -=1
                            self.text = self.values[self.index]
                            self.center.setText(self.text)
                            return (self,False)
            return False, self
        self.state = False
        return (False,False)

    def get_value(self):
        return self.values[self.index]

    def getIndex(self):
        return self.index

    def setIndex(self, index):
        self.index=index
        self.text = self.values[self.index]
        self.center.setText(self.text)

    def set_value(self, value):
        try:
            self.setIndex(self.values.index(value))
        except:
            pass

