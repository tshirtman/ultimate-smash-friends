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

    def __init__(self):
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
                                                "main_frame.png"),
                                        scale=(self.sizex(195), self.sizey(120)))[0]

        self.frame = loaders.image(os.path.join(config.sys_data_dir,
                                                "gui",
                                                config.general['THEME'],
                                                "coverflow",
                                                "frame.png"),
                                        scale=(self.sizex(137), self.sizey(86)))[0]

        self.surface = pygame.surface.Surface((self.width, self.height))

    def draw(self):
        self.surface = self.surface.convert().convert_alpha()
        self.surface.blit(self.main_frame, (self.width/2 - self.main_frame.get_width()/2, self.sizey(60)))
        
        #right frame
        self.surface.blit(self.frame, (self.width/2 - self.main_frame.get_width()/2 - self.frame.get_width(), self.sizey(82)))

        #left frame
        self.surface.blit(self.frame, (self.width/2 + self.main_frame.get_width()/2, self.sizey(82)))

        #right right frame
        self.surface.blit(self.frame, (self.width/2 - self.main_frame.get_width()/2 - self.frame.get_width()*2, self.sizey(82)))

        #left left frame
        self.surface.blit(self.frame, (self.width/2 + self.main_frame.get_width()/2 + self.frame.get_width(), self.sizey(82)))
        
        self.surface.blit(self.foreground, (0, 0))
        return self.surface
    
    def sizex(self, x):
        return x*self.width/800

    def sizey(self, y):
        return y*self.height/340
