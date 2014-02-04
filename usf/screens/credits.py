################################################################################
# copyright 2010 Lucas Baudin <xapantu@gmail.com>                              #
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
The Credit screen.

'''

import os
from usf.screens import Screen
from usf import CONFIG

from usf.widgets.box import VBox
from usf.widgets.button import Button
from usf.widgets.paragraph import Paragraph

from usf.translation import _

class Credits(Screen):

    def init(self):
        padding = CONFIG.general.HEIGHT / 10   # 10 percent of screen height

        self.name = (_("credit"))
        self.add(VBox())

        credits_text = open(
            os.path.join(CONFIG.system_path, 'CREDITS')
            , 'r'
        ).readlines()

        self.widget.add(
            Paragraph(credits_text),
            size=(
                CONFIG.general.WIDTH - padding,
                CONFIG.general.HEIGHT - padding
            ),
            margin=padding
        )

        self.widget.add(Button(_('Back')), margin=55)

    def callback(self, action):
        if action.text == _('Back'):
            return {'goto': 'back'}
