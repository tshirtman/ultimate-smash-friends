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


'''
The Screen to choose the level to be played.

'''


#standard imports
from os.path import join
import os
import logging

#our modules
from usf.screen.screen import Screen
from usf.widgets.box import VBox
from usf.widgets.button import Button
from usf.widgets.coverflow import Coverflow

from usf import loaders
CONFIG = loaders.get_config()

from usf.translation import _

class Level(Screen):

    def init(self):
        self.add(VBox())

        coverflow_data = []
        #create a level image for every directory in the level directory.
        files = os.listdir(os.path.join( CONFIG.system_path, 'levels'))
        files.sort()

        for f in files:
            try:
                if 'level.xml' in os.listdir(
                        os.path.join(CONFIG.system_path, "levels", f)):
                    coverflow_data.append([])
                    coverflow_data[-1].append(f)
                    coverflow_data[-1].append(
                            join(
                                CONFIG.system_path,
                                "levels", f, "screenshot.png"))
            except:
                logging.debug(str(f) +" is not a valid level.")

        self.coverflow = Coverflow(coverflow_data)
        self.widget.add(self.coverflow, size=(800, 275))
        self.widget.add(Button(_('Go !')), margin_left=290)
        self.widget.add(
                Button(_('Back')),
                size=(150, 40),
                margin_left=20,
                margin=20)

    def get_level(self):
        return self.coverflow.get_value()

    def callback(self, action):
        if action.text == _('Go !'):
            return "game:new"

        if action.text == _('Back'):
            return "goto:back"
