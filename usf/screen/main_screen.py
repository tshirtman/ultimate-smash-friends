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
import widgets
import copy
class main_screen(Screen):
    def init(self):
        self.add(widgets.HBox(False))
        hbox = widgets.HBox(False)
        #vbox2 = widgets.HBox(False)
        #hbox2 = widgets.HBox(False)
        self.widget.add(hbox)
        #self.widget.add(hbox2)
        #self.widget.add(vbox2)
        #hbox.add(widgets.Label('gui/icon.png'))
        hbox.add(widgets.Image('gui/icon.png'))
        #hbox.add(widgets.Image('gui/icon.png'))
        #hbox.add(widgets.Image('gui/icon.png'))
        hbox.add(widgets.Image('gui/icon.png'))
        hbox.add(widgets.Image('gui/icon.png'))
        hbox.add(widgets.Image('gui/icon.png'), margin=100)
        #print hbox.widgets
        #print hboxa.widgets
        #vbox2.add(widgets.Image('gui/icon.png'))
        self.widget.update_size()
        self.widget.update_pos()
