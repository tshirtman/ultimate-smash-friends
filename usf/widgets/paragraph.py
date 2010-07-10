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
from os.path import join

from widget import Widget, get_scale, optimize_size
from usf import loaders
from usf.font import fonts
config = loaders.get_config()

from box import HBox


class Paragraph(Widget):

    def __init__(self, path):
        self.defil = 0
        self.state = False
        self.widgets = []
        self.orientation = True
        self.text = open(config.sys_data_dir + os.sep + 'text' + os.sep + path, 'r').readlines()
        self.text_height = loaders.text("", fonts['mono']['normal']).get_height()
        self.init()

    def init(self):
        self.surface = pygame.surface.Surface((self.width, self.height))
        self.surface_text = pygame.surface.Surface((self.width, len(self.text)*self.text_height))
        for i in range(len(self.text)):
            self.surface_text.blit(loaders.text(self.text[i], fonts['mono']['normal']), (0, self.text_height*i  ))

    def draw(self):
        self.surface = self.surface.convert().convert_alpha()
        self.surface.blit(self.surface_text, (0,-(self.defil*(self.surface_text.get_height()-self.height)/100)))
        self.surface.blit(loaders.image(join(config.sys_data_dir, "gui", config.general['THEME'], "sliderh_background.png"), scale=(self.width/10, self.height))[0], (self.width/10*9, 0))
        self.surface.blit(loaders.image(join(config.sys_data_dir, "gui", config.general['THEME'], "sliderh_background.png"), scale=(self.width/10, self.height/5))[0], (self.width/10*9, self.defil*(self.height - self.height/5)/100))
        return self.surface

    def handle_mouse(self,event):
        if self.state == True:
            #relative position
            event.dict['pos'] =(event.dict['pos'][0] - self.parentpos[0]-self.x,
                        event.dict['pos'][1] - self.parentpos[1] - self.y)
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        if event.type == pygame.MOUSEBUTTONUP:
            self.state = False
            return self,False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.dict['button'] == 4:
                if 0 <= self.defil - 5 <= 100:
                    self.defil -= 5
            if event.dict['button'] == 5:
                if 0 <= self.defil + 5 <= 100:
                    self.defil += 5
            if event.dict['button'] == 1:
                if self.width/10*9 < event.dict['pos'][0] < self.width and 0 < event.dict['pos'][1] < self.height:
                    self.state = True
                    return False,self
            self.state = False
            return False,False
        elif self.state and event.type == pygame.MOUSEMOTION:
            if 0 < y < self.height:
                self.defil = y * 100 / self.height
            elif y < 0:
                self.defil = 0
            else:
                self.defil = 100
            return False,self
        return False,False
