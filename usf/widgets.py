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
    margin_left = 0
    parentpos = (0,0)
    #this function can be rewritten in the others widgets to have a custom argument lists
    def __init__(self):
        self.init()
    #this function can be rewritten in the others widget if the surface isn't empty
    def init(self):
        self.surface = pygame.Surface((self.width,self.height))
    def draw(self):
        #empty the surface
        self.surface = self.surface.convert().convert_alpha()
        return self.surface
    #this function is used to resize a widget
    def setSize(self, (w,h)):
        self.height = h
        self.width = w
        self.init()
    #this function is used for mosue events
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
    def update_pos(self):
        pass
    def update_size(self):
        pass
class Container(Widget):
    #this function is used to update the container size after adding a widget
    def update_size(self):
        sizex = 0
        sizey = 0
        for widget in self.widgets:
            if self.orientation:
                sizex += widget.width
                if sizey < widget.height:
                    sizey = widget.height
            else:
                sizey += widget.height
                if sizex < widget.width:
                    sizex = widget.width
            if type(self) == HBox:
                sizex += widget.margin
            else:
                sizey += widget.margin
            widget.init()
        self.width = sizex
        self.height = sizey
    #updating the position of all widgets in the container
    def update_pos(self):
        posx = 0
        posy = 0
        for widget in self.widgets:
            if self.orientation:
                posx += widget.margin
            else:
                posy += widget.margin
            widget.y = posy
            widget.x = posx + widget.margin_left
            if self.orientation:
                posx += widget.width
            else:
                posy += widget.height
            widget.parentpos = (self.parentpos[0] + self.x, self.parentpos[1] + self.y)
            widget.update_size()
            widget.update_pos()
    def draw(self):
        self.surface = self.surface.convert().convert_alpha()
        for widget in self.widgets:
            self.surface.blit(widget.draw(),(widget.x,widget.y))
        return self.surface
    #this function is used to add a widget in the conatiner
    def add(self, widget, *args, **kwargs):
        self.widgets.append(widget)
        if 'size' in kwargs:
            widget.setSize((kwargs['size'][0]*800/config.general['WIDTH'], kwargs['size'][1]*480/config.general['HEIGHT']))
        if 'margin' in kwargs:
            if self.orientation:
                widget.margin = kwargs['margin']*config.general['WIDTH']/800
            else:
                widget.margin = kwargs['margin']*config.general['HEIGHT']/480
        if 'margin_left' in kwargs:
            widget.margin_left = kwargs['margin_left']*config.general['WIDTH']/800
        if 'align' in kwargs:
            widget.align(kwargs['align'])
        self.update_size()
        self.update_pos()
        #widget.parentpos = (self.parentpos[0] + self.x, self.parentpos[1] + self.y)
    
            
            
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
        
class Tab(VBox):
    def __init__(self):
        self.init()
        self.widgets = []
        self.orientation = False
        self.tab = TabBar()
        self.add(self.tab)
        self.tab_list = []
        self.tab_content = []
    def add_tab(self, tab, box):
        self.tab.add(tab)
        self.tab_list.append(tab)
        box_content = HBox()
        box_content.add(box)
        self.tab_content.append(box_content)
        if len(self.tab_content) == 1:
            self.add(box_content)
            print self.widgets.index(box_content)
        self.update_pos()
        self.update_size()
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
                if widget == self.tab:
                    for wid in widget.widgets:
                        wid.state=False
                    widget_ = widget.handle_mouse(event)
                    if event.type == pygame.MOUSEBUTTONUP:
                        self.widgets[1] = self.tab_content[self.tab_list.index(widget_)]
                        self.update_pos()
                        self.update_size()
                    elif widget_ != None:
                        widget_.state=True
                else:
                    return widget.handle_mouse(event)
                break
        
        return (False,False)
class TabBar(HBox):
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
                return widget
                break
