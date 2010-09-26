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
        self.add(widgets.VBox())
        self.set_name(_("screen configuration"))
        modes = []
        for resolution in pygame.display.list_modes():
            if resolution[0] >= 800:
                modes.append(str(resolution[0]) + "x" + str(resolution[1]))
        modes.reverse()
        self.resolution = widgets.Spinner(modes, 170)
        self.fullscreen = widgets.CheckBox()
        
        if config.general['FULLSCREEN']:
            self.fullscreen.set_value(True)
        self.resolution.set_value(str(config.general['WIDTH']) + 'x'
                                    + str(config.general['HEIGHT']))
        
        self.widget.add(widgets.Label(_('Screen resolution (requires a restart):')),
                        margin=50)
        self.widget.add(self.resolution, margin=10)
        fullscreen_hbox = widgets.HBox()
        
        fullscreen_hbox.add(widgets.Label(_('Fullscreen:')))
        fullscreen_hbox.add(self.fullscreen, margin=50)
        self.widget.add(fullscreen_hbox, margin=25)
        
        self.widget.add(widgets.Label(_('Zoom sharpness:')), margin=25)
        zoom = widgets.Slider('zoom_sharpness')
        self.widget.add(zoom, margin=10, size=(220, 30))
        zoom.set_value(config.general['ZOOM_SHARPNESS']/5)

        self.fps = widgets.CheckBox()
        
        if config.general['SHOW_FPS']:
            self.fps.set_value(True)
        fps_hbox = widgets.HBox()
        
        fps_hbox.add(widgets.Label(_('Show FPS:')), margin=0)
        fps_hbox.add(self.fps, margin=50)
        self.widget.add(fps_hbox, margin=25)

        self.widget.add(widgets.Button(_('Back')), margin=30)
        
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
        if action == self.fps:
            if config.general['SHOW_FPS']:
                config.general['SHOW_FPS'] = False
            else:
                config.general['SHOW_FPS'] = True
        if action.text == 'zoom_sharpness':
            config.general['ZOOM_SHARPNESS'] = (action.get_value()+1)*5
        if action.text == _('Back'):
            return "goto:back"


