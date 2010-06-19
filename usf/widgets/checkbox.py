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


class CheckBox(Widget):

    def __init__(self):
        #save the path to scale it later -> maybe it is bad 
        #for performance, FIXME
        self.path = 'gui'  + os.sep + config.general['THEME'] \
                     + os.sep + 'checkbox_empty.png' 
        self.path_checked = 'gui'  + os.sep + config.general['THEME'] \
                     + os.sep + 'checkbox_full.png'
        self.init()
        self.set_size((optimize_size((25,25))[0], optimize_size((25,25))[1]))
        self.state = False
        self.checked = False

    def init(self):
        pass
        
    def set_size(self, (w,h)):
        self.height = h
        self.width = w
        self.surface = loaders.image(config.sys_data_dir +  os.sep + self.path,
                    scale=(w, h)
                    )[0]
        self.surface_checked = loaders.image(config.sys_data_dir + os.sep +
                    self.path_checked,
                    scale=(w, h)
                    )[0]

    def handle_mouse(self,event):
        if self.state == True:
            event.dict['pos'] = (event.dict['pos'][0] - self.parentpos[0] - self.x,
                                 event.dict['pos'][1] - self.parentpos[1] - self.y)
        if (0 < event.dict['pos'][0] < self.width and
            0 < event.dict['pos'][1] < self.height and
            event.type == pygame.MOUSEBUTTONUP):
            if self.checked:
                self.checked =False
            else:
                self.checked = True
            self.state = True
            return self,False
        self.state = False
        return False,False

    def draw(self):
        if self.checked:
            return self.surface_checked
        else:
            return self.surface

    def get_value(self):
        return self.checked
    def set_value(self, value):
        self.checked = value
