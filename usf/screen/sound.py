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
import widgets
from config import Config

config = Config()

class sound(Screen):
    def init(self):
        self.add(widgets.HBox())
        vbox = widgets.VBox()
        self.widget.add(vbox, margin=220)
        vbox.add(widgets.Label('Sound'), margin=150)
        sound = widgets.Slider('sound_slider')
        vbox.add(sound, margin=10, size=(360,40))
        vbox.add(widgets.Label('Music'), margin=10)
        music = widgets.Slider('music_slider')
        vbox.add(music, margin=10, size=(360,40))
        
        music.set_value(config.audio['MUSIC_VOLUME'])
        sound.set_value(config.audio['SOUND_VOLUME'])
    def callback(self,action):
        if action.text == 'music_slider':
            config.audio['MUSIC_VOLUME'] = action.get_value()
        if action.text == 'sound_slider':
            config.audio['SOUND_VOLUME'] = action.get_value()
