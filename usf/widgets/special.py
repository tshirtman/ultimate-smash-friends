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


class KeyboardWidget(Widget):

    def __init__(self, value):
        self.value = value
        exec("self.letter = pygame.key.name(pygame." + self.value + ").upper()")
        self.font =  fonts['mono']['25']
        self.set_size(optimize_size((35, 35)))
        self.state = False
        self.focus = False

    def init(self):
        self.background = loaders.image(config.sys_data_dir +
            os.sep + "gui" + os.sep + config.general['THEME'] + os.sep
            + "keyboard.png", scale=(self.width,self.height))[0]
        self.background_hover = loaders.image(config.sys_data_dir +
            os.sep + "gui" + os.sep + config.general['THEME'] + os.sep
            + "keyboard_hover.png", scale=(self.width,self.height))[0]

    def set_size(self, (w, h)):
        self.height = h
        self.width = w
        self.init()

    def draw(self):
        if self.state or self.focus:
            return loaders.image_layer(self.background_hover,
                loaders.text(self.letter, self.font))
        else:
            return loaders.image_layer(self.background,
                loaders.text(self.letter, self.font))

    def handle_mouse(self,event):
        if self.focus:
            return False, self
        if event.type == pygame.MOUSEBUTTONUP:
            self.state = False
            self.focus = True
            return False,self
        if self.state == True:
            event.dict['pos'] =(event.dict['pos'][0] - self.parentpos[0]-self.x, event.dict['pos'][1] - self.parentpos[1] - self.y)
        if 0 < event.dict['pos'][0] < self.width and 0 < event.dict['pos'][1] < self.height:
            self.state = True
            return False,self
        self.state = False
        return False,False

    def handle_keys(self, event):
        if self.focus:
            if event.type == pygame.KEYDOWN:
                self.letter = pygame.key.name(event.dict['key']).upper()
                self.value = config.reverse_keymap(event.dict['key'])
                self.focus = False
                self.state = False
                return self, False
            return self, False
        return False, False

    def get_value(self):
        return self.value
