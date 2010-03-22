#i###############################################################################
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
from pygame.locals import USEREVENT, QUIT
from math import sin, cos
from time import time
import os
import time
import xml.dom.minidom
import logging

# Our modules
from loaders import image

from enums import reverse_keymap
from config import Config

config = Config.getInstance()

import usf.controls
import entity_skin
from usf.game import Game
import usf.controls
from usf import loaders
# Gui modules
from widgets import (Widget, WidgetLabel, WidgetIcon, WidgetParagraph,
                     WidgetImage, WidgetImageButton, WidgetTextarea,
                     WidgetCheckbox, WidgetCoverflow)

#translation
import translation


class Gui(object):
    """
    Main class of the GUI. Init and maintain all menus and widgets.

    """
    # entries from list.usf.gui will be in file_gui
    file_gui = []
    button_active = 0
    widgetselect = -1
    widget_list={}
    parent_screen = {}
    screen_current = "main.usfgui"
    state="menu"
    level = "BiX_level"
    character = []
    game_data = {}
    level_current=0
    screen_shot = None
    game = None
    widget_list_order = {}
    widget_anim = []
    dialog = {}
    last_event = 0
    background_alpha = 0

    def update(self, state, game, controls, eventcurrent=None):
        """
        Update the screen state based on user inputs.

        """
        global skin
        if time.time() > self.last_event +skin.background_duration[self.image] and self.image+1<len(skin.background):
            self.image +=1
            self.last_event = time.time()
        elif time.time() > self.last_event +skin.background_duration[self.image]:
            self.image = 0
            self.last_event = time.time()
        if game != None and game.ingame == False and self.screen_current=="ingame.usfgui":
            self.state = "menu"
            self.goto_screen("main.usfgui")
            self.background_alpha = 255
        self.controls = controls
        if self.screen_shot == None and self.state == "game":
            self.screen_shot = self.screen.copy()
            self.background_alpha = 255
        self.game = game
        #for performance problem if no widget are animated wait for an event
        """if(eventcurrent == None and len(self.widget_anim) == 0):
            #wait for an event (mouse or keyboard)
            eventcurrent = pygame.event.wait()
        if(eventcurrent != None):
            result =  self.exec_event(eventcurrent)
            if(result == "return True, self.game"):
                return True, self.game
            elif(result == "return False, None"):
                return False, None
            self.draw_screen()
            exec result"""
        time.sleep(1.00/float(config.general['MAX_FPS']))
        for widget in self.widget_anim:
            self.widget_list[self.screen_current][widget].click("1")
        while(True):
            eventcurrent = pygame.event.poll()
            if eventcurrent.type == pygame.QUIT:
                pygame.event.post( pygame.event.Event(QUIT) )
                break
            elif eventcurrent.type != pygame.NOEVENT:
                result =  self.exec_event(eventcurrent)
                if(result == "return True, self.game"):
                    return True, self.game
                elif(result == "return False, None"):
                    return False, None
                exec result
            else:
                break
        self.draw_screen()
        return False, None

    def __init__(self, surface):
        """
        Initialize menues from xml files, loading every characters and levels
        to get their previews, initializing menu state.

        """
        global skin
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
                    config.data_dir,
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
                #logging.debug( "character "+file+" created.")
            except OSError, e:
                if e.errno is 20:
                    pass
                else:
                    raise
            except IOError, e:
                logging.debug(file+" is not a valid character directory.", 3)
                #raise
                #logging.debug(e)
                pass
        #create a level image for every directory in the level directory.
        files = os.listdir(
                os.path.join(
                    config.data_dir,
                    'levels'
                    )
                )
        files.sort()
        for file in files:
            try:
                if '.xml' in file :
                    self.game_data['level_name'].append(file.replace(".xml",""))
            except :
                #logging.debug(file+" is not a valid level.")
                raise
                pass
        self.screen = surface
        self.sizex = self.screen.get_width()
        self.sizey = self.screen.get_height()
        self.key_list={}
        xml_file = xml.dom.minidom.parse(config.data_dir+
            os.sep+
            'gui'+
            os.sep+
            'list.usfgui').getElementsByTagName("gui")[0]
        for i in range (0, len(xml_file.childNodes)):
            try:
                if(xml_file.childNodes[i].tagName == "menu"):
                   self.load_from_xml(xml_file.childNodes[i].childNodes[0].nodeValue)
                if(xml_file.childNodes[i].tagName == "dialog"):
                   self.dialog[xml_file.childNodes[i].childNodes[0].nodeValue] = Dialog(
                    self.screen,xml_file.childNodes[i].childNodes[0].nodeValue)
                   self.load_from_xml(xml_file.childNodes[i].childNodes[0].nodeValue)
            except:
                continue
        #load background image
        
        self.image = 0
        self.draw_screen(True)

    def launch_game(self, game):
        """
        Function to launch the game, use precedant user choices to initiate the
        game with level and characters selected.

        """

        players = [
        self.game_data['character_file'][p]
        for p in self.players if p != -1
        ]
        for i in range(0,3):
            if self.widget_list['characters.usfgui']["ai" + str(i)].text == "True":
                players[i] = players[i].replace("characters/", "characters/AI")
        game = Game(
            self.screen,
            self.game_data['level_name'][self.level_current],
            players
        )

        self.goto_screen("ingame.usfgui")
        self.state="game"
        return game

    def load_from_xml(self, filename):
        """
        init all widget of a menu using the xml file.

        """
        global skin
        self.widget_list[filename] = {}
        self.widget_list_order[filename] = []
        xml_file = xml.dom.minidom.parse(config.data_dir+
            os.sep+
            'gui'+
            os.sep+ filename).getElementsByTagName("gui")[0]
        for i in range (0, len(xml_file.childNodes)):
            try:
                if xml_file.childNodes[i].tagName != "parent":
                    id_current = xml_file.childNodes[i].getAttribute("id")
                    self.widget_list_order[filename].append(id_current)
                    if(xml_file.childNodes[i].tagName == "label"):
                        self.widget_list[filename][id_current] = WidgetLabel(self.screen)
                    elif(xml_file.childNodes[i].tagName == "p"):
                        self.widget_list[filename][id_current] = WidgetParagraph(self.screen)
                        #FIXME : remove these two line
                        self.widget_list[filename][id_current].set_sizex(self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("sizex"))/100)
                        self.widget_list[filename][id_current].set_sizey(self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("sizey"))/100)
                        self.widget_list[filename][id_current].setParagraph(xml_file.childNodes[i].childNodes[0].nodeValue)
                    elif(xml_file.childNodes[i].tagName == "imagebutton"):
                        self.widget_list[filename][id_current] = WidgetImageButton(self.screen)
                        self.widget_list[filename][id_current].action=xml_file.childNodes[i].getAttribute("action")
                    elif(xml_file.childNodes[i].tagName == "coverflow"):
                        self.widget_list[filename][id_current] = WidgetCoverflow(self.screen)
                    elif(xml_file.childNodes[i].tagName == "checkbox"):
                        self.widget_list[filename][id_current] = WidgetCheckbox(self.screen)
                        self.widget_list[filename][id_current].action=xml_file.childNodes[i].getAttribute("action")
                    elif(xml_file.childNodes[i].tagName == "textarea"):
                        self.widget_list[filename][id_current] = WidgetTextarea(self.screen)
                        self.widget_list[filename][id_current].str_len =int(xml_file.childNodes[i].getAttribute("nb"))
                        #it is for label and image couldn't be select
                        self.widget_list[filename][id_current].action=xml_file.childNodes[i].getAttribute("action")
                    elif(xml_file.childNodes[i].tagName == "button"):
                        self.widget_list[filename][id_current] = WidgetIcon(self.screen)
                        self.widget_list[filename][id_current].action=xml_file.childNodes[i].getAttribute("action")
                    elif(xml_file.childNodes[i].tagName == "image"):
                        self.widget_list[filename][id_current] = WidgetImage(self.screen)
                    if(self.dialog.has_key(filename)):
                        self.widget_list[filename][id_current].posx = skin.dialog['posx']+config.general['WIDTH']/40 + skin.dialog['sizex']*int(xml_file.childNodes[i].getAttribute("posx"))/100
                        self.widget_list[filename][id_current].posy = skin.dialog['posy'] +config.general['HEIGHT']/20 + skin.dialog['sizey']*int(xml_file.childNodes[i].getAttribute("posy"))/100
                    else:
                        self.widget_list[filename][id_current].posx=self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("posx"))/100
                        self.widget_list[filename][id_current].posy=self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("posy"))/100
                    try:
                        self.widget_list[filename][id_current].set_sizex(self.screen.get_width()*int(xml_file.childNodes[i].getAttribute("sizex"))/100)
                        self.widget_list[filename][id_current].set_sizey(self.screen.get_height()*int(xml_file.childNodes[i].getAttribute("sizey"))/100)
                    except:
                        self.widget_list[filename][id_current].set_sizex(0)
                        self.widget_list[filename][id_current].set_sizey(0)
                    if xml_file.childNodes[i].hasAttribute("value"):
                        self.widget_list[filename][id_current].setText(_(xml_file.childNodes[i].getAttribute("value")))
                    else:
                        self.widget_list[filename][id_current].setText(_(xml_file.childNodes[i].childNodes[0].nodeValue))
                elif(xml_file.childNodes[i].tagName == "parent"):
                    self.parent_screen[filename] =xml_file.childNodes[i].childNodes[0].nodeValue
            except AttributeError:
                continue
    def goto_screen(self,screen):
        """
        menu goes to the specified screen.

        """
        if(self.dialog.has_key(self.screen_current)):
            self.dialog[self.screen_current].show()
        if(self.dialog.has_key(screen)):
            self.screen_current = screen
            self.dialog[self.screen_current].show()
        else:
            for i in range(0,5):
                start = time.time()
                self.draw_screen(True,i*50)
                time.sleep(1.00/float(config.general['MAX_FPS']))
            self.screen_current = screen
            for i in range(0,5):
                start = time.time()
                self.draw_screen(True,(i*-1+5)*50)
                time.sleep(1.00/float(config.general['MAX_FPS']))
        self.button_active = 0
        self.widgetselect = -1
        self.widget_anim=[]
        for widget in self.widget_list[screen].keys():
            if self.widget_list[screen][widget].anim:
                self.widget_anim.append(widget)
        self.draw_screen(True)
        #draw new screen

    def exec_event(self, eventcurrent):
        """
        function whiwh processes event

        """
        str_return = ""
        if type(eventcurrent) is not str:
            if(eventcurrent.type is pygame.KEYUP):
                if(eventcurrent.dict['key'] == pygame.K_DOWN):
                    self.select(True)
                if(eventcurrent.dict['key'] == pygame.K_UP):
                    self.select(False)
                if(eventcurrent.dict['key'] == pygame.K_ESCAPE):
                    try:
                        self.widget_list[self.parent_screen[self.screen_current]]
                        self.goto_screen(self.parent_screen[self.screen_current])
                    except:
                        exec self.parent_screen[self.screen_current]
            if(eventcurrent.type==pygame.MOUSEMOTION or eventcurrent.type==pygame.MOUSEBUTTONUP or eventcurrent.type==pygame.MOUSEBUTTONDOWN):
                mousex = eventcurrent.dict['pos'][0]
                mousey = eventcurrent.dict['pos'][1]
                for widget in self.widget_list[self.screen_current].values():
                    widgetx = widget.posx
                    widgety = widget.posy
                    if(mousex>=widgetx and mousex<=widget.sizex + widgetx):
                        if(mousey>=widgety and mousey<=widget.sizey + widgety):
                            if(eventcurrent.type==pygame.MOUSEMOTION):
                                str_return = self.select(self.widget_list_order[self.screen_current].index(self.widget_list[self.screen_current].keys()[self.widget_list[self.screen_current].values().index(widget)]))
                            elif(eventcurrent.type==pygame.MOUSEBUTTONUP):
                                str_return = self.valid(self.widget_list_order[self.screen_current].index(self.widget_list[self.screen_current].keys()[self.widget_list[self.screen_current].values().index(widget)]))
                            widget.click(eventcurrent)
                            break
            return str_return

    def select(self,sens):
        """
        function which select a widget

        """
        if(type(sens) == bool):
            if sens:
                if(self.widgetselect < len(self.widget_list_order[self.screen_current])-1):
                    self.widget_list[self.screen_current][self.widget_list_order[self.screen_current][self.widgetselect]].state("norm")
                    self.widgetselect += 1
                    self.widget_list[self.screen_current][self.widget_list_order[self.screen_current][self.widgetselect]].state("hover")
            else:
                if(self.widgetselect > 0):
                    self.widget_list[self.screen_current][self.widget_list_order[self.screen_current][self.widgetselect]].state("norm")
                    self.widgetselect -= 1
                    self.widget_list[self.screen_current][self.widget_list_order[self.screen_current][self.widgetselect]].state("hover")
        else:
            self.widget_list[self.screen_current][self.widget_list_order[self.screen_current][self.widgetselect]].state("norm")
            self.widgetselect = sens
            self.widget_list[self.screen_current][self.widget_list_order[self.screen_current][self.widgetselect]].state("hover")
        return ""

    def valid(self,i):
        """
        /!\ documentation #TODO

        """
        str_return = ""
        id_widget = self.widget_list_order[self.screen_current][i]
        self.widget_list[self.screen_current][self.widget_list_order[self.screen_current][self.widgetselect]].state("norm")
        widget_action =self.widget_list[self.screen_current][self.widget_list_order[self.screen_current][i]].action

        ############################## CUSTOM ACTION ###########################
        if(id_widget=="nextlevel"):
            if(self.level_current< len(self.game_data['level_name'])-1):
                self.level_current += 1
                self.widget_list[self.screen_current]["level_name"].setText(
                    self.game_data['level_name'][self.level_current]
                    )
                self.widget_list[self.screen_current]['level'].setText(
                    os.path.join(
                        "gui",
                        "image",
                        self.game_data['level_name'][self.level_current]+".png"
                        )
                    )
        elif(id_widget=="prevlevel"):
            if(self.level_current>0):
                self.level_current -= 1
                self.widget_list[self.screen_current]["level_name"].setText(
                    self.game_data['level_name'][self.level_current]
                )
                self.widget_list[self.screen_current]['level'].setText(
                os.path.join(
                    "gui",
                    "image",
                    self.game_data['level_name'][self.level_current]+".png"
                    )
                )
        elif("prev" in id_widget or "next" in id_widget):
            if("prev" in id_widget):
                player = id_widget.replace("prev", "")
                if(self.players[int(player)] != -1):
                    self.players[int(player)] -= 1
            else:
                player = id_widget.replace("next", "")
                if(self.players[int(player)] < len(self.game_data['character_name'])-1):
                    self.players[int(player)] += 1
            if(self.players[int(player)]==-1):
                self.widget_list[self.screen_current]['player' + player].setText("gui" + os.sep +"image" + os.sep +"none.png")
            else:
                dir_player = self.game_data['character_file'][self.players[int(player)]]
                self.widget_list[self.screen_current]['player' + player].setText( dir_player + os.sep+self.game_data['character_file'][self.players[int(player)]].replace("characters"+os.sep, "") + "-portrait.png")
        elif(id_widget=="quit"):
            pygame.event.post( pygame.event.Event(QUIT) )
        elif(id_widget=="quitgame"):
            self.game = None
            self.state = "menu"
            self.goto_screen("main.usfgui")
            str_return  = "return False, None"
        elif(id_widget=="fullscreen"):
            if(config.general['FULLSCREEN'] == "True"):
                config.general['FULLSCREEN'] = "False"
                self.widget_list[self.screen_current]['fullscreen'].text = "False"
            else:
                config.general['FULLSCREEN'] = "True"
                self.widget_list[self.screen_current]['fullscreen'].text = "True"
        elif(id_widget=="gotolevel"):
            nb_player = 0
            for p in [p for p in self.players if p is not -1]:
                nb_player += 1
            if nb_player > 1:
                self.goto_screen("level.usfgui")
            else:
                self.goto_screen("dialog_characters.usfgui")
        elif(id_widget=="musicp"):
            config.audio['MUSIC_VOLUME'] += 5
            self.widget_list[self.screen_current]['music'].text = str(config.audio['MUSIC_VOLUME'])
        elif(id_widget=="musicm"):
            config.audio['MUSIC_VOLUME'] -= 5
            self.widget_list[self.screen_current]['music'].text = str(config.audio['MUSIC_VOLUME'])
        elif(id_widget=="soundp"):
            config.audio['SOUND_VOLUME'] += 5
            self.widget_list[self.screen_current]["sounds"].text = str(config.audio['SOUND_VOLUME'])
        elif(id_widget=="soundm"):
            config.audio['SOUND_VOLUME'] -= 5
            self.widget_list[self.screen_current]["sounds"].text = str(config.audio['SOUND_VOLUME'])
        elif(id_widget=="launch_game"):
            self.game = self.launch_game(self.game)
            str_return  = "return True, self.game"
        elif(id_widget=="resume_game"):
            self.screen_shot = None
            str_return  = "return True, self.game"
        elif(id_widget=="full_check"):
            if self.widget_list[self.screen_current][id_widget].text == "True" :
                config.general['FULLSCREEN'] = "False"
                pygame.display.toggle_fullscreen()
                self.widget_list[self.screen_current][id_widget].setText("")
            else:
                config.general['FULLSCREEN'] = "True"
                pygame.display.toggle_fullscreen()
                self.widget_list[self.screen_current][id_widget].setText("True")
        elif "ai" in id_widget :
            if self.widget_list[self.screen_current][id_widget].text == "True" :
                self.widget_list[self.screen_current][id_widget].setText("")
            else:
                self.widget_list[self.screen_current][id_widget].setText("True")
        else:
            if(widget_action.split(":")[0] == "goto"):
                self.goto_screen(widget_action.split(":")[1])
            elif(widget_action.split(":")[0] == "anim"):
                self.anim(widget_action.split(":")[1], widget_action.split(":")[2], self.controls)
            elif(widget_action == ""):
                self.exec_event(self.widget_list[self.screen_current].values()[i].name)
            else:
                exec widget_action
        #to exec an action in update()
        return str_return

    def anim(self, widget_name, argument, controls):
        """
        /!\ documentation #TODO

        """
        if("txt" in widget_name):
            self.widget_list[self.screen_current][widget_name].text = _("Press a key")
            #update screen
            self.update("",None,"",pygame.event.Event(pygame.USEREVENT, {}))
            pygame.display.update()
            for len_str in range(0,self.widget_list[self.screen_current][widget_name].str_len):
                event_current = pygame.event.wait()
                while(event_current.type != pygame.KEYDOWN):
                    self.update("",None,"",event_current)
                    event_current = pygame.event.wait()
                    pygame.display.update()

                self.widget_list[self.screen_current][widget_name].text  = \
                  pygame.key.name(event_current.dict['key'])

                config.keyboard[widget_name.replace('txtconfig', '')] = reverse_keymap[event_current.dict['key']]
        else :
            while(True):
                time.sleep(0.04)
                self.screen.blit(self.image,(0,0))
                for j in range (0, len(self.widget_list[self.screen_current].values())):
                    #draw items at once
                    self.widget_list[self.screen_current].values()[j].draw()
                pygame.display.update()
                if not self.widget_list[self.screen_current][widget_name].click(argument): break

    def draw_screen(self,update = False, opacity = None):
        """
        Draw the menu to the screen, use a screenshot of the game to display
        the menu "ingame".

        """
        global skin
        back = loaders.image(
            config.data_dir+
            os.sep+
            "gui"+
            os.sep +
            config.general['THEME']+
            os.sep+
            skin.background[self.image], scale=(config.general['WIDTH'], config.general['HEIGHT'])
            )[0].convert()
        back.set_alpha(250)
        if(self.state == "game"):
            self.screen.blit(self.screen_shot,(0,0))
        if not self.dialog.has_key(self.screen_current):
            self.screen.blit(back,(0,0))

        for dialog in [dialog for dialog in self.dialog.values() if dialog.state is True]:
        #    draw items at once
            dialog.draw()
        for widget in self.widget_list[self.screen_current].values():
            #draw items at once
            widget.draw()
        if opacity is not None:
            self.background_alpha = opacity
            back.set_alpha(opacity)
            self.screen.blit(back,(0,0))
        if update : pygame.display.update()

