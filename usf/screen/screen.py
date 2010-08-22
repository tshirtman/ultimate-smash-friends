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

# Our modules
from usf.config import Config
config = Config()
from usf.font import fonts
from usf import loaders

class Screen(object):

    def __init__(self, name, screen):
        self.set_name(name)
        self.screen = screen
        self.init()
        self.widget.update_size()
        self.widget.update_pos()

    def add(self, widget):
        self.widget = widget
        #define the position and the size of the top-level widget
        self.widget.set_size((config.general['WIDTH'],config.general['HEIGHT']))
        self.widget.x = 0
        self.widget.y = 70*config.general['HEIGHT']/480
        self.widget.update_size()
        self.widget.update_pos()

    def update(self):
        self.screen.blit(loaders.text(self.name, fonts['mono']['15']), (self.indent_title,10))
        self.screen.blit(self.widget.draw(), (0,self.widget.y))

    def load(self):
        loaders.text(self.name, fonts['mono']['15'])
        self.widget.draw()

    def init(self):
        pass

    def callback(self, action):
        pass
        
    def set_name(self, name):
        self.name = name.replace('_', ' ')  
        self.indent_title = config.general['WIDTH']/2 - loaders.text(self.name, fonts['mono']['15']).get_width()/2
