################################################################################
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
from pygame.locals import QUIT
#from math import sin, cos
#from time import time
import os
import time
#import xml.dom.minidom
#import logging
#import thread
# Our modules

from config import Config

config = Config()

#import controls
#import entity_skin
#from game import Game
#import controls
import loaders
# Gui modules
#from widgets import (HBox, VBox, Label)
from skin import Skin
#import game
from widgets import optimize_size 
from font import fonts
class Gui(object):
    """
    Main class of the GUI. Init and maintain all menus and widgets.

    """
    def __init__(self, surface):
        self.screen = surface
        self.game = None
        self.screens = {}
        self.screen_history = []
        #TODO : Use a config file
        screens = ['main_screen', 'configure', 'about', 'local_game', 'resume', 'sound', 'screen_screen', 'keyboard']
        for name in screens:
            exec("import screen." + name)
            exec('scr = screen.' + name + '.' + name + "('"+ name +"',self.screen)")
            #load all image
            scr.update()
            scr.update()
            self.screens[name] = scr
        self.screen_current = 'main_screen'
        self.skin = Skin()
        self.last_event = time.time()
        self.image = 0
        self.focus = False
        self.state = "menu"
        self.background_scale = (config.general['WIDTH'],
            config.general['HEIGHT'])
        self.cursor = loaders.image(config.sys_data_dir + os.sep + 'cursor.png')[0]
        self.background = loaders.image(
                        config.sys_data_dir+
                        os.sep+
                        "gui"+
                        os.sep +
                        config.general['THEME']+
                        os.sep+
                        self.skin.background[0],
                        scale=self.background_scale
                        )[0]
        self.update_youhere()

    def update(self, first, second, third):
        #FIXME : it sould be in main.pyw
        time.sleep(1.00/float(config.general['MAX_FPS']))
        while(True):
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                pygame.event.post( pygame.event.Event(QUIT) )
                break
            elif event.type != pygame.NOEVENT:
                if event.type == pygame.KEYDOWN:
                    self.handle_keys(event)
                elif ( event.type == pygame.MOUSEBUTTONUP or
                    event.type == pygame.MOUSEBUTTONDOWN or
                    event.type == pygame.MOUSEMOTION) :
                    self.handle_mouse(event)
            else:
                break
        #draw background
        self.screen.blit(loaders.image(
            config.sys_data_dir+
            os.sep+
            "gui"+
            os.sep +
            config.general['THEME']+
            os.sep+
            self.skin.background[0],
            scale=self.background_scale
            )[0], (0,0))
            
        self.screens[self.screen_current].update()
        
        #draw the '> you are here :' dialog
        #self.screen.blit(self.here, (10, 10))
        #update the mouse position
        x, y = pygame.mouse.get_pos()
        #x += self.cursor.get_height()
        #y += self.cursor.get_width()
        self.screen.blit(self.cursor, (x, y))
        
        #if we have a game instance and the state is menu...
        if self.game != None and self.state != "ingame":
            self.state = "ingame"
            self.screen_current = 'resume'
            self.screen_history = []
            return True, self.game
            
        return False, None
        
    def handle_mouse(self,event):
        """
        This function handles mouse event which are send from the update function.
        """
        if self.focus == False:
            event.dict['pos'] = (event.dict['pos'][0], event.dict['pos'][1]-self.screens[self.screen_current].widget.y)
            (query, self.focus) = self.screens[self.screen_current].widget.handle_mouse(event)
        else:
            (query, focus) = self.focus.handle_mouse(event)
            if focus == False:
                self.focus = False
        if  query != False:
            reply = self.screens[self.screen_current].callback(query)
            self.handle_reply(reply)
        #remove the event for performance, maybe it is useless
        del(event)
        
    def handle_keys(self,event):
        """
        This function handles keyboard event which are send from the update function.
        """
        #TODO : a complete navigation system with the keyboard.
        reply = False
        query = False
        if self.focus:
            (query, focus) = self.focus.handle_keys(event)
            if focus == False:
                self.focus = False
            if  query != False:
                reply = self.screens[self.screen_current].callback(query)
                self.handle_reply(reply)
        if self.focus == False and (not reply and not query):
            if event.dict['key'] == pygame.K_ESCAPE:
                self.handle_reply("goto:back")
        #remove the event for performance, maybe it is useless
        del(event)
                
    def handle_reply(self,reply):
        #print type(reply)
        if type(reply) == str:
            if reply.split(':')[0] == 'goto':
                animation = True
                old_surface = self.screens[self.screen_current].widget.draw()
                oldy = self.screens[self.screen_current].widget.y
                indent_title = self.screens[self.screen_current].indent_title
                name = self.screens[self.screen_current].name
                if reply.split(':')[1] == 'back':
                    animation = self.screen_back()
                else:
                    self.screen_history.append(self.screen_current)
                    self.screen_current = reply.split(':')[1]
                if animation:
                    new_surface = self.screens[self.screen_current].widget.draw()

                    text = loaders.text(name, fonts['mono']['10']).convert()
                    text.fill(pygame.color.Color("black"))
                    text.set_colorkey(pygame.color.Color("black"))
                    text.blit(loaders.text(name, fonts['mono']['10']), (0,0))

                    for i in range(0, 10):
                        time.sleep(1.00/float(config.general['MAX_FPS']))
                        self.screen.blit(self.background, (0,0))
                        text.set_alpha( (i*(- 1) + 10) *250/10)
                        self.screen.blit(text, (indent_title,10))
                        self.screen.blit(old_surface, (optimize_size((i*8*10, 0))[0],oldy))
                        pygame.display.update()

                    text = loaders.text(self.screens[self.screen_current].name, fonts['mono']['10']).convert()
                    text.fill(pygame.color.Color("black"))
                    text.set_colorkey(pygame.color.Color("black"))
                    text.blit(loaders.text(self.screens[self.screen_current].name, fonts['mono']['10']), (0,0))

                    for i in range(0, 10):
                        time.sleep(1.00/float(config.general['MAX_FPS']))
                        self.screen.blit(self.background, (0,0))
                        text.set_alpha(i*250/10)
                        self.screen.blit(text, (self.screens[self.screen_current].indent_title,10))
                        self.screen.blit(new_surface, 
                            (optimize_size((i*8*10-800, 0))[0],
                            self.screens[self.screen_current].widget.y))
                        pygame.display.update()
                    self.update_youhere()
                    pygame.event.clear()

        elif reply != None:
            if reply == True:
                self.state = "menu"
            else:
                self.state = "menu"
                self.game = reply

    def screen_back(self):
        if len(self.screen_history) > 0:
            self.screen_current = self.screen_history[-1]
            del self.screen_history[-1]
            return True
        return False

    def update_youhere(self):
        screen_list = ""
        for screen in self.screen_history :
            screen_list += screen + "/"
        screen_list += self.screen_current + "/"
        self.here = loaders.text("> " + _("you are here :") + screen_list, fonts['mono']['30'])





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
