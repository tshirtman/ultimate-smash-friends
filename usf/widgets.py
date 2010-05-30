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
config = Config()

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
    margin = 0
    parentpos = (0,0)
    def __init__(self):
        self.init()
    def init(self):
        self.surface = pygame.Surface((self.width,self.height))
    def draw(self):
        #empty the surface
        self.surface = self.surface.convert().convert_alpha()
        return self.surface
    def setSize(self, (w,h)):
        self.height = h
        self.width = w
        self.init()
    def handle_mouse(self,event):
        try:
            self.widgets
        except:
            self.widgets = []
        #print event.dict['pos']
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        for widget in self.widgets:
            if widget.x < x < widget.x+widget.width and widget.y < y < widget.y+widget.height:
                #print 'widget: ' + str(widget) + ' x: ' + str(widget.x) + ' width: ' + str(widget.width) + ' y: ' + str(widget.y) + ' height: ' + str(widget.height)
                event.dict['pos'] = (x-widget.x, y-widget.y)
                return widget.handle_mouse(event)
                break
        
        return (False,False)
    def align(self,align):
        pass
class Container(Widget):
    def update_size(self):
        sizex = 0
        sizey = 0
        for widget in self.widgets:
            sizex += widget.width
            sizey += widget.height
            if type(self) == HBox:
                sizex += widget.margin
            else:
                sizey += widget.margin
            widget.init()
        self.width = sizex
        self.height = sizey
    def update_pos(self):
        posx = 0
        posy = 0
        for widget in self.widgets:
            if type(self) == HBox:
                posx += widget.margin
            else:
                posy += widget.margin
            widget.y = posy
            widget.x = posx
            if self.orientation:
                posx += widget.width
            else:
                posy += widget.height
    def draw(self):
        self.surface = self.surface.convert().convert_alpha()
        for widget in self.widgets:
            self.surface.blit(widget.draw(),(widget.x,widget.y))
        return self.surface
    def add(self, widget, *args, **kwargs):
        self.widgets.append(widget)
        if 'size' in kwargs:
            widget.setSize((kwargs['size'][0]*800/config.general['WIDTH'], kwargs['size'][1]*480/config.general['HEIGHT']))
        if 'margin' in kwargs:
            if self.orientation:
                widget.margin = kwargs['margin']*config.general['WIDTH']/800
            else:
                widget.margin = kwargs['margin']*config.general['HEIGHT']/480
        if 'align' in kwargs:
            widget.align(kwargs['align'])
        widget.parentpos = (self.parentpos[0] + self.x, self.parentpos[1] + self.y)
        self.update_pos()
        self.update_size()
    
            
            
class HBox(Container):
    def __init__(self):
        self.init()
        self.widgets = []
        self.orientation = True
        
        
class VBox(Container):
    def __init__(self):
        self.init()
        self.widgets = []
        self.orientation = False
        
        
class Label(Widget):
    indent = 0
    def init(self):
        pass
    def __init__(self, text, *args, **kwargs):
        self.text = text
        self.state = False
        #self.init()
        self.surface  = game_font.render(
            _(self.text),
            True,
            pygame.color.Color("white")
            )
        #backup for button
        if "height" in kwargs:
            self.height = kwargs['height']
        else:
            self.height = self.surface.get_height()
        self.width = self.surface.get_width()
        if "background" in kwargs:
            self.background = loaders.image(config.sys_data_dir + os.sep + kwargs['background'],scale=(self.width,self.height))[0]
            self.surface = loaders.image_layer(self.background,self.surface)
    def draw(self):
        #TODO : a @memoize function, and a config file with the color
        return self.surface
        
        
class CheckBox(Widget):
    pass
    
    
