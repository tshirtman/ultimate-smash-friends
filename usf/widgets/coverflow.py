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
import os

from widget import Widget, get_scale, optimize_size
from usf import loaders
from usf.font import fonts
config = loaders.get_config()

class Coverflow(Widget):

    def __init__(self, values):
        self.values = values
        self.init()

    def init(self):
        self.foreground = loaders.image(os.path.join(config.sys_data_dir,
                                                "gui",
                                                config.general['THEME'],
                                                "coverflow",
                                                "foreground.png"),
                                        scale=(self.width, self.height))[0]

        self.main_frame = loaders.image(os.path.join(config.sys_data_dir,
                                                "gui",
                                                config.general['THEME'],
                                                "coverflow",
                                                "frame.png"),
                                        scale=(self.sizex(195), self.sizey(120)))[0]

        self.frame = loaders.image(os.path.join(config.sys_data_dir,
                                                "gui",
                                                config.general['THEME'],
                                                "coverflow",
                                                "frame.png"),
                                        scale=(self.sizex(137), self.sizey(86)))[0]

        self.surface = pygame.surface.Surface((self.width, self.height))
        self.index = 0
        self.previous()

    def draw(self):
        self.surface = self.surface.convert().convert_alpha()
        pos = self.width/2 - self.frame.get_width()/2

        #main frame
        self.surface.blit(self.main_frame, (pos, self.sizey(60)))
        self.surface.blit(loaders.image(self.values[self.index][1],
                                       scale=(self.main_frame.get_width(), self.main_frame.get_height())
                                       )[0],
                         (pos, self.sizey(60)))
        pos += self.main_frame.get_width()

        for i in range(self.index + 1, len(self.values)):
            self.surface.blit(self.frame, (pos, self.sizey(82)))
            self.surface.blit(loaders.image(self.values[i][1], scale=(self.frame.get_width(), self.frame.get_height()))[0],
                 (pos, self.sizey(82)))
            pos += self.frame.get_width()
        #we need 3 image at right at least
        if (self.index + 1) - len(self.values) < 3:
            for i in range(0, 3 - (len(self.values) - (self.index + 1))):
                self.surface.blit(self.frame, (pos, self.sizey(82)))
                self.surface.blit(loaders.image(self.values[i][1], scale=(self.frame.get_width(), self.frame.get_height()))[0],
                     (pos, self.sizey(82)))
                pos += self.frame.get_width()

        #at left now
        pos = self.width/2 - self.frame.get_width()/2 - self.frame.get_width()*3
        for i in range(self.index - 3, self.index):
            self.surface.blit(self.frame, (pos, self.sizey(82)))
            self.surface.blit(loaders.image(self.values[i][1], scale=(self.frame.get_width(), self.frame.get_height()))[0],
                 (pos, self.sizey(82)))
            pos += self.frame.get_width()

        self.surface.blit(self.foreground, (0,0))
        return self.surface
    
    def sizex(self, x):
        return x*self.width/800

    def sizey(self, y):
        return y*self.height/340
    
    def next(self):
        if self.index - 1 > 0:
            self.index -= 1
        else:
            self.index = len(self.values) - 1
    def previous(self):
        if self.index + 1 < len(self.values) - 1:
            self.index += 1
        else:
            self.index = 0
