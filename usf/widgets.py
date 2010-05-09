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
    def __init__(self, extend=True):
        self.extend = extend
        self.init()
        self.widgets = []
        print "new hbox"
    def add(self, widget, size=(0,0)):
        self.widgets.append(widget)
        if self.extend:
        #set the size of the widgets, they have the same height as the container
            for widget_ in self.widgets:
                widget_.setSize(self.width/len(self.widgets), self.height)
                widget_.x = self.width/len(self.widgets)*self.widgets.index(widget_)
        else:
            posx = 0
            for widget_ in self.widgets:
                if widget_ != widget:
                    posx += widget.width
            widget.x = posx
            if size != (0,0):
                widget.setSize(size[0]*self.width/100, size[1]*self.height/100)
            #widget.setSize(self.width/len(self.widgets), self.height)
    def draw(self):
        self.surface = self.surface.convert().convert_alpha()
        for widget_ in self.widgets:
            self.surface.blit(widget_.draw(),(widget_.x,0))
        return self.surface
class VBox(Container):
    def __init__(self, extend=True):
        self.extend = extend
        self.init()
        self.widgets = []
    def add(self, widget, size=(0,0)):
        self.widgets.append(widget)
        if self.extend:
        #set the size of the widgets, they have the same height as the container
            for widget_ in self.widgets:
                widget_.setSize(self.width, self.height/len(self.widgets))
                widget_.y = self.height/len(self.widgets)*self.widgets.index(widget_)
        else:
            posy = 0
            for widget_ in self.widgets:
                if widget_ != widget:
                    posy += widget.height
            widget.y = posy
            if size != (0,0):
                widget.setSize(size[0]*self.width/100, size[1]*self.height/100)
            #widget.setSize(self.width/len(self.widgets), self.height)
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
        size = get_scale(loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    image)[0])
        print "loading an image : " + self.path
        self.init()
        self.setSize(size[0], size[1])
    def setSize(self, w,h):
        self.height = h
        self.width = w
        self.surface = loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    self.path, scale=(w,h)
                    )[0]
    def draw(self):
        #empty the surface
        return self.surface
class Button(Label):
    pass
def get_scale(surface):
    size = (surface.get_width()*800/config.general['WIDTH'], surface.get_height()*480/config.general['HEIGHT'])
    return size
