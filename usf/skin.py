#i###############################################################################
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
from pygame.locals import USEREVENT, QUIT

# Our modules
from config import Config
import loaders
sys_data_dir = Config().sys_data_dir
general = Config().general
config = Config()

#translation
import translation

class Skin (object):
    def __init__(self):
        self.last_update = 0
        self.dialog = {}
        self.color = pygame.color.Color("white")
        self.background = []
        self.layer = []
        self.background_duration = []
        self.current = 0
        self.surface = 0
        xml_file = ElementTree().parse(os.path.join(sys_data_dir, 
                                                    "gui", general["THEME"],
                                                    "theme.xml"))

        if xml_file.find("color") is not None:
            self.color = pygame.color.Color(xml_file.find("color").attrib["value"])

        if xml_file.find("dialog") is not None:
            self.dialog["sizex"] = int(xml_file.find("dialog").attrib["sizex"])*general["WIDTH"]/100
            self.dialog["sizey"] = int(xml_file.find("dialog").attrib["sizey"])*general["HEIGHT"]/100
            self.dialog["posx"] = int(xml_file.find("dialog").attrib["posx"])*general["WIDTH"]/100
            self.dialog["posy"] = int(xml_file.find("dialog").attrib["posy"])*general["HEIGHT"]/100

        for node in xml_file.findall("layer"):
            self.layer.append(Layer(node))

    def get_background(self):
        pygame.display.get_surface().fill(pygame.color.Color("black"))
        for layer in self.layer:
            pygame.display.get_surface().blit(layer.get_image(), layer.get_pos())

class Layer(object):

    def __init__(self, node):
        self.last_update = 0
        self.current = 0
        self.background = loaders.image(join(config.sys_data_dir,
                                             "gui",
                                             config.general['THEME'],
                                             node.attrib["src"]),
                                        scale=(int(node.attrib["sizex"])*config.general['WIDTH']/800,
                                               int(node.attrib["sizey"])*config.general['HEIGHT']/480))[0]
        self.frame = []
        for frame in node.findall("frame"):
            self.frame.append([float(frame.attrib["time"]),
                          (int(frame.attrib["x"]), int(frame.attrib["y"]))])

    def get_image(self):
        if self.last_update + self.frame[self.current][0] < time.time():
            self.last_update = time.time()
            if self.current + 1 < len(self.frame):
                self.current += 1
            else:
                self.current = 0
        return self.background

    def get_pos(self):
        return self.frame[self.current][1]
