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
import entity_skin
from game import Game
import controls
import loaders
# Gui modules
from new_widgets import (Widget, WidgetLabel, WidgetIcon, WidgetParagraph,
                     WidgetImage, WidgetImageButton, WidgetTextarea,
                     WidgetCheckbox, WidgetCoverflow, WidgetProgressBar)

#translation
import translation


class NewGui(object):
    """
    Main class of the GUI. Init and maintain all menus and widgets.

    """
    def __init__(self, screen):
        self.screen = screen
    def update(self, first, second, third):
        pass
        return False,None
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
skin = Skin()
class Dialog(object):
    state = False
    image = None
    def __init__(self, screen, name):
        global skin
        self.background = loaders.image(
            config.sys_data_dir+
            os.sep+
            'gui'+
            os.sep+
            config.general['THEME']+
            os.sep+
            "background-dialog.png", scale=(skin.dialog['sizex'], skin.dialog['sizey'])
            )[0]
        self.background.set_alpha(150)
        self.screen = screen
    def draw(self):
        self.screen.blit(self.tmp_screen, (0,0))
        self.screen.blit(self.background, (skin.dialog['posx'], skin.dialog['posy']))
    def show(self):
        if self.state is False:
            self.state = True
            self.tmp_screen = self.screen.copy()
            cache = pygame.Surface((config.general['WIDTH'], config.general['HEIGHT']))
            cache.fill(pygame.color.Color("black"))
            cache.set_alpha(100)
            self.tmp_screen.blit(cache, (0,0))
        else:
            self.state = False
            self.tmp_screen = None