class Label(Widget):
    indent = 0
    def init(self):
        pass
    def __init__(self, text, *args, **kwargs):
        self.text = text
        self.state = False
        #self.init()
        self.surface_text  = loaders.text( _(self.text),game_font)

        if "height" in kwargs:
            self.height = kwargs['height']
        else:
            self.height = self.surface_text.get_height()
        if "width" in kwargs:
            self.width = kwargs['width']
        else:
            self.width = self.surface_text.get_width()
        if "margin" in kwargs:
            self.txtmargin= kwargs['margin']
        else:
            margin = 0
        if "background" in kwargs:
            self.background = loaders.image(config.sys_data_dir + os.sep + kwargs['background'],scale=(self.width,self.height))[0]
            self.surface = loaders.image_layer(self.background,self.surface_text,(self.txtmargin,0))
        else:
            self.background = None
            self.surface = self.surface_text
    def draw(self):
        #TODO : a @memoize function, and a config file with the color
        return self.surface
    def setText(self,text):
        self.text = text
        self.surface_text  = game_font.render(
            _(self.text),
            True,
            pygame.color.Color("white")
            )
        if self.background != None:
            self.surface = loaders.image_layer(self.background,self.surface_text,(self.txtmargin,0))
        else:
            self.surface = self.surface_text
          
class LongText(Widget):
    def __init__(self, text, *args, **kwargs):
        self.text = open(config.sys_data_dir + os.sep + 'text' + os.sep + text, 'r').readlines()
        
        self.text_height = loaders.text("", game_font).get_height()
        
        
        #the width of the biggest line of the file
        self.max_width = 0
        for i in range(0, len(self.text)):
            self.text[i] = self.text[i].rstrip()
            #print self.text[i]
            if self.max_width < loaders.text(self.text[i], game_font).get_width():
                self.max_width = loaders.text(self.text[i], game_font).get_width()
        #print self.text
        if "height" in kwargs:
            self.height = kwargs['height']
        else:
            #if there isn't any specified height, we keep the height of all the lines
            self.height = self.text_height * len(self.text)
        if "width" in kwargs:
            self.width = kwargs['width']
        else:
            self.width = self.max_width
        if "margin" in kwargs:
            self.txtmargin= kwargs['margin']
        #self.init()
        self.surface = pygame.Surface((self.width,self.height))
        #this surface will be draw into self.surface with a special position to scroll
        #self.surface.blit(self.text_surface, (0,0))
        self.text_surface = pygame.Surface((self.max_width, self.text_height * len(self.text)))
        
        #self.surface = self.surface.convert().convert_alpha()
        #self.text_surface = self.text_surface.convert().convert_alpha()
        
        self.text_surface.fill((0,0,0))
        self.text_surface.set_colorkey((0,0,0))
        self.surface.fill((0,0,0))
        self.surface.set_colorkey((0,0,0))


        #we draw a line under another to have a space between the lines
        text_space = 0
        for text in self.text:
            self.text_surface.blit(loaders.text(text, game_font), (0,text_space))
            #increase the space between the lines
            text_space += self.text_height
        self.surface.blit(self.text_surface, (0,0))
        
        #this variable will be used for scroll
        self.scroll = 0
    def init(self):
        pass
        
    def draw(self):
        #empty the surface:
        self.surface.fill((0,0,0))
        self.surface.set_colorkey((0,0,0))
        
        self.surface.blit(self.text_surface, (0,-self.scroll))
        
        return self.surface
        
        
    def handle_mouse(self,event):
        if (event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEBUTTONDOWN):
            if event.dict['button'] == 4:
                if self.scroll > 0:
                    self.scroll -= 20
            elif event.dict['button'] == 5:
                if self.scroll < self.text_height * len(self.text)-self.width:
                    self.scroll += 20
            print self.scroll*100/self.getTextHeight()
            self.slider.setValue(self.scroll*100/self.getTextHeight())
        return (False,False)
    def getTextHeight(self):
        return self.text_height * len(self.text)-self.width
class Paragraph(HBox):
    def setText(self, widget):
        self.widgets = []
        self.add(widget)
        self.add(SliderParagraph('a'), size=(20,self.height))
        self.widgets[0].slider = self.widgets[1]
        self.widgets[1].slider = self.widgets[0]
    def draw(self):
        self.surface = self.surface.convert().convert_alpha()
        for widget in self.widgets:
            self.surface.blit(widget.draw(),(widget.x,widget.y))
        return self.surface
