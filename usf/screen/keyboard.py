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
import copy
from usf.config import Config
config = Config()


class keyboard(Screen):

    def init(self):
        self.add(widgets.HBox())
        vbox = widgets.VBox()
        self.widget.add(vbox, margin=75)
        action_ = ['Left', 'Right', 'Up', 'Down', 'A', 'B', 'Shield'    ]
        hbox = widgets.HBox()
        hbox.add(widgets.Label(" "), size=(80,20))
        for action in action_:
            hbox.add(widgets.Label(action), size=(80,50))
        vbox.add(hbox, margin=100)
        #one repetition by players
        for i in range (0, 4):
            hbox = widgets.HBox()
            hbox.add(widgets.Label('Player ' + str(i + 1)), size=(80,50))
            for action in action_:
                w = widgets.KeyboardWidget(config.keyboard['PL' + str(i + 1) + '_' + action.upper()])
                w.set_id('PL' + str(i + 1) + '_' + action.upper())
                hbox.add(w, size=(70,35), margin=10)
            vbox.add(hbox)

    def callback(self,action):
        if action.text == 'Sounds and music':
            return "goto:sound"
        if action.text == 'Screen':
            return "goto:screen_screen" 
        if type(action) == widgets.KeyboardWidget:
            config.keyboard[action.get_id()] = action.get_value()
