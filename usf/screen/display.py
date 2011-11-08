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
'''
This module profide the display configuration screen (resolution,
fullscreen, display fps...)

'''

from usf.screen.screen import Screen
from usf.widgets.box import VBox
from usf.widgets.label import Label
from usf.widgets.checkbox_text import TextCheckBox
from usf.widgets.spinner import Spinner
from usf.widgets.slider import Slider
from usf.widgets.button import Button
from usf.translation import _
from usf import loaders
import pygame

CONFIG = loaders.get_config()


class Display(Screen):

    def init(self):
        self.add(VBox())
        self.set_name(_("display configuration"))
        modes = []
        for resolution in pygame.display.list_modes():
            if resolution[0] >= 800:
                modes.append(str(resolution[0]) + "x" + str(resolution[1]))
        modes.reverse()
        self.resolution = Spinner(modes, 170)
        self.resolution.set_value(str(CONFIG.general.WIDTH) + 'x'
                                    + str(CONFIG.general.HEIGHT))

        self.widget.add(Label(_('Screen resolution (requires a restart):')))
        self.widget.add(self.resolution)

        self.fullscreen = TextCheckBox(_('Fullscreen:'))

        self.fullscreen.set_value(CONFIG.general.FULLSCREEN)
        self.widget.add(self.fullscreen)
        self.widget.add(Label(_('Zoom sharpness:')), margin=25)
        zoom = Slider('zoom_sharpness')
        self.widget.add(zoom, margin=10, size=(220, 30))
        zoom.set_value(CONFIG.general.ZOOM_SHARPNESS/5)

        self.fps = TextCheckBox(_('Show FPS:'))

        self.fps.set_value(CONFIG.general.SHOW_FPS)
        self.widget.add(self.fps, margin=25)

        self.widget.add(Button(_('Back')), margin=30)

    def callback(self, action):
        if action == self.resolution:
            value = action.get_value()
            CONFIG.general.WIDTH = int(value.split('x')[0])
            CONFIG.general.HEIGHT = int(value.split('x')[1])
        if action == self.fullscreen:
            pygame.display.toggle_fullscreen()
            if CONFIG.general.FULLSCREEN:
                CONFIG.general.FULLSCREEN = False
            else:
                CONFIG.general.FULLSCREEN = True
        if action == self.fps:
            if CONFIG.general.SHOW_FPS:
                CONFIG.general.SHOW_FPS = False
            else:
                CONFIG.general.SHOW_FPS = True
        if action.text == 'zoom_sharpness':
            CONFIG.general.ZOOM_SHARPNESS = (action.get_value()+1)*5
        if action.text == _('Back'):
            return "goto:back"

        CONFIG.write()