class SliderParagraph(Widget):
    def __init__(self, text):
        self.text = text
        self.parentpos = (0,0)
        self.extend = False
        self.value = 0
        self.orientation = False
        self.init()
        self.index = 0
        self.state = False
        self.height =0
        self.width = 0
    def init(self):
        self.background= loaders.image(config.sys_data_dir + os.sep + 'gui' + os.sep + config.general['THEME'] + os.sep + 'sliderh_background.png',
            scale=optimize_size((self.width,self.height)))[0]
        self.center= loaders.image(config.sys_data_dir + os.sep + 'gui' + os.sep + config.general['THEME'] + os.sep + 'sliderh_center.png',
            scale=optimize_size((self.width,self.width*6)))[0]
        self.center_hover= loaders.image(config.sys_data_dir + os.sep + 'gui' + os.sep + config.general['THEME'] + os.sep + 'sliderh_center.png',
            scale=optimize_size((self.width,self.width*6)))[0]
    def handle_mouse(self,event):
        if self.state == True:
            event.dict['pos'] =(event.dict['pos'][0] - self.parentpos[0]-self.x,
                                event.dict['pos'][1] - self.parentpos[1]-self.y)
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        if self.state == True:
            if event.type == pygame.MOUSEBUTTONUP:
                self.state = False
                return False, False
            elif event.type == pygame.MOUSEMOTION and y -self.space >0 and y - self.space + self.width*6 < self.height:
                self.value = y - self.space
            elif event.type == pygame.MOUSEMOTION  and y -self.space >0:
                self.value = self.height-self.width*6
            elif event.type == pygame.MOUSEMOTION  and y - self.space + self.width*6 < self.height:
                self.value = 0
            
            textheight = self.slider.getTextHeight()
            scroll = self.getValue()
            self.slider.scroll = textheight*scroll/100
            return self, self
        if 0 < x < self.width and 0 < y < self.height:
            if self.value-self.height < y and y < self.value + self.height:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #to adjust the position of the slider
                    self.space = y - self.value
                    
                    self.state = True
                    return self, self
            return False, False
        self.state = False
        return (False,False)
    def getValue(self):
        return self.value*100/(self.height - self.width*6)
    def setValue(self, value):
        print value
        self.value = value*(self.height - self.width*6)/100
        print self.value
    def draw(self):
        if self.state:
            return loaders.image_layer(self.background, self.center_hover, (0,self.value))
        else:
            return loaders.image_layer(self.background, self.center, (0,self.value))
class Slider(Widget):
    def __init__(self, text):
        self.text = text
        self.parentpos = (0,0)
        self.extend = False
        self.value = 0
        self.orientation = False
        self.init()
        self.index = 0
        self.state = False
        self.height = optimize_size((250,30))[1]
        self.width = optimize_size((25,30))[0] + optimize_size((25,30))[0] + optimize_size((100,30))[0]
    def init(self):
        self.background= loaders.image(config.sys_data_dir + os.sep + 'gui' + os.sep + config.general['THEME'] + os.sep + 'slider_background.png',
            scale=optimize_size((self.width,self.height)))[0]
        self.center= loaders.image(config.sys_data_dir + os.sep + 'gui' + os.sep + config.general['THEME'] + os.sep + 'slider_center.png',
            scale=optimize_size((self.height,self.height)))[0]
        self.center_hover= loaders.image(config.sys_data_dir + os.sep + 'gui' + os.sep + config.general['THEME'] + os.sep + 'slider_center_hover.png',
            scale=optimize_size((self.height,self.height)))[0]
    def handle_mouse(self,event):
        if self.state == True:
            event.dict['pos'] =(event.dict['pos'][0] - self.parentpos[0]-self.x,
                                event.dict['pos'][1] - self.parentpos[1]-self.y)
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        if self.state == True:
            if event.type == pygame.MOUSEBUTTONUP:
                self.state = False
                return False, False
            elif event.type == pygame.MOUSEMOTION and x -self.space >0 and x - self.space + self.height < self.width:
                self.value = x - self.space
            elif event.type == pygame.MOUSEMOTION  and x -self.space >0:
                self.value = self.width-self.height
            elif event.type == pygame.MOUSEMOTION  and x - self.space + self.height < self.width:
                self.value = 0
            return self, self
        if 0 < x < self.width and 0 < y < self.height:
            if self.value-self.height < x and x < self.value + self.height:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #to adjust the position of the slider
                    self.space = x - self.value
                    
                    self.state = True
                    return self, self
            return False, False
        self.state = False
        return (False,False)
    def getValue(self):
        return self.value*100/(self.width - self.height)
    def setValue(self, value):
        self.value = value*(self.width - self.height)/100
    def draw(self):
        if self.state:
            return loaders.image_layer(self.background, self.center_hover, (self.value,0))
        else:
            return loaders.image_layer(self.background, self.center, (self.value,0))
            
