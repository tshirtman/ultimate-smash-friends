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
# FITNESS FOR A PARTICULAR PURself.posE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# You should have received a copy of the GNU General Public License along with #
# Ultimate Smash Friends.  If not, see <http://www.gnu.org/licenses/>.         #
################################################################################

import pygame
import os
import time
from widget import Widget, get_scale, optimize_size
from usf import loaders
from usf.font import fonts
config = loaders.get_config()

class Coverflow(Widget):

    animation_speed = True
    def __init__(self, values):
        self.values = values
        for value in self.values:
            value.append((0,0))
            value.append(0)
        self.in_anim = False
        self.anim_state = ""
        self.advance = 0
        self.init()

    def init(self):
        self.center_size = (self.sizex(195), self.sizey(120))
        self.posy_center = self.sizey(60)
        self.foreground = loaders.image(os.path.join(config.sys_data_dir,
                                                "gui",
                                                config.general['THEME'],
                                                "coverflow",
                                                "foreground.png"),
                                        scale=(self.width, self.height))[0]
        

        self.frame = loaders.image(os.path.join(config.sys_data_dir,
                                                "gui",
                                                config.general['THEME'],
                                                "coverflow",
                                                "frame.png"),
                                        scale=(self.sizex(137), self.sizey(86)))[0]

        self.surface = pygame.surface.Surface((self.width, self.height))
        self.index = 0
        self.text = self.get_text_transparent(self.values[self.index][0])
        self.previous()
        self.load_main_frame()
        for value in self.values:
            img = loaders.image(value[1])[0]
            #keep ratio
            if img.get_height() > img.get_width():
                value[2] = (self.frame.get_width() - self.sizex(25), img.get_height() * (self.frame.get_width()  - self.sizex(25))/ img.get_width())
            else:
                value[2] = (img.get_width() * (self.frame.get_height()- self.sizex(25)) / img.get_height() , self.frame.get_height() - self.sizey(25))
            value[3] = (self.frame.get_width()/2 - value[2][0]/2, self.frame.get_height()/2 - value[2][1]/2)
        self.need_update = True
                

    def draw(self):
        if self.in_anim or self.need_update:
            size = self.surface.get_size()
            del self.surface
            self.surface = pygame.surface.Surface(size)
            self.pos = self.width/2 - self.main_frame.get_width()/2 + self.advance
            self.draw_main()
            self.draw_right()
            self.draw_left()
            reflection = pygame.transform.flip(self.surface, False, True)
            reflection.set_colorkey(pygame.color.Color("black"))
            #reflection.set_alpha(20)
            self.surface.blit(reflection, (0, self.sizey(100)))
            self.surface.blit(self.text, (self.width/2 - self.text.get_width()/4, self.sizey(30)))

            self.surface.blit(self.foreground, (0,0))
            self.need_update = False
            if self.in_anim:
                self.start_anim()
        return self.surface

    def draw_main(self):
            #main frame
            self.surface.blit(self.main_frame, (self.pos, self.posy_center))
            self.surface.blit(loaders.image(self.values[self.index][1],
                                           scale=self.center_image
                                           )[0],
                             (self.pos + self.center_image_indent[0], self.posy_center  + self.center_image_indent[1]))
            self.pos += self.main_frame.get_width()

    def draw_right(self):
        
        for i in range(self.index - len(self.values) + 1, self.index - len(self.values) + 4):
            self.surface.blit(self.frame, (self.pos, self.sizey(82)))
            self.surface.blit(loaders.image(self.values[i][1], scale=self.values[i][2])[0],
                 (self.pos + self.values[i][3][0], self.sizey(82) + self.values[i][3][1]))
            self.pos += self.frame.get_width()

    def draw_left(self):
            #at left now
            self.pos = self.width/2 - self.main_frame.get_width()/2 - self.frame.get_width()*3 + self.advance
            for i in range(self.index - 3, self.index):
                self.surface.blit(self.frame, (self.pos, self.sizey(82)))
                self.surface.blit(loaders.image(self.values[i][1], scale=self.values[i][2])[0],
                     (self.pos + self.values[i][3][0], self.sizey(82) + self.values[i][3][1]))
                self.pos += self.frame.get_width()
    
    def sizex(self, x):
        return x*self.width/800

    def sizey(self, y):
        return y*self.height/275
    
    def next(self):
        if self.index - 1 >= 0:
            self.index -= 1
        else:
            self.index = len(self.values) - 1
        self.text = self.get_text_transparent(self.values[self.index][0])

    def previous(self):
        if self.index + 1 <= len(self.values) - 1:
            self.index += 1
        else:
            self.index = 0
        self.text = self.get_text_transparent(self.values[self.index][0])
    
    def handle_mouse(self, event):
        if not self.in_anim:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x = event.dict['pos'][0]
                y = event.dict['pos'][1]
                if x > self.width/2 + self.frame.get_width()/2:
                    self.launch_anim(False)
                elif x < self.width/2 - self.frame.get_width()/2:
                    self.launch_anim(True)
        return False, False
        
    def launch_anim(self, sens):
        #self.last_c_update = time.time()
        self.anim_state = "start"
        self.last_index = self.index
        self.in_anim = True
        self.sens = sens
        
    def animation(self):
        if self.in_anim:
            if self.anim_state == "start" or self.anim_state == "slide":
                if self.center_size[0] - self.sizex(10) > self.sizey(137):
                    w = self.center_size[0] - self.sizex(30)
                    h = self.center_size[1] * w / self.center_size[0]
                    #self.advance += self.sizex(5)
                    self.text.set_alpha(self.text.get_alpha() - 50)
                else:
                    self.anim_state = "slide"
                    self.text.set_alpha(0)
                    w = self.sizey(137)
                    h = self.sizey(86)
                self.posy_center = self.sizey(125) - h/2
                self.center_size = (w, h)
                self.load_main_frame()
                if self.sens:
                    if self.advance + 40 < self.frame.get_width():
                        self.advance +=40
                    else:
                        self.advance = self.frame.get_width()
                        self.anim_state = "change"
                else:
                    if self.advance - 40 > - (self.frame.get_width()):
                        self.advance -=40
                    else:
                        self.advance = - self.frame.get_width()
                        self.anim_state = "change"
            elif self.anim_state == "change":
                if self.sens:
                    self.next()
                else:
                    self.previous()
                self.text.set_alpha(0)
                self.advance = 0
                self.anim_state = "end"
            elif self.anim_state == "end":
                if self.center_size[0] < self.sizey(195):
                    w = self.center_size[0] + self.sizex(30)
                    h = self.center_size[1] * w / self.center_size[0]
                    #self.advance -= self.sizex(5)
                    self.text.set_alpha(self.text.get_alpha() + 50)
                else:
                    w = self.sizex(195)
                    h = self.sizey(120)
                    self.text.set_alpha(250)
                    #self.in_anim = False
                    self.anim_state = ""
                    self.advance = 0
                self.posy_center = self.sizey(125) - h/2
                self.center_size = (w, h)
                self.load_main_frame()
                self.need_update = True
            elif self.anim_state == "":
                self.in_anim = False
                #print time.time() - self.last_c_update
                self.need_update = True
                
            
    def load_main_frame(self):
        self.main_frame = loaders.image(os.path.join(config.sys_data_dir,
                                                "gui",
                                                config.general['THEME'],
                                                "coverflow",
                                                "frame.png"),
                                        scale=self.center_size)[0]
        
        img = loaders.image(self.values[self.index][1])[0]
        #keep ratio
        if img.get_height() > img.get_width():
            self.center_image = (self.main_frame.get_width() - self.sizex(25), img.get_height() * (self.main_frame.get_width() - self.sizex(25)) / img.get_width())
        else:
            self.center_image = (img.get_width() * (self.main_frame.get_height() - self.sizey(25)) / img.get_height(), (self.main_frame.get_height()- self.sizey(25)))
        self.center_image_indent = (self.main_frame.get_width()/2 - self.center_image[0]/2,
                                    self.main_frame.get_height()/2 - self.center_image[1]/2)
    
    def get_text_transparent(self, name):
        text = loaders.text(name, fonts['mono']['10']).convert()
        text.fill(pygame.color.Color("black"))
        text.set_colorkey(pygame.color.Color("black"))
        text.blit(loaders.text(name, fonts['mono']['22']), (0,0))
        return text
    
    def get_value(self):
        return self.values[self.index][0]
