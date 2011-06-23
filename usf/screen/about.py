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

from screen import Screen
from usf import loaders

from usf.widgets.box import VBox
from usf.widgets.button import Button
from usf.widgets.paragraph import Paragraph

from usf.translation import _

class About(Screen):

    def init(self):
        self.set_name(_("about"))
        self.add(VBox())

        self.widget.add(Paragraph('CREDITS'),
                size=(
                    490*loaders.get_config().general["WIDTH"]/800,
                    300*loaders.get_config().general["HEIGHT"]/600))

        self.widget.add(Button(_('Back')),
                        margin=55)

    def callback(self, action):
        if action.text == _('Back'):
            return "goto:back"