class CheckBox(Widget):
    pass
    
    
class Image(Widget):
    def init(self):
        pass
    def __init__(self, image, *args, **kwargs):
        #save the path to scale it later -> maybe it is bad for performance, FIXME
        self.path = image
        if "size" in kwargs:
            size = optimize_size(kwargs['size'])
        else:
            size = get_scale(loaders.image(
                    config.sys_data_dir+
                    os.sep+
                    image)[0])
                    
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
    def setImage(self,path):
        self.path = path
        self.setSize((self.width,self.height))
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
            return self.surface_hover
        else:
            return self.surface
class Spinner(HBox):
    def __init__(self, values):
        self.parentpos = (0,0)
        self.extend = False
        self.values = values
        self.orientation = True
        self.init()
        self.index = 0
        self.state = False
        self.height = optimize_size((250,30))[1]
        self.width = optimize_size((25,30))[0] + optimize_size((25,30))[0] + optimize_size((100,30))[0]
    def init(self):
        self.surface = pygame.Surface((self.width,self.height))
        self.widgets = []
        self.left_arrow = ImageButton("gui" + os.sep + config.general['THEME'] + os.sep + "spinner_left.png",
            "gui" + os.sep + config.general['THEME'] + os.sep + "spinner_left_hover.png")
        self.left_arrow.setSize(optimize_size((25,30)))
        self.add(self.left_arrow)
        self.center = Label(self.values[0],
            background="gui" + os.sep + config.general['THEME'] + os.sep + "spinner_center.png",
            height=optimize_size((100,30))[1],
            width=optimize_size((100,30))[0],
            margin=optimize_size((10,0))[0])
        self.add(self.center)
        self.right_arrow = ImageButton("gui" + os.sep + config.general['THEME'] + os.sep + "spinner_right.png",
            "gui" + os.sep + config.general['THEME'] + os.sep + "spinner_right_hover.png")
        self.right_arrow.setSize(optimize_size((25,30)))
        self.add(self.right_arrow)
        self.update_pos()
        self.update_size()
    def handle_mouse(self,event):
        if self.state == True:
            event.dict['pos'] =(event.dict['pos'][0] - self.parentpos[0]-self.x,
                                event.dict['pos'][1] - self.parentpos[1]-self.y)
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        self.left_arrow.state = False
        self.right_arrow.state = False
        if 0 < event.dict['pos'][0] < self.width and 0 < event.dict['pos'][1] < self.height:
            self.state = True
            for widget in self.widgets:
                if widget.x < x < widget.x+widget.width and widget.y < y < widget.y+widget.height:
                    if widget == self.left_arrow or widget == self.right_arrow:
                        widget.state = True
                        if event.type == pygame.MOUSEBUTTONUP:
                            if widget == self.right_arrow:
                                if self.index < len(self.values)-1:
                                    self.index +=1
                            else:
                                if self.index > 0:
                                    self.index -=1
                            self.text = self.values[self.index]
                            self.center.setText(self.text)
                            return (self,False)
            return False, self
        self.state = False
        return (False,False)
    def getValue(self):
        return self.values[self.index]
    def getIndex(self):
        return self.index
        
#these functions are used to handle the others screen resolutions
#FIXME : maybe they could go to loaders ?
def optimize_size(size):
    size = (size[0]*config.general['WIDTH']/800, size[1]*config.general['HEIGHT']/480)
    return size
def get_scale(surface):
    size = (surface.get_width()*config.general['WIDTH']/800, surface.get_height()*config.general['HEIGHT']/480)
    return size
