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
import time

from usf import loaders

config = loaders.get_config()

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
    text = ""
    widget_id = ""
    animation_speed = 1.0
    last_animation = 0.0
    
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

    def set_size(self, (w,h)):
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
                event.dict['pos'] = (x-widget.x, y-widget.y)
                return widget.handle_mouse(event)
        
        return (False,False)

    def set_align(self,align):
        pass

    def update_pos(self):
        pass

    def update_size(self):
        pass

    def handle_keys(self,event):
        return False, False

    def set_id(self, value):
        self.widget_id = value

    def get_id(self):
        return self.widget_id
        
    def start_anim(self):
        if(self.last_animation + self.animation_speed <= time.time()):
            self.last_animation = time.time()
            self.animation()
        
    def animation(self):
        pass


#these functions are used to handle the others screen resolutions
#FIXME : maybe they could go to loaders ?
width = config.general['WIDTH']
height = config.general['HEIGHT']
def optimize_size(size):
    size = (size[0]*width/800, size[1]*height/480)
    return size
def get_scale(surface):
    size = (surface.get_width()*800/config.general['WIDTH'], surface.get_height()*480/config.general['HEIGHT'])
    return size
