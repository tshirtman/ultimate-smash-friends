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

import pygame
from pygame.locals import USEREVENT, QUIT
from math import sin, cos
from time import time
import os
import time
import xml.dom.minidom
import logging
import thread
# Our modules

from config import Config

config = Config.getInstance()

import controls
import loaders

#translation
import translation

class Skin (object):
    dialog = {}
    color = None
    background = []
    background_duration = []
    def __init__(self):
        xml_file = xml.dom.minidom.parse(config.sys_data_dir+
            os.sep+
            'gui'+
            os.sep+ config.general['THEME'] + os.sep + "theme.xml").getElementsByTagName("theme")[0]
        self.color = pygame.color.Color("white")
        for node in xml_file.childNodes:
            try:
                if node.tagName == "color":
                    self.color = pygame.color.Color(str(node.getAttribute("value")))
                elif node.tagName == "dialog":
                    self.dialog['sizex'] = int(node.getAttribute("sizex"))*config.general['WIDTH']/100
                    self.dialog['sizey'] = int(node.getAttribute("sizey"))*config.general['HEIGHT']/100
                    self.dialog['posx'] = int(node.getAttribute("posx"))*config.general['WIDTH']/100
                    self.dialog['posy'] = int(node.getAttribute("posy"))*config.general['HEIGHT']/100
                elif node.tagName == "background":
                    for child_node in node.childNodes:
                        try:
                            if child_node.tagName == "img":
                                self.background.append(child_node.getAttribute("src"))
                                self.background_duration.append(float(child_node.getAttribute("time")))
                        except:
                            pass
            except:
                pass
