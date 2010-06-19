################################################################################
# copyright 2010 Lucas Baudin <xapantu@gmail.com>                              #
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

import pygame
from widget import Widget, get_scale, optimize_size
from usf import loaders
from usf.font import fonts

from box import HBox

class LongText(Widget):
    """
    This widget is used with the Paragraph widget, it support a long text
    with break line whereas Label support only one line
    """

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
            self.height = optimize_size((0,kwargs['height']))[1]
        else:
            #if there isn't any specified height, we keep the height of all the lines
            self.height = self.text_height * len(self.text)
        if "width" in kwargs:
            self.width = optimize_size((kwargs['width'],0))[0]
        else:
            self.width = self.max_width
        if "margin" in kwargs:
            self.txtmargin= kwargs['margin']

        self.surface = pygame.Surface((self.width,self.height))
        self.text_surface = pygame.Surface((self.max_width, self.text_height * len(self.text)))
        
        
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
                if self.scroll > 20:
                    self.scroll -= 20
                else:
                    self.scroll = 0
            elif event.dict['button'] == 5:
                if self.scroll < (self.text_height * len(self.text)-self.width)-20:
                    self.scroll += 20
                else:
                    self.scroll = self.text_height * len(self.text)-self.width
                    
            #update the scrollbar
            self.slider.set_value(self.scroll*100/self.getTextHeight())
        return (False,False)

    def getTextHeight(self):
        """
        Get the height of all the text.
        """
        return self.text_height * len(self.text)-self.width


class Paragraph(HBox):

    def setText(self, widget):
        self.widgets = []
        self.add(widget)
        self.add(SliderParagraph(''), size=(25,300))
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
        self.background= loaders.image(join(config.sys_data_dir, 'gui',
                                            config.general['THEME'],
                                            'sliderh_background.png'),
                                       scale=(self.width, self.height))[0]
        self.center= loaders.image(config.sys_data_dir + os.sep + 'gui' + os.sep + config.general['THEME'] + os.sep + 'sliderh_center.png',
            scale=(self.width, 180*self.width/34))[0]
        self.center_hover= loaders.image(config.sys_data_dir + os.sep + 'gui' + os.sep + config.general['THEME'] + os.sep + 'sliderh_center_hover.png',
            scale=(self.width, 180*self.width/34))[0]

    def handle_mouse(self,event):
        if self.state == True:
            event.dict['pos'] =(event.dict['pos'][0] - self.parentpos[0] - self.x,
                                event.dict['pos'][1] - self.parentpos[1] - self.parentpos[1] - self.y)
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        if self.state == True:
            if event.type == pygame.MOUSEBUTTONUP:
                self.state = False
                return False, False
            elif event.type == pygame.MOUSEMOTION and y -self.space >0 and y - self.space + 180*self.width/34 < self.height:
                self.value = y - self.space
            elif event.type == pygame.MOUSEMOTION  and y -self.space >0:
                self.value = self.height-180*self.width/34
            elif event.type == pygame.MOUSEMOTION  and y - self.space + 180*self.width/34 < self.height:
                self.value = 0
            
            textheight = self.slider.getTextHeight()
            scroll = self.get_value()
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

    def get_value(self):
        return self.value*100/(self.height - 180*self.width/34)
        
    def set_value(self, value):
        self.value = value*(self.height - 180*self.width/34)/100
        
    def draw(self):
        if self.state:
            return loaders.image_layer(self.background, self.center_hover, (0,self.value))
        else:
            return loaders.image_layer(self.background, self.center, (0,self.value))
