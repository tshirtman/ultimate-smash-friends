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
from xml.etree.ElementTree import ElementTree

import pygame
from pygame.locals import USEREVENT, QUIT

# Our modules
from config import Config

sys_data_dir = Config().sys_data_dir
general = Config().general

#translation
import translation

class Skin (object):
    def __init__(self):
        self.dialog = {}
        self.color = pygame.color.Color("white")
        self.background = []
        self.background_duration = []
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

        if xml_file.find("background") is not None:
            img = xml_file.find("background").find("img")
            self.background.append(img.attrib["src"])
            self.background.append(img.attrib["time"])

pygame.font.init()
game_font = pygame.font.Font(os.path.join(sys_data_dir, "gui", 
                                          general["THEME"], "font.otf"),
                             general["HEIGHT"]/25) 
