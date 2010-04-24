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

import os, time
from os.path import join
from xml.etree.ElementTree import ElementTree
import pygame
from pygame.locals import *
from pygame.color import Color
from pygame.font import Font

from os import stat
from sys import prefix
import loaders
from config import Config

config = Config.getInstance()

class Widget (object):
    """
    This class is the base of all other widget.
    """

    def __init__(self, screen):
        self.sizex = 0
        self.sizey = 0
        self.posx = 0
        self.posy = 0
        self.name = "name"
        self.action = "print 'click'"
        self.selectable = False
        self.text = ""
        self.anim = False
        self.screen = screen
        self.font_size = screen.get_height()/20
        self.game_font = Font(join(config.sys_data_dir, 'gui',
                                   config.general['THEME'], 'font.otf'),
                               self.font_size)
                              
        filename = join(config.sys_data_dir, 'gui', config.general['THEME'],
                        'theme.xml')
        self.theme = ElementTree().parse(filename)
        self.color = Color(self.theme.find('color').attrib['value'])

        self.load()

    def load(self):
        pass

    def drawSimple(self):
        pass

    def drawHover(self):
        self.drawSimple()
        
    def set_sizex(self, size):
        self.sizex =size
        self.load()
        
    def set_sizey(self, size):
        self.sizey =size
        self.load()
        
    def setText(self, value):
        if(value.split(':')[0] == "config"):
            if(value.split(':')[1] == "keyboard"):
                numcle=0
                try:
                    while config.keyboard.keys()[numcle] != value.split(':')[2]:
                        numcle += 1

                    self.text = pygame.key.name(eval(config.keyboard.values()[numcle]))
                except:
                    self.text ="not defined"
            elif(value.split(':')[1] == "sounds"):
                self.text = str(config.audio[value.split(':')[2]])
            else:
                if(config.general[value.split(':')[1]] == 0):
                    self.text = "False"
                else:
                    self.text = str(config.general[value.split(':')[1]])
        else:
            self.text = value
            
    def state(self,state_str):
        self.state_str = state_str
        
    def click(self,event):
        pass
        return ""

class WidgetLabel(Widget):
    text = ""
    def drawSimple(self):
        for text in self.text.split("\n"):
            self.screen.blit(
                self.game_font.render(
                _(text),
                True,
                self.color
                ),
            (self.posx, self.posy+self.font_size*self.text.split("\n").index(text))
            )
    def draw(self):
        self.drawSimple()

