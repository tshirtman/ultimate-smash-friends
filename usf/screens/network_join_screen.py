################################################################################
# copyright 2010 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
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

from usf.screens.screen import Screen
from usf.widgets.box import VBox
from usf.widgets.label import Label
from usf.widgets.button import Button
from usf.widgets.text_entry import TextEntry
from usf.translation import _


class NetworkJoinScreen(Screen):
    def init(self):
        self.name = "ultimate smash friends"
        self.add(VBox())

        self.widget.add(Label('Address of server:'))
        self.ip = TextEntry('X.X.X.X')
        self.widget.add(self.ip)
        self.widget.add(Button(_('Join game')))
        self.widget.add(Button(_('Back')), margin=30)

    def callback(self, action):
        if action.text == _('Join game'):
            # TODO: disable button

            # TODO: start a connection attempt at self.ip

            # if succeed, go to shared conf screen
            return 'goto:network_game_conf_screen'

        if action.text == _('Back'):
            return "goto:back"

