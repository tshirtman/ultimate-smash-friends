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
The screen to configure the Keyboard.

'''
from os.path import join

from usf import CONFIG
from usf.translation import _
from usf.widgets.box import VBox, HBox
from usf.widgets.button import Button
from usf.widgets.image import Image
from usf.widgets.label import Label
from usf.screens.screen import Screen
from usf.widgets.special import KeyboardWidget


class Keyboard(Screen):

    def init(self):
        self.add(VBox())
        self.name = _("Keyboard Options")

        hbox = HBox()
        hbox.add(Label(" "), size=(80, 20))
        for img in ['left.png', 'right.png', 'top.png', 'bottom.png']:
            hbox.add(Image(join(
                'gui',
                CONFIG.general.THEME,
                img)),
                size=(40, 30),
                margin=30)


        hbox.add(Label('B'), size=(30, 40), margin=40, align="center")
        hbox.add(Label('A'), size=(30, 40), margin=40, align="center")
        hbox.add(Label(_("Shield")), size=(60, 40), margin=10, align="center")
        self.widget.add(hbox)
        actions = ['Left', 'Right', 'Up', 'Down', 'A', 'B', 'Shield']

        #one iteration per player
        for i in xrange(1, 5):
            hbox = HBox()
            hbox.add(Label('Player ' + str(i + 1)), size=(80, 50))

            for action in actions:
                w = KeyboardWidget(getattr(CONFIG.keyboard, 
                                       "PL{0}_{1}".format(i, action.upper())))
                w.set_id("PL{0}_{1}".format(i, action.upper()))
                hbox.add(w, size=(40, 40), margin=30)

            self.widget.add(hbox)

        self.widget.add(Button(_('Back')), align="center")
        self.widget.update_pos()

    def callback(self, action):
        if hasattr(action, 'letter'):
            setattr(CONFIG.keyboard, action.get_id(), action.get_value())

        if action.text == _('Back'):
            return {'goto': 'back'}

        CONFIG.write()
