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
from pygame.locals import USEREVENT, QUIT
from math import sin, cos
from time import time
import os
import pygame
import time
import xml.dom.minidom

# Our modules
from usf_modules.loaders import image
from usf_modules.config import (
        config,
        sound_config,
        save_conf,
        load_config,
        save_sound_conf,
        load_sound_config,
        save_keys_conf,
        load_key_config,
        reverse_keymap
        )

import usf_modules.controls
import entity_skin
from debug_utils import LOG
from usf_modules.game import Game
from usf_modules.config import xdg_config_home
import usf_modules.controls

# Gui modules
from usf_modules.widget import Widget
from usf_modules.widget_label import WidgetLabel
from usf_modules.widget_icon import WidgetIcon
from usf_modules.widget_credits import WidgetCredits
from usf_modules.widget_image import WidgetImage
from usf_modules.widget_image_button import WidgetImageButton
from usf_modules.widget_textarea import WidgetTextarea


#translation
import translation
class Gui(object):
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
    level = "BiX_level"
    character = []
    game_data = {}
    level_current=0
    screenshot = None
    # function which is called everytime
    def update(self, state, game, controls, eventcurrent=None):
        if(game !=None):
            if(self.screenshot == None):
                #take a screenshot of the current game before draw
                self.screenshot = self.screen.copy()
        if(eventcurrent == None):
            #wait for an event (mouse or keyboard)
            eventcurrent = pygame.event.wait()
        else:
            print "event send"
        #draw background
        #if(eventcurrent.type== pygame.KEYDOWN):
        #    print eventcurrent.dict['key']
        if(self.screenshot != None):
            self.screen.blit(self.screenshot,(0,0))
            self.image.set_alpha(200)
        self.screen.blit(self.image,(0,0))
        #if it is a mouse event, reset the active button
        if(eventcurrent.type== pygame.MOUSEBUTTONUP or eventcurrent.type==pygame.MOUSEMOTION):
            self.widget_list[self.screen_current][self.button_active].state="norm"
            mousex = eventcurrent.dict['pos'][0]
            mousey = eventcurrent.dict['pos'][1]
        if(eventcurrent.type== pygame.KEYDOWN and (eventcurrent.dict['key'] ==274 or eventcurrent.dict['key'] == 273 or eventcurrent.dict['key'] == 13 or eventcurrent.dict['key'] == 27)):
            # idem
            self.widget_list[self.screen_current][self.button_active].state ="norm"
            #to up and down items
            if(eventcurrent.dict['key'] == 274):
                if(self.button_active<len(self.widget_list[self.screen_current])-1):
                    self.button_active += 1
                else:
                    self.button_active = 0
                self.widget_list[self.screen_current][self.button_active].state= "hover"
            elif(eventcurrent.dict['key'] == 273):
                if(self.button_active > 0):
                    self.button_active-=1
                else:
                    self.button_active =len(self.widget_list[self.screen_current])-1
                self.widget_list[self.screen_current][self.button_active].state= "hover"
            # to valid item current
            if(eventcurrent.dict['key'] == pygame.K_ESCAPE):
                try:
                    self.widget_list[self.parent_screen[self.screen_current]]
                    self.goto_screen(self.parent_screen[self.screen_current])
                except:
                    exec self.parent_screen[self.screen_current]
                    if(self.parent_screen[self.screen_current] == "self.screenshot=None"):
                            return True, game
                return False, None
            if(eventcurrent.dict['key'] == 13):
                widget_action =self.widget_list[self.screen_current][self.button_active].action
                if(widget_action.split(":")[0] == "goto"):
                    self.goto_screen(widget_action.split(":")[1])
                    return False, None
                if(widget_action.split(":")[0] == "anim"):
                    self.anim(widget_action.split(":")[1], widget_action.split(":")[2], controls)
                    return False, None
                exec widget_action
                if(widget_action == ""):
                   self.exec_event(self.widget_list[self.screen_current][i].name)
                #if the game start
                if(widget_action=="game = self.launch_game(game)"):
                    return True, game
                if(widget_action=="self.screenshot=None"):
                    return True, game
        #if it is a mouse event, define which is the active item
        for i in range (0, len(self.widget_list[self.screen_current])):
            if(eventcurrent.type== pygame.MOUSEBUTTONUP or eventcurrent.type==pygame.MOUSEMOTION):
                widgetx = self.widget_list[self.screen_current][i].posx
                widgety = self.widget_list[self.screen_current][i].posy
                if(mousex>=widgetx and mousex<=self.widget_list[self.screen_current][i].sizex + widgetx):
                    if(mousey>=widgety and mousey<=self.widget_list[self.screen_current][i].sizey + widgety):
                        if(eventcurrent.type== pygame.MOUSEBUTTONUP):
                            widget_action =self.widget_list[self.screen_current][self.button_active].action
                            if(widget_action.split(":")[0] == "goto"):
                                self.goto_screen(widget_action.split(":")[1])
                                return False, None
                            if(widget_action.split(":")[0] == "anim"):
                                self.anim(widget_action.split(":")[1], widget_action.split(":")[2], controls)
                                return False, None
                            exec widget_action
                            if(widget_action == ""):
                               self.exec_event(self.widget_list[self.screen_current][i].name)
                            #if the game start
                            if(widget_action=="game = self.launch_game(game)"):
                                return True, game
                            #if it is resume
                            if(widget_action=="self.screenshot=None"):
                                return True, game
                        elif(eventcurrent.type== pygame.MOUSEMOTION):
                            self.widget_list[self.screen_current][i].state ="hover"
                            self.button_active = i
            #draw items at once
            self.widget_list[self.screen_current][i].draw()
        return False, None

    def __init__(self, surface):
        self.characters = []
        self.players = [-1, -1, -1, -1]
        self.state = 'menu'
        self.levels = []
        self.level = 0
        self.game_data['character_file'] = []
        self.game_data['character_name'] = []
        self.game_data['level_name'] = []
        #create a character for every directory in the characters directory.
        files = os.listdir(
                os.path.join(
                    config['MEDIA_DIRECTORY'],
                    'characters'
                    )
                )
        files.sort()
        for file in files:
            try:
                self.game_data['character_file'].append(os.path.join(
                                'characters',
                                file
                                ))
                self.game_data['character_name'].append(entity_skin.Entity_skin(
                            os.path.join(
                                'characters',
                                file
                                )
                            ).name)
                #LOG().log( "character "+file+" created.")
            except OSError, e:
                if e.errno is 20:
                    pass
                else:
                    raise
            except IOError, e:
                LOG().log(file+" is not a valid character directory.", 3)
                #raise
                #LOG().log(e)
                pass
        #create a level image for every directory in the level directory.
        files = os.listdir(
                os.path.join(
                    config['MEDIA_DIRECTORY'],
                    'levels'
                    )
                )
        files.sort()
        for file in files:
            try:
                if '.xml' in file :
                    self.game_data['level_name'].append(file.replace(".xml",""))
            except :
                #LOG()(file+" is not a valid level.")
                raise
                pass
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
        self.image = pygame.transform.scale(self.image, (self.sizex,self.sizey))

    #function to launch the game
    def launch_game(self, game):
        self.goto_screen("ingame.usfgui")
        self.screenshot = None
        players = [None, None, None, None]
        for i in range (0, len(self.players)):
            if(self.players[i] != -1):
                players[i] = self.game_data['character_file'][self.players[i]]
        print players
        game = Game(
            self.screen,
            self.game_data['level_name'][self.level_current],
            players
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
                    self.widget_list[filename][len(self.widget_list[filename])-1].setText(_(xml_file.childNodes[i].getAttribute("value")))
                elif(xml_file.childNodes[i].tagName == "credits"):
                   self.widget_list[filename].append(WidgetCredits(self.screen))
                elif(xml_file.childNodes[i].tagName == "imagebutton"):
                   self.widget_list[filename].append(WidgetImageButton(self.screen))
                   self.widget_list[filename][len(self.widget_list[filename])-1].set_sizex(self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("sizex"))/100)
                   self.widget_list[filename][len(self.widget_list[filename])-1].set_sizey(self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("sizey"))/100)
                   self.widget_list[filename][len(self.widget_list[filename])-1].action=xml_file.childNodes[i].getAttribute("action")
                   self.widget_list[filename][len(self.widget_list[filename])-1].setText(xml_file.childNodes[i].getAttribute("value"))
                elif(xml_file.childNodes[i].tagName == "textarea"):
                   self.widget_list[filename].append(WidgetTextarea(self.screen))
                   self.widget_list[filename][len(self.widget_list[filename])-1].set_sizex(self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("sizex"))/100)
                   self.widget_list[filename][len(self.widget_list[filename])-1].set_sizey(self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("sizey"))/100)
                   self.widget_list[filename][len(self.widget_list[filename])-1].str_len =int(xml_file.childNodes[i].getAttribute("nb"))
                   self.widget_list[filename][len(self.widget_list[filename])-1].action=xml_file.childNodes[i].getAttribute("action")
                   self.widget_list[filename][len(self.widget_list[filename])-1].setText(_(xml_file.childNodes[i].getAttribute("value")))
                elif(xml_file.childNodes[i].tagName == "button"):
                   self.widget_list[filename].append(WidgetIcon(self.screen))
                   self.widget_list[filename][len(self.widget_list[filename])-1].set_sizex(self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("sizex"))/100)
                   self.widget_list[filename][len(self.widget_list[filename])-1].set_sizey(self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("sizey"))/100)
                   self.widget_list[filename][len(self.widget_list[filename])-1].action=xml_file.childNodes[i].getAttribute("action")
                   self.widget_list[filename][len(self.widget_list[filename])-1].setText(_(xml_file.childNodes[i].getAttribute("value")))
                elif(xml_file.childNodes[i].tagName == "image"):
                   self.widget_list[filename].append(WidgetImage(self.screen))
                   if(int(xml_file.childNodes[i].getAttribute("sizex")) != 0):
                       self.widget_list[filename][len(self.widget_list[filename])-1].set_sizex(self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("sizex"))/100)
                   else:
                       self.widget_list[filename][len(self.widget_list[filename])-1].set_sizex(self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("sizey"))/100)
                   self.widget_list[filename][len(self.widget_list[filename])-1].set_sizey(self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("sizey"))/100)
                   self.widget_list[filename][len(self.widget_list[filename])-1].setText(xml_file.childNodes[i].getAttribute("value").replace("/", os.sep))
                elif(xml_file.childNodes[i].tagName == "parent"):
                    self.parent_screen[filename] =xml_file.childNodes[i].childNodes[0].nodeValue
                if(xml_file.childNodes[i].tagName == "label" or xml_file.childNodes[i].tagName == "credits" or xml_file.childNodes[i].tagName =="button" or xml_file.childNodes[i].tagName == "image" or xml_file.childNodes[i].tagName == "imagebutton" or xml_file.childNodes[i].tagName == "textarea"):
                   self.widget_list[filename][len(self.widget_list[filename])-1].name=xml_file.childNodes[i].getAttribute("id")
                   self.widget_list[filename][len(self.widget_list[filename])-1].posx=self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("posx"))/100
                   self.widget_list[filename][len(self.widget_list[filename])-1].posy=self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("posy"))/100
            except AttributeError:
                continue

    def goto_screen(self,screen):
        self.screen_current = screen
        self.button_active = 0
        #draw new screen
        if(self.screenshot != None):
            self.screen.blit(self.screenshot,(0,0))
            self.image.set_alpha(200)
        self.screen.blit(self.image,(0,0))
        pygame.display.update()
        for i in range (0, len(self.widget_list[self.screen_current])):
            #draw items at once
            self.widget_list[self.screen_current][i].draw()
    #function for special event (if action =="")
    def exec_event(self, id_widget):
        print id_widget
        if(id_widget=="nextlevel"):
            if(self.level_current< len(self.game_data['level_name'])-1):
                self.level_current += 1
                i=0
                while(self.widget_list[self.screen_current][i].name != "level"):
                    i+=1
                #change level preview
                self.widget_list[self.screen_current][i].setText("gui" +os.sep + "image" + os.sep + self.game_data['level_name'][self.level_current] + ".png")
                i=0
                while(self.widget_list[self.screen_current][i].name !="level_name"):
                    i+=1
                #change level name
                self.widget_list[self.screen_current][i].text =self.game_data['level_name'][self.level_current]
        elif(id_widget=="prevlevel"):
            if(self.level_current>0):
                self.level_current -= 1
                i=0
                #dirty ?
                while(self.widget_list[self.screen_current][i].name !="level_name"):
                    i+=1
                self.widget_list[self.screen_current][i].text =self.game_data['level_name'][self.level_current]
                i=0
                #dirty ?
                while(self.widget_list[self.screen_current][i].name != "level"):
                    i+=1
                self.widget_list[self.screen_current][i].setText("gui" +os.sep + "image" + os.sep + self.game_data['level_name'][self.level_current] + ".png")
        elif("prev" in id_widget or "next" in id_widget):
            if("prev" in id_widget):
                player = id_widget.replace("prev", "")
                if(self.players[int(player)] != -1):
                    self.players[int(player)] -= 1
            else:
                player = id_widget.replace("next", "")
                if(self.players[int(player)] < len(self.game_data['character_name'])-1):
                    self.players[int(player)] += 1
            #dirty ?
            i=0
            while(self.widget_list[self.screen_current][i].name != "player" + player):
                i+=1
            if(self.players[int(player)]==-1):
                self.widget_list[self.screen_current][i].setText("gui" + os.sep +"image" + os.sep +"none.png")
            else:
                self.widget_list[self.screen_current][i].setText(self.game_data['character_file'][self.players[int(player)]] + os.sep+self.game_data['character_file'][self.players[int(player)]].replace("characters"+os.sep, "") + "-portrait.png")
        elif(id_widget=="quitgame"):
            self.screenshot=None
            self.goto_screen("main.usfgui")
        elif(id_widget=="fullscreen"):
            i=0
            while(self.widget_list[self.screen_current][i].name !="fullscreen"):
                i+=1
            if(config['FULLSCREEN']):
                config['FULLSCREEN'] = False
                self.widget_list[self.screen_current][i].text = "False"
            else:
                config['FULLSCREEN'] = True
                self.widget_list[self.screen_current][i].text = "True"
            save_conf()
        elif(id_widget=="musicp"):
            i=0
            while(self.widget_list[self.screen_current][i].name !="music"):
                i+=1
            sound_config['MUSIC_VOLUME'] += 5
            save_sound_conf()
            self.widget_list[self.screen_current][i].text = str(int(self.widget_list[self.screen_current][i].text) +5)
        elif(id_widget=="musicm"):
            i=0
            while(self.widget_list[self.screen_current][i].name !="music"):
                i+=1
            sound_config['MUSIC_VOLUME'] -= 5
            save_sound_conf()
            self.widget_list[self.screen_current][i].text = str(int(self.widget_list[self.screen_current][i].text) -5)
        elif(id_widget=="soundp"):
            i=0
            while(self.widget_list[self.screen_current][i].name !="sounds"):
                i+=1
            sound_config['SOUND_VOLUME'] += 5
            save_sound_conf()
            self.widget_list[self.screen_current][i].text = str(int(self.widget_list[self.screen_current][i].text) +5)
        elif(id_widget=="soundm"):
            i=0
            while(self.widget_list[self.screen_current][i].name !="sounds"):
                i+=1
            sound_config['SOUND_VOLUME'] -= 5
            save_sound_conf()
            self.widget_list[self.screen_current][i].text = str(int(self.widget_list[self.screen_current][i].text) -5)
    def anim(self, widget_name, argument, controls):
        i=0
        print widget_name
        #dirty ?
        while(self.widget_list[self.screen_current][i].name !=widget_name):
            i+=1
        if("txt" in widget_name):
            self.widget_list[self.screen_current][i].text = _("Press key")
            #update screen
            self.update("",None,"",pygame.event.Event(pygame.USEREVENT, {}))
            pygame.display.update()
            for len_str in range(0,self.widget_list[self.screen_current][i].str_len):
                event_current = pygame.event.wait()
                while(event_current.type != pygame.KEYDOWN):
                    print "send event to update()"
                    self.update("",None,"",event_current)
                    event_current = pygame.event.wait()
                    pygame.display.update()
                if(self.widget_list[self.screen_current][i].text==_("Press key")):
                    self.widget_list[self.screen_current][i].text = ""
                exec "self.widget_list[self.screen_current][i].text += pygame.key.name(pygame." + reverse_keymap[event_current.dict['key']] + ")"
                numcle = 0
                try:
                    while(controls.keys.values()[numcle] != widget_name.replace('txtconfig', '')):
                        numcle += 1
                    del controls.keys[controls.keys.keys()[numcle]]
                except:
                    pass
                controls.keys[event_current.dict['key']] = widget_name.replace('txtconfig', '')
                controls.save()
                
                print controls.keys
        else:
            while(True):
                time.sleep(0.04)
                self.screen.blit(self.image,(0,0))
                for j in range (0, len(self.widget_list[self.screen_current])):
                    #draw items at once
                    self.widget_list[self.screen_current][j].draw()
                pygame.display.update()
                if not self.widget_list[self.screen_current][i].click(argument): break
