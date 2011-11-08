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

import pygame
import os

from usf.widgets.widget import Widget
from usf import loaders
from usf import CONFIG


class Image(Widget):
    """
    An image widget which can be used as a base for others widgets like
    buttons.
    """

    def __init__(self, image):
        #save the path to scale it later
        super(Image, self).__init__()
        self.setImage(image)

        self.screen = pygame.display.get_surface()
        self.state = True

    def set_size(self, (w, h)):
        """
        Set the size of the image.
        /!\ The width and the height have to be the real value
        (not the value only for 800x480)
        """

        self.height = h
        self.width = w

    def setImage(self, path):
        """
        With this method, you can change the image.
        'CONFIG.system_path' will be added to 'path'
        """
        self.path = path

        self.surface = loaders.image(
                    CONFIG.system_path+
                    os.sep+
                    self.path, scale=(self.width, self.height))[0]

