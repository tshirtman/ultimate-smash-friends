################################################################################
# Copyright 2011 Lucas Baudin <xapantu@gmail.com>                              #
#                                                                              #
# This file is part of Ultimate Smash Friends                                  #
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

# Launch this files using 'python -m usf.tests.skin' from the root folder of usf

# This file contains a testsuite for skin.Layer
# TODO: skin.Skin is not tested

from usf import skin
from usf import loaders

import unittest
from xml.etree.ElementTree import ElementTree
import pygame

class TestLayer(unittest.TestCase):

    def setUp(self):
        pass

    def test(self):
        # We need to init pygame and to create a display to load the images
        pygame.init()
        self.screen = pygame.display.set_mode((100,100))

        # Read the xml file of blobplanet level
        attrib = ElementTree()
        attrib.parse(loaders.get_config().sys_data_dir + "levels/blobplanet/level.xml")
        
        # Let's use the first layer node, we know it values
        layer = skin.Layer(attrib.findall("layer")[0])

        # Update the timing of the layer
        layer.get_image(0)

        # At 0.0, our layer should be at 0 on the x axis
        self.assertEqual(layer.get_pos(0)[0], 0)
        # At 0.0, our layer should be at -70 on the y axis
        self.assertEqual(layer.get_pos(0)[1], -70)
        # At 2.0, our layer should be at 30 on the x axis
        self.assertEqual(layer.get_pos(2)[0], 30)
        # At 2.0, our layer should be at 600 on the x axis
        self.assertEqual(layer.get_pos(2)[1], 600)


if __name__ == '__main__':
    unittest.main()
