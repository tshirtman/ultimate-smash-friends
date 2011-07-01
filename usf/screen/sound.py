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

from usf.screen.screen import Screen
from usf.widgets.box import VBox
from usf.widgets.slider import Slider
from usf.widgets.label import Label
from usf.widgets.button import Button
from usf.translation import _

from usf.loaders import get_config

CONFIG = get_config()


class Sound(Screen):
    def init(self):
        self.add(VBox())
        self.widget.add(Label(_('Sound and effects')))
        sound = Slider('sound_slider')
        self.widget.add(sound, margin=10, size=(220, 30))
        self.widget.add(Label(_('Music')))
        music = Slider('music_slider')
        self.widget.add(music, size=(220, 30))

        music.set_value(CONFIG.audio['MUSIC_VOLUME'])
        sound.set_value(CONFIG.audio['SOUND_VOLUME'])
        self.widget.add(Button(_('Back')), margin=30)

    def callback(self, action):
        if action.text == 'music_slider':
            CONFIG.audio['MUSIC_VOLUME'] = action.get_value()
        if action.text == 'sound_slider':
            CONFIG.audio['SOUND_VOLUME'] = action.get_value()
        if action.text == _('Back'):
            return "goto:back"
