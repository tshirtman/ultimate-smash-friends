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

#theme support
from skin import Skin, game_font
skin = Skin()

#module to load image
import loaders
class Widget (object):
    """
    This class is the base of all other widget.
    """
    width = 0
    height = 0
    x =0
    y = 0
    def __init__(self):
        self.init()
    def init(self):
        self.surface = pygame.Surface((self.width,self.height))
    def draw(self):
        #empty the surface
        self.surface = self.surface.convert().convert_alpha()
        return self.surface
    def setSize(self, w,h):
        self.height = h
        self.width = w
        self.surface = pygame.Surface((w,h))
class Container(Widget):
    pass
class HBox(Container):
    widgets = []
    def __init__(self, extend=True):
        self.extend = extend
        self.init()
    def add(self, widget, size=(20,20)):
        self.widgets.append(widget)
        if self.extend:
            for widget in self.widgets:
                #set the size of the widgets, they have the same height as the container
                    widget.setSize(self.width/len(self.widgets), self.height)
                    widget.x = self.width/len(self.widgets)*self.widgets.index(widget)
        else:
            posx = 0
            for widget in self.widgets:
                posx += widget.width
            widget.x = posx
            widget.setSize(size[0]*self.width/100, size[1*self.height/100])
    def draw(self):
        self.surface = self.surface.convert().convert_alpha()
        for widget in self.widgets:
            self.surface.blit(widget.draw(),(widget.x,0))
        return self.surface
class VBox(Container):
    widgets = []
    def __init__(self, extend=True):
        self.extend = extend
        self.init()
    def add(self, widget, size=(20,20)):
        self.widgets.append(widget)
        if self.extend:
            for widget in self.widgets:
                #set the size of the widgets, they have the same height as the container
                    widget.setSize(self.width, self.height/len(self.widgets))
                    widget.y = self.height/len(self.widgets)*self.widgets.index(widget)
        else:
            posy = 0
            for widget in self.widgets:
                posy += widget.height
            widget.y = posx
            widget.setSize(size[0]*self.width/100, size[1*self.height/100])
    def draw(self):
        self.surface = self.surface.convert().convert_alpha()
        for widget in self.widgets:
            self.surface.blit(widget.draw(),(0,widget.y))
        return self.surface
class Label(Widget):
    def __init__(self, text):
        self.text = text
        self.init()
    def draw(self):
        #TODO : a @memoize function, and a config file with the color
        self.surface = self.surface.convert().convert_alpha()
        self.surface.blit(
            game_font.render(
            _(self.text),
            True,
            pygame.color.Color("white")
            ),
        (0,0)
        )
        return self.surface
class CheckBox(Widget):
    pass
class Image(Widget):
    def __init__(self, image):
        #save the path to scale it later -> maybe it is bad for performance, FIXME
        self.path = image
        self.surface = loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    image)[0]
        self.init()
        print "loading an image : " + self.path
    def setSize(self, w,h):
        self.height = h
        self.width = w
        self.surface = loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    self.path, scale=(w, h)
                    )[0]
    def draw(self):
        #empty the surface
        return self.surface
class Button(Label):
    pass
