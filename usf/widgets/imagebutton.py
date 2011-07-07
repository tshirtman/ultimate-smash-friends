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
A Button widget with an image inside, instead of a text.

'''

import os

from usf.widgets.widget import get_scale
from usf.widgets.image import Image
from usf import loaders
CONFIG = loaders.get_config()



class ImageButton(Image):

    def __init__(self, image, image_hover):
        # FIXME save the path to scale it later -> maybe it is bad for
        # performance?
        super(ImageButton, self).__init__(image)
        self.path_hover = image_hover
        size = get_scale(loaders.image(
                    CONFIG.sys_data_dir+
                    os.sep+
                    image)[0])

        self.set_size((size[0], size[1]))
        self.state = False

    def set_size(self, (w, h)):
        self.height = h
        self.width = w
        self.surface_static = loaders.image(
                    CONFIG.sys_data_dir+
                    os.sep+
                    self.path, scale=(w, h))[0]

        self.surface_hover = loaders.image(
                    CONFIG.sys_data_dir+
                    os.sep+
                    self.path_hover, scale=(w, h))[0]

        self.surface = self.surface_static

    def handle_mouse(self, event):
        if self.state:
            event.dict['pos'] = (
                    event.dict['pos'][0] - self.parentpos[0] - self.x,
                    event.dict['pos'][1] - self.parentpos[1] - self.y)

            print event.dict['pos']
        if (
                0 < event.dict['pos'][0] < self.width and
                0 < event.dict['pos'][1] < self.height):
            self.state = True
            self.surface = self.surface_hover
            return False, self
        self.surface = self.surface_static
        return False, False

    def draw(self):
        """
        Return the widget surface. This fonction is often overrided.
        """
        if self.state:
            self.screen.blit(self.surface_hover, (self.parentpos[0] + self.x,
                                                   self.parentpos[1] + self.y))
        else:
            self.screen.blit(self.surface, (self.parentpos[0] + self.x,
                                                   self.parentpos[1] + self.y))


