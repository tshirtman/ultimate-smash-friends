################################################################################
# copyright 2009-2011 Gabriel Pettier <gabriel.pettier@gmail.com>              #
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
The Sound configuration screen. to manage music and SFX volume.

'''
from usf import CONFIG
from usf.translation import _
from usf.screens.screen import Screen
from usf.widgets.box import VBox
from usf.widgets.button import Button
from usf.widgets.checkbox_text import TextCheckBox
from usf.widgets.label import Label
from usf.widgets.slider import Slider


class Audio(Screen):
    def init(self):
        # create widgets
        self.add(VBox())
        self.name = _('Audio Options')

        self.sound = TextCheckBox(_('Sound'))
        self.sound_volume = Slider('Sound Volume')
        self.music = TextCheckBox(_('Music'))
        self.music_volume = Slider('Music Volume')

        # set values from config
        self.sound.set_value(CONFIG.audio.SOUND)
        self.sound_volume.set_value(CONFIG.audio.SOUND_VOLUME)
        self.music.set_value(CONFIG.audio.MUSIC)
        self.music_volume.set_value(CONFIG.audio.MUSIC_VOLUME)

        # add widgets
        self.widget.add(self.sound)
        self.widget.add(self.sound_volume, margin=10, size=(220, 30))
        self.widget.add(self.music)
        self.widget.add(self.music_volume, margin=10, size=(220, 30))
        self.widget.add(Button(_('Back')), margin=30)
                
    def callback(self, action):
        if action.text == 'Music Volume':
            CONFIG.audio.MUSIC_VOLUME = action.get_value()
        if action.text == 'Sound Volume':
            CONFIG.audio.SOUND_VOLUME = action.get_value()
        if action.text == 'Music':
            if CONFIG.audio.MUSIC:
                CONFIG.audio.MUSIC = False
            else:
                CONFIG.audio.MUSIC = True
        if action.text == 'Sound':
            if CONFIG.audio.SOUND:
                CONFIG.audio.SOUND = False
            else:
                CONFIG.audio.SOUND = True
        if action.text == _('Back'):
            return {'goto': 'back'}

        CONFIG.write()
