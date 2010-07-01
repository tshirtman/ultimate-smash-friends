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

from os.path import join

from screen import Screen
from usf import widgets
import copy
from usf.config import Config
config = Config()


class keyboard(Screen):

    def init(self):
        self.add(widgets.VBox())

        action_ = ['A', 'B', 'Shield']
        hbox = widgets.HBox()
        hbox.add(widgets.Label(" "), size=(80,20))
        hbox.add(widgets.Image(join('gui', config.general['THEME'], 'left.png')), size=(40,30), margin=30)
        hbox.add(widgets.Image(join('gui', config.general['THEME'], 'right.png')), size=(40,30), margin=30)
        hbox.add(widgets.Image(join('gui', config.general['THEME'], 'top.png')), size=(40,30), margin=30)
        hbox.add(widgets.Image(join('gui', config.general['THEME'], 'bottom.png')), size=(40,30), margin=30)
        hbox.add(widgets.Label('B'), size=(30,40), margin=40, align="center")
        hbox.add(widgets.Label('A'), size=(30,40), margin=40, align="center")
        hbox.add(widgets.Label(_("Shield")), size=(60,40), margin=10, align="center")
        self.widget.add(hbox, margin_left=80, margin=20)
        action_ = ['Left', 'Right', 'Up', 'Down', 'A', 'B', 'Shield']
        #one repetition by players
        for i in range (0, 4):
            hbox = widgets.HBox()
            hbox.add(widgets.Label('Player ' + str(i + 1)), size=(80,50))
            for action in action_:
                w = widgets.KeyboardWidget(config.keyboard['PL' + str(i + 1) + '_' + action.upper()])
                w.set_id('PL' + str(i + 1) + '_' + action.upper())
                hbox.add(w, size=(40,40), margin=30)
            self.widget.add(hbox, margin_left=80)
        self.widget.add(widgets.Button(_('Back')), margin_left=20, margin=30)

    def callback(self,action):
        if type(action) == widgets.KeyboardWidget:
            config.keyboard[action.get_id()] = action.get_value()
        if action.text == _('Back'):
            return "goto:back"
