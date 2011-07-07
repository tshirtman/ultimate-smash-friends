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
Provide a widget to construct the Keyboard Configuration Interface.

'''

import pygame
import os

from usf.widgets.widget import Widget, optimize_size
from usf import loaders
from usf.font import fonts
from usf.config import reverse_keymap
CONFIG = loaders.get_config()


class KeyboardWidget(Widget):
    ''' actually it should be KeyWidget, if i get it correctly
    '''

    def __init__(self, value):
        super(KeyboardWidget, self).__init__()
        self.value = value
        try:
            self.letter = pygame.key.name(pygame.__dict__[self.value]).upper()
        except KeyError:
            self.letter = str(self.value)

        self.font = fonts['mono']['25']
        self.set_size(optimize_size((35, 35)))
        self.state = False
        self.focus = False

    def set_size(self, (w, h)):
        self.width = w
        self.height = h
        self.update()

    def update(self):
        self.background = loaders.image(
                os.path.join(
                    CONFIG.sys_data_dir, "gui",
                    CONFIG.general['THEME'],"keyboard.png"),
                scale=(self.width, self.height))[0]

        self.background_hover = loaders.image(
                os.path.join(
                    CONFIG.sys_data_dir,
                    "gui",
                    CONFIG.general['THEME'],
                    "keyboard_hover.png"),
                scale=(self.width, self.height))[0]

        text = loaders.text(self.letter, self.font)
        if text.get_width() > self.width:
            text = pygame.transform.smoothscale(
                    text, (
                        self.width,
                        self.width * text.get_height() / text.get_width()))

        posx = self.width/2 - text.get_width()/2
        posy = self.height/2 - text.get_height()/2
        self.surface = loaders.image_layer(self.background_hover,
                text, (posx, posy))
        self.surface_hover = loaders.image_layer(self.background,
                text, (posx, posy))
        self.screen = pygame.display.get_surface()

    def draw(self):
        if self.state or self.focus:
            self.screen.blit(
                    self.surface, (
                        self.parentpos[0] + self.x,
                        self.parentpos[1] + self.y))

        else:
            self.screen.blit(
                    self.surface_hover, (
                        self.parentpos[0] + self.x,
                        self.parentpos[1] + self.y))

    def handle_mouse(self, event):
        if self.focus:
            return False, self
        if event.type == pygame.MOUSEBUTTONUP:
            self.state = False
            self.focus = True
            return False, self
        if self.state:
            event.dict['pos'] = (
                    event.dict['pos'][0] - self.parentpos[0]-self.x,
                    event.dict['pos'][1] - self.parentpos[1] - self.y)

        if (
                0 < event.dict['pos'][0] < self.width and
                0 < event.dict['pos'][1] < self.height):
            self.state = True
            self.update()
            return False, self
        self.state = False
        return False, False

    def handle_keys(self, event):
        if self.focus:
            if event.type == pygame.KEYDOWN:
                self.letter = pygame.key.name(event.dict['key']).upper()
                self.value = reverse_keymap(event.dict['key'])
                self.focus = False
                self.state = False
                self.update()
                return self, False
            return self, False
        return False, False

    def get_value(self):
        return self.value
