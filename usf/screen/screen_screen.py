################################################################################
# copyright 2009 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
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

from screen import Screen
from usf import widgets
from usf.config import Config
import pygame
config = Config()

class screen_screen(Screen):
    def init(self):
        self.add(widgets.HBox())
        vbox = widgets.VBox()
        self.resolution = widgets.Spinner(['800x480', '1200x720', '1600x960'], 170)
        self.fullscreen = widgets.CheckBox()
        
        if config.general['FULLSCREEN']:
            self.fullscreen.set_value(True)
        self.resolution.set_value(str(config.general['WIDTH']) + 'x'
                                    + str(config.general['HEIGHT']))
        
        vbox.add(widgets.Label('Screen resolution :'), margin=150)
        vbox.add(self.resolution, margin=10)
        fullscreen_hbox = widgets.HBox()
        
        fullscreen_hbox.add(widgets.Label('Fullscreen :'))
        fullscreen_hbox.add(self.fullscreen, margin=50)
        vbox.add(fullscreen_hbox, margin=25)
        self.widget.add(vbox, margin=220)
        
    def callback(self,action):
        if action == self.resolution:
            value = action.get_value()
            config.general['WIDTH'] = int(value.split('x')[0])
            config.general['HEIGHT'] = int(value.split('x')[1])
        if action == self.fullscreen:
            pygame.display.toggle_fullscreen()
            if config.general['FULLSCREEN']:
                config.general['FULLSCREEN'] = False
            else:
                config.general['FULLSCREEN'] = True
