################################################################################
# copyright 2009 xapantu <xapantu@gmail.com>                                   #
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
from pygame.locals import USEREVENT, QUIT
from math import sin, cos
from time import time
import os
import pygame
import time
import xml.dom.minidom

#Our modules
from usf_modules.loaders import image
from usf_modules.config import (
        config,
        sound_config,
        save_conf,
        load_config,
        save_sound_conf,
        load_sound_config,
        save_keys_conf,
        load_key_config
        )
import usf_modules.controls
import entity_skin
from debug_utils import LOG
from usf_modules.game import Game
from usf_modules.config import xdg_config_home

#Gui modules
from usf_modules.widget import Widget
from usf_modules.widget_label import WidgetLabel
from usf_modules.widget_icon import WidgetIcon
from usf_modules.widget_credits import WidgetCredits
from usf_modules.gui_event import (
        level,
        exec_event
        )
class Gui:
    """
    Main class of the GUI
    In this class, there are the function update which is called everytime
    """
    # entries from list.usf.gui will be in file_gui
    file_gui = []
    button_active = 0
    widget_list={}
    parent_screen = {}
    screen_current = "main.usfgui"
    state="menu"
    # function which is called everytime
    def update(self, state, game, controls):
        #wait for an event (mouse or keyboard)
        eventcurrent = pygame.event.wait()
        #draw background
        #if(eventcurrent.type== pygame.KEYDOWN):
        #    print eventcurrent.dict['key']
        self.screen.blit(self.image,(0,0))
        #if it is a mouse event, reset the active button
        if(eventcurrent.type== pygame.MOUSEBUTTONUP or eventcurrent.type== pygame.MOUSEMOTION):
            self.widget_list[self.screen_current][self.button_active].state = "norm"
            mousex = eventcurrent.dict['pos'][0]
            mousey = eventcurrent.dict['pos'][1]
        if(eventcurrent.type== pygame.KEYDOWN and (eventcurrent.dict['key'] == 274 or eventcurrent.dict['key'] == 273 or eventcurrent.dict['key'] == 13 or eventcurrent.dict['key'] == 27)):
            # idem
            self.widget_list[self.screen_current][self.button_active].state = "norm"
            #to up and down items
            if(eventcurrent.dict['key'] == 274):
                if(self.button_active <len(self.widget_list[self.screen_current])-1):
                    self.button_active += 1
                else:
                    self.button_active = 0
                self.widget_list[self.screen_current][self.button_active].state = "hover"
            elif(eventcurrent.dict['key'] == 273):
                if(self.button_active > 0):
                    self.button_active-=1
                else:
                    self.button_active = len(self.widget_list[self.screen_current])-1
                self.widget_list[self.screen_current][self.button_active].state = "hover"
            # to valid item current
            if(eventcurrent.dict['key'] == 27):
                print "parent"
                self.goto_screen(self.parent_screen[self.screen_current])
                return False, None
            if(eventcurrent.dict['key'] == 13):
                widget_action = self.widget_list[self.screen_current][self.button_active].action
                if(widget_action.split(":")[0] == "goto"):
                    self.goto_screen(widget_action.split(":")[1])
                    return False, None
                exec widget_action
                #if the game start
                if(widget_action=="game = self.launch_game(game)"):
                    self.state = "game"
                    return True, game
        #if it is a mouse event, define which is the active item
        for i in range (0, len(self.widget_list[self.screen_current])):
            if(eventcurrent.type== pygame.MOUSEBUTTONUP or eventcurrent.type== pygame.MOUSEMOTION):
                widgetx = self.widget_list[self.screen_current][i].posx
                widgety = self.widget_list[self.screen_current][i].posy
                if(mousex>=widgetx and mousex<=self.widget_list[self.screen_current][i].sizex + widgetx):
                    if(mousey>=widgety and mousey<=self.widget_list[self.screen_current][i].sizey + widgety):
                        if(eventcurrent.type== pygame.MOUSEBUTTONUP):
                            print "click on "+self.widget_list[self.screen_current][i].name
                            widget_action = self.widget_list[self.screen_current][self.button_active].action
                            if(widget_action.split(":")[0] == "goto"):
                                self.goto_screen(widget_action.split(":")[1])
                                return False, None
                            exec widget_action
                            if(widget_action == ""):
                                exec_event(self.widget_list[self.screen_current][i].name)
                            #if the game start
                            if(widget_action=="game = self.launch_game(game)"):
                                self.state = "game"
                                return True, game
                        elif(eventcurrent.type== pygame.MOUSEMOTION):
                            self.widget_list[self.screen_current][i].state = "hover"
                            self.button_active = i
            #draw items at once
            self.widget_list[self.screen_current][i].draw()
        return False, None
    def __init__(self, surface): 
        self.characters = []
        self.players = [None, None, None, None]
        self.state = 'menu'
        self.levels = []
        self.level = 0
        self.screen = surface
        self.sizex = self.screen.get_width()
        self.sizey = self.screen.get_height()
        self.key_list={}
        xml_file = xml.dom.minidom.parse(config['MEDIA_DIRECTORY']+
            os.sep+
            'gui'+
            os.sep+
            'list.usfgui').getElementsByTagName("gui")[0]
        for i in range (0, len(xml_file.childNodes)):
            try:
                if(xml_file.childNodes[i].tagName == "menu"):
                    self.load_from_xml(xml_file.childNodes[i].childNodes[0].nodeValue)
            except:
                continue
        #load background image
        self.image = pygame.image.load(config['MEDIA_DIRECTORY']+
            os.sep+
            'gui'+
            os.sep+
            config['THEME']+
            os.sep+
            'background.png').convert()
        self.image = pygame.transform.scale(self.image, (self.sizex, self.sizey))
        
    #function to launch the game
    def launch_game(self, game):
        game = Game(
            self.screen,
            "BiX_level",
            ["characters/boogy-t", "characters/boogy-t", None, None]
        )
        self.state="game"
        return game
    def load_from_xml(self, filename):
        self.widget_list[filename] = []
        xml_file = xml.dom.minidom.parse(config['MEDIA_DIRECTORY']+
            os.sep+
            'gui'+
            os.sep+ filename).getElementsByTagName("gui")[0]
        for i in range (0, len(xml_file.childNodes)):
            try:
                if(xml_file.childNodes[i].tagName == "label"):
                    self.widget_list[filename].append(WidgetLabel(self.screen))
                    self.widget_list[filename][len(self.widget_list[filename])-1].name =xml_file.childNodes[i].getAttribute("id")
                    self.widget_list[filename][len(self.widget_list[filename])-1].text =xml_file.childNodes[i].getAttribute("value")
                    self.widget_list[filename][len(self.widget_list[filename])-1].posx =self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("posx"))/100
                    self.widget_list[filename][len(self.widget_list[filename])-1].posy =self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("posy"))/100
                if(xml_file.childNodes[i].tagName == "credits"):
                    self.widget_list[filename].append(WidgetCredits(self.screen))
                    self.widget_list[filename][len(self.widget_list[filename])-1].name =xml_file.childNodes[i].getAttribute("id")
                    self.widget_list[filename][len(self.widget_list[filename])-1].text =xml_file.childNodes[i].getAttribute("value")
                    self.widget_list[filename][len(self.widget_list[filename])-1].set_sizex(self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("sizex"))/100)
                    self.widget_list[filename][len(self.widget_list[filename])-1].set_sizey(self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("sizey"))/100)
                    self.widget_list[filename][len(self.widget_list[filename])-1].posx =self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("posx"))/100
                    self.widget_list[filename][len(self.widget_list[filename])-1].posy =self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("posy"))/100
                if(xml_file.childNodes[i].tagName == "button"):
                    self.widget_list[filename].append(WidgetIcon(self.screen))
                    self.widget_list[filename][len(self.widget_list[filename])-1].name =xml_file.childNodes[i].getAttribute("id")
                    self.widget_list[filename][len(self.widget_list[filename])-1].text =xml_file.childNodes[i].getAttribute("value")
                    self.widget_list[filename][len(self.widget_list[filename])-1].set_sizex(self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("sizex"))/100)
                    self.widget_list[filename][len(self.widget_list[filename])-1].set_sizey(self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("sizey"))/100)
                    self.widget_list[filename][len(self.widget_list[filename])-1].posx =self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("posx"))/100
                    self.widget_list[filename][len(self.widget_list[filename])-1].posy =self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("posy"))/100
                    self.widget_list[filename][len(self.widget_list[filename])-1].action =xml_file.childNodes[i].getAttribute("action")
                if(xml_file.childNodes[i].tagName == "parent"):
                    self.parent_screen[filename] = xml_file.childNodes[i].childNodes[0].nodeValue
            except AttributeError:
                continue
    def goto_screen(self,screen):
        self.screen_current = screen
        self.button_active = 0
        #draw new screen
        self.screen.blit(self.image,(0,0))
        for i in range (0, len(self.widget_list[self.screen_current])):
            #draw items at once
            self.widget_list[self.screen_current][i].draw()
