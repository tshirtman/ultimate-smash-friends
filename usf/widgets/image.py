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
from widget import Widget, get_scale, optimize_size
from usf import loaders
from usf.font import fonts


class Image(Widget):
    """
    An image widget which can be used as a base for others widgets like buttons
    """

    def init(self):
        pass

    def __init__(self, image, *args, **kwargs):
        #save the path to scale it later -> maybe it is bad for performance, FIXME
        self.path = image
        if "size" in kwargs:
            size = optimize_size(kwargs['size'])
        else:
            size = get_scale(loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    image)[0])
                    
        self.init()
        self.set_size((size[0], size[1]))
        self.state = True

    def set_size(self, (w,h)):
        """
        Set the size of the image.
        /!\ The width and the height have to be the real value
        (not the value only for 800x480)
        """

        self.height = h
        self.width = w
        self.surface = loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    self.path, scale=(w,h)
                    )[0]

    def draw(self):
        return self.surface

    def setImage(self,path):
        """
        With this method, you can change the image. 'config.sys_data_dir' will be added to 'path'
        """
        self.path = path
        self.set_size((self.width,self.height))

        