class Image(Widget):
    def init(self):
        pass
    def __init__(self, image):
        #save the path to scale it later -> maybe it is bad for performance, FIXME
        self.path = image
        size = get_scale(loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    image)[0])
        print "loading an image : " + self.path
        self.init()
        self.setSize((size[0], size[1]))
        self.state = True
    def setSize(self, (w,h)):
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
    posy = 0
    def setSize(self, (w,h)):
        if self.width < w:
            # a nice effect to unstick the text from the left
            self.indent = 20*config.general['WIDTH']/800
        self.height = h
        self.width = w
        #center the text
        self.posy = self.height/2-get_scale(self.surface)[1]/2
    def draw(self):
        #print self.x
        #TODO : a @memoize function, and a config file with the color
        if self.state == True:
            return loaders.image_layer(loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    'gui'+
                    os.sep+
                    config.general['THEME']+
                    os.sep+
                    'back_button_hover.png', scale=(self.width, self.height))[0], self.surface, (self.indent, self.posy))
        else:
            return loaders.image_layer(loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    'gui'+
                    os.sep+
                    config.general['THEME']+
                    os.sep+
                    'back_button.png', scale=(self.width, self.height))[0], self.surface, (self.indent, self.posy))
    def handle_mouse(self,event):
        if event.type == pygame.MOUSEBUTTONUP:
            self.state = False
            return self,False
        else:
            if self.state == True:
                event.dict['pos'] =(event.dict['pos'][0] - self.parentpos[0]-self.x, event.dict['pos'][1] - self.parentpos[1]-self.y)
            if 0 < event.dict['pos'][0] < self.width and 0 < event.dict['pos'][1] < self.height:
                self.state = True
                return False,self
            self.state = False
            return False,False
class ImageButton(Image):
    def __init__(self, image, image_hover):
        #save the path to scale it later -> maybe it is bad for performance, FIXME
        self.path = image
        self.path_hover = image_hover
        size = get_scale(loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    image)[0])
        print "loading an image : " + self.path
        self.init()
        self.setSize((size[0], size[1]))
        self.state = False
    def setSize(self, (w,h)):
        self.height = h
        self.width = w
        self.surface = loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    self.path, scale=(w,h)
                    )[0]
        self.surface_hover = loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    self.path_hover, scale=(w,h)
                    )[0]
    def handle_mouse(self,event):
        if self.state == True:
            event.dict['pos'] =(event.dict['pos'][0] - self.parentpos[0]-self.x, event.dict['pos'][1] - self.parentpos[1]-self.y)
        if 0 < event.dict['pos'][0] < self.width and 0 < event.dict['pos'][1] < self.height:
            self.state = True
            return False,self
        self.state = False
        return False,False
    def draw(self):
        if self.state == True:
            return self.surface
        else:
            return self.surface_hover
class Spinner(HBox):
    def __init__(self, values):
        self.extend = False
        self.values = values
        self.orientation = True
        self.init()
        self.widgets = []
        self.left_arrow = ImageButton("gui" + os.sep + config.general['THEME'] + os.sep + "spinner_left.png",
            "gui" + os.sep + config.general['THEME'] + os.sep + "spinner_left_hover.png")
        self.left_arrow.setSize(optimize_size((25,30)))
        self.add(self.left_arrow)
        center = Label(values[0], background="gui" + os.sep + config.general['THEME'] + os.sep + "spinner_center.png", height=optimize_size((0,30))[1])
        self.add(center)
        self.right_arrow = ImageButton("gui" + os.sep + config.general['THEME'] + os.sep + "spinner_right.png",
            "gui" + os.sep + config.general['THEME'] + os.sep + "spinner_right_hover.png")
        self.right_arrow.setSize(optimize_size((25,30)))
        self.add(self.right_arrow)
    def handle_mouse(self,event):
        try:
            self.widgets
        except:
            self.widgets = []
        #print event.dict['pos']
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        for widget in self.widgets:
            if widget.x < x < widget.x+widget.width and widget.y < y < widget.y+widget.height:
                #print 'widget: ' + str(widget) + ' x: ' + str(widget.x) + ' width: ' + str(widget.width) + ' y: ' + str(widget.y) + ' height: ' + str(widget.height)
                if widget == self.left_arrow or widget == self.right_arrow:
                    if event.type == pygame.MOUSEBUTTONUP:
                        return (self,False)
                    else:
                        event.dict['pos'] = (x-widget.x, y-widget.y)
                        print "spinner"
                        return widget.handle_mouse(event)
        return (False,False)
def optimize_size(size):
    size = (size[0]*config.general['WIDTH']/800, size[1]*config.general['HEIGHT']/480)
    return size
def get_scale(surface):
    size = (surface.get_width()*config.general['WIDTH']/800, surface.get_height()*config.general['HEIGHT']/480)
    return size
