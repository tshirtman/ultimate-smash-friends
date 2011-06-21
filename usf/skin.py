################################################################################
# copyright 2009 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
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

import os
from os.path import join
import time
from xml.etree.ElementTree import ElementTree

import pygame

# Our modules
from usf.config import Config
import usf.loaders as loaders

CONFIG = Config()


class Skin (object):

    def __init__(self):
        self.dialog = {}
        self.color = pygame.color.Color("white")
        self.layer = []
        xml_file = ElementTree().parse(os.path.join(
            CONFIG.sys_data_dir,
            "gui",
            CONFIG.general["THEME"],
            "theme.xml"))

        if xml_file.find("color") is not None:
            self.color = pygame.color.Color(
                    xml_file.find("color").attrib["value"])

        if xml_file.find("dialog") is not None:
            conf_d = xml_file.find("dialog")
            W, H = CONFIG.general["WIDTH"], CONFIG.general["HEIGHT"]

            self.dialog["sizex"] = int(conf_d.attrib["sizex"]) * W / 100
            self.dialog["sizey"] = int(conf_d.attrib["sizey"]) * H / 100
            self.dialog["posx"] = int(conf_d.attrib["posx"]) * W / 100
            self.dialog["posy"] = int(conf_d.attrib["posy"]) * H / 100

        for node in xml_file.findall("layer"):
            self.layer.append(Layer(node))

    def get_background(self):
        pygame.display.get_surface().fill(pygame.color.Color("black"))
        for layer in self.layer:
            pygame.display.get_surface().blit(
                    layer.get_image(), layer.get_pos())


class Layer(object):
    """
    A layer class.
    It is mainly used to have animated background in both the gui and the game.

    It is created from an ElementTree xml node.

    Here is the syntax::

        <layer sizex="35" sizey="46" src="path.png">
            <frame time="2" x="0" y="-70" />
            <frame time="0" x="30" y="600" />
        </layer>

    The path (path.png) of the image must be an absolute path from the data
    directory of USF, e.g. levels/blobplanet/leaf.png.

    Time is the duration of the frame (seconds), here, the image will go to the
    second frame in 2 seconds (and then, it will go to the first in 0).
    """

    def __init__(self, node):
        self.last_update = 0
        self.current = 0
        sizex = int(node.attrib["sizex"]) * CONFIG.general['WIDTH']/800
        sizey = int(node.attrib["sizey"]) * CONFIG.general['HEIGHT']/600
        self.frame = []
        if "type" in node.attrib:
            self.x = int(node.attrib["x"]) * CONFIG.general['WIDTH']/800
            self.y = int(node.attrib["y"]) * CONFIG.general['HEIGHT']/600
            if node.attrib["type"] == "framebyframe":
                self.type = 1
                for frame in node.findall("frame"):
                    src = loaders.image(join(CONFIG.sys_data_dir,
                                                 frame.attrib["src"]),
                                            scale=(sizex, sizey))[0]

                    time = float(frame.attrib["time"])
                    self.frame.append((time, src))
        else:
            self.type = 0
            self.background = loaders.image(join(CONFIG.sys_data_dir,
                                                 node.attrib["src"]),
                                            scale=(sizex, sizey))[0]

            for frame in node.findall("frame"):
                x = int(frame.attrib["x"]) * CONFIG.general['WIDTH']/800
                y = int(frame.attrib["y"]) * CONFIG.general['HEIGHT']/600
                time = float(frame.attrib["time"])
                self.frame.append((time, (x, y)))

    def get_image(self, dt=-1):
        """
        Get the image surface.

        :param dt: The current time. Usually, it is -1, and it is set to
            time.time() when it is -1. It can be useful to specify the time for
            unit testing.

        :rtype: pygame surface
        """

        if dt == -1:
            dt = time.time()
        if self.last_update + self.frame[self.current][0] < dt:
            self.last_update = dt
            if self.current + 1 < len(self.frame):
                self.current += 1
            else:
                self.current = 0
        if self.type == 0:
            return self.background
        else:
            return self.frame[self.current][1]

    def get_pos(self, dt = -1):
        """
        Get the position of the layer.

        :param dt: The current time. Usually, it is -1, and it is set to
            time.time() when it is -1. It can be useful to specify the time for
            unit testing.

        :rtype: tuple which contains the coordinates of the layer (x, y)
        """
        if self.type == 0:
            if dt == -1:
                dt = time.time()

            interval = dt - self.last_update
            period = self.frame[self.current][0]
            position_first = self.frame[self.current][1]
            position_next = (0, 0)

            # if we are on the last frame, just return the value of this frame
            if self.current + 1 < len(self.frame):
                position_next = self.frame[self.current + 1][1]
            else:
                period = 0

            # if we are on the first frame, just return it coordinates
            if period == 0:
                return self.frame[self.current][1]

            p = period
            i = interval

            x = ((p - i) * position_first[0] + i * position_next[0]) / p
            y = ((p - i) * position_first[1] + i * position_next[1]) / p

            position = (x, y)
            return position
        else:
            return(self.x, self.y)

