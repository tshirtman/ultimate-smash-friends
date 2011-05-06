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


class Slider(Widget):

    def __init__(self, text):
        self.focusable = False
        self.text = text
        self.keyboard = False
        self.space = 0
        self.parentpos = (0, 0)
        self.extend = False
        self.value = 0
        self.orientation = False
        self.init()
        self.index = 0
        self.state = False
        self.height = optimize_size((250, 25))[1]
        self.width = optimize_size((25, 25))[0] + optimize_size((25, 25))[0] + optimize_size((100, 25))[0]

    def init(self):
        self.background= loaders.image(join(config.sys_data_dir, 'gui',
                config.general['THEME'], 'slider_background.png'),
            scale=(self.width, self.height))[0]
        self.center= loaders.image(join(config.sys_data_dir, 'gui',
                config.general['THEME'], 'slider_center.png'),
            scale=(self.height, self.height))[0]
        self.center_hover= loaders.image(join(config.sys_data_dir, 'gui',
                config.general['THEME'], 'slider_center_hover.png'),
            scale=(self.height, self.height))[0]
        self.screen = pygame.display.get_surface()

    def handle_mouse(self, event):
        if not self.keyboard:
            if self.state:
                event.dict['pos'] =(event.dict['pos'][0] - self.parentpos[0] - self.x,
                                    event.dict['pos'][1] - self.parentpos[1] - self.y)
            x = event.dict['pos'][0]
            y = event.dict['pos'][1]
            if self.state:
                if event.type == pygame.MOUSEBUTTONUP:
                    self.state = False
                    return False, False
                elif event.type == pygame.MOUSEMOTION and x -self.space >0 and x - self.space + self.height < self.width:
                    self.value = x - self.space
                elif event.type == pygame.MOUSEMOTION  and x -self.space >0:
                    self.value = self.width-self.height
                elif event.type == pygame.MOUSEMOTION  and x - self.space + self.height < self.width:
                    self.value = 0
                return self, self
            if 0 < x < self.width and 0 < y < self.height:
                if self.value < x and x < self.value + self.height:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        #to adjust the position of the slider
                        self.space = x - self.value

                        self.state = True
                        return self, self
                return False, False
            self.state = False
        else:
            self.state = False
            self.keyboard = False
        return (False, False)

    def get_value(self):
        return self.value*100/(self.width - self.height)

    def set_value(self, value):
        self.value = value*(self.width - self.height)/100

    def draw(self):
        if self.state:
            surf = loaders.image_layer(self.background, self.center_hover, (self.value, 0))
        else:
            surf = loaders.image_layer(self.background, self.center, (self.value, 0))
        self.screen.blit(surf, (self.parentpos[0] + self.x, self.parentpos[1] + self.y))

    def handle_keys(self, event):
        self.keyboard = True
        if (event.dict["key"] == pygame.K_DOWN or event.dict["key"] == pygame.K_UP) and not self.state:
            self.state = True
            return False, self

        if event.dict["key"] == pygame.K_LEFT:
            if self.get_value() > 10:
                self.set_value(self.get_value() - 10)
            else:
                self.set_value(0)
            return self, self

        if event.dict["key"] == pygame.K_RIGHT:
            if self.get_value() < 90:
                self.set_value(self.get_value() + 10)
            else:
                self.set_value(100)
            return self, self

        self.state = False
        return False, False

