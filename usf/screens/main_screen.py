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

'''
The main screen of the Gui, the first one shown to the user when game is
started.

'''
import pygame

from usf.translation import _
from usf.screens.screen import Screen
from usf.widgets.box import VBox
from usf.widgets.button import Button


class MainScreen(Screen):
    def init(self):
        self.name = "ultimate smash friends"
        self.add(VBox())

        self.widget.add(Button(_('Local Game')))
        self.widget.add(Button(_('Network Game')))
        self.widget.add(Button(_('Configure')))
        self.widget.add(Button(_('Credits')))
        self.widget.add(Button(_('Quit')))

    def callback(self, action):
        if action.text == _('Local Game'):
            return {'goto': 'characters'}
        if action.text == _('Network Game'):
            return {'goto': 'network'}
        if action.text == _('Configure'):
            return {'goto': 'configure'}
        if action.text == _('Credits'):
            return {'goto': 'about'}
        if action.text == _('Quit'):
            pygame.event.post( pygame.event.Event(pygame.QUIT) )

