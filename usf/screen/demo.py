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
from usf import loaders
from os.path import join
config = loaders.get_config()

class demo(Screen):

    def init(self):
        self.add(widgets.VBox())
        basename = join(config.sys_data_dir, "test", "")
        self.widget.add(widgets.Coverflow([["First",  join(config.sys_data_dir, "items", "item-heal.png")],
                                           ["Second", basename + "2.png"],
                                           ["Third", basename + "3.png"],
                                           ["Fourth", basename + "4.png"],
                                           ["Fifth", basename + "5.png"],
                                           ["Sixth", basename + "6.png"]]), size=(800, 275))