class Skin (object):
    dialog = {}
    color = None
    background = []
    background_duration = []
    def __init__(self):
        xml_file = xml.dom.minidom.parse(config.data_dir+
            os.sep+
            'gui'+
            os.sep+ config.general['THEME'] + os.sep + "theme.xml").getElementsByTagName("theme")[0]
        self.color = pygame.color.Color("white")
        for node in xml_file.childNodes:
            try:
                if node.tagName == "color":
                    self.color = pygame.color.Color(str(node.getAttribute("value")))
                elif node.tagName == "dialog":
                    self.dialog['sizex'] = int(node.getAttribute("sizex"))*config.general['WIDTH']/100
                    self.dialog['sizey'] = int(node.getAttribute("sizey"))*config.general['HEIGHT']/100
                    self.dialog['posx'] = int(node.getAttribute("posx"))*config.general['WIDTH']/100
                    self.dialog['posy'] = int(node.getAttribute("posy"))*config.general['HEIGHT']/100
                elif node.tagName == "background":
                    for child_node in node.childNodes:
                        try:
                            if child_node.tagName == "img":
                                self.background.append(child_node.getAttribute("src"))
                                self.background_duration.append(float(child_node.getAttribute("time")))
                        except:
                            pass
            except:
                pass
skin = Skin()
class Dialog(object):
    state = False
    image = None
    def __init__(self, screen, name):
        global skin
        self.background = loaders.image(
            config.data_dir+
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
