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
import xml.dom.minidom
import pygame
from pygame.locals import *

import loaders
from config import Config

config_ = Config.getInstance()
general = config_.general
sound_config = config_.audio
keyboard_config = config_.keyboard
MEDIA_DIRECTORY = config_.data_dir

class Widget (object):
    """
    This class is the base of all other widget.
    """
    sizex = 0
    sizey = 0
    posx = 0
    posy = 0
    name = "name"
    action = "print 'click'"
    selectable = False
    text = ""
    anim = False
    color="white"
    def __init__(self, screen):
        self.game_font = pygame.font.Font(
            MEDIA_DIRECTORY +
            os.sep +
            "gui" +os.sep + general['THEME'] + os.sep +
            "font.otf", screen.get_height()/20)
        self.screen = screen
        xml_file = xml.dom.minidom.parse(MEDIA_DIRECTORY+
            os.sep+
            'gui'+
            os.sep+ general['THEME'] + os.sep + "theme.xml").getElementsByTagName("theme")[0]
        self.color = pygame.color.Color("white")
        for i in range (0, len(xml_file.childNodes)):
            try:
                if xml_file.childNodes[i].tagName == "color":
                    self.color = pygame.color.Color(str(xml_file.childNodes[i].getAttribute("value")))
            except:
                pass
        self.font_size = screen.get_height()/20
        self.load()
    def load(self):
        pass
    def drawSimple(self):
        pass
    def drawHover(self):
        self.drawSimple()
    def set_sizex(self, size):
        self.sizex =size
        self.load()
    def set_sizey(self, size):
        self.sizey =size
        self.load()
    def setText(self, value):
        if(value.split(':')[0] == "config"):
            if(value.split(':')[1] == "keyboard"):
                numcle=0
                try:
                    while keyboard_config.keys()[numcle] != value.split(':')[2]:
                        numcle += 1

                    self.text = pygame.key.name(eval(keyboard_config.values()[numcle]))
                except:
                    self.text ="not defined"
            elif(value.split(':')[1] == "sounds"):
                self.text = str(sound_config[value.split(':')[2]])
            else:
                if(general[value.split(':')[1]] == 0):
                    self.text = "False"
                else:
                    self.text = str(general[value.split(':')[1]])
        else:
            self.text = value
    def state(self,state_str):
        self.state_str = state_str
    def click(self,event):
        pass

class WidgetCheckbox(Widget):
    """
    A simple button image.
    """
    text = ""
    state_str = "norm"
    def drawSimple(self):
        self.screen.blit(
            self.image,
        (self.posx, self.posy)
        )
    def drawHover(self):
        self.screen.blit(
            self.image,
        (self.posx, self.posy)
        )
    def draw(self):
        if (self.state_str == "norm"):
            self.drawSimple()
        elif (self.state_str == "click"):
            self.drawClick()
        elif (self.state_str == "hover"):
            self.drawHover()
    def setText(self, value):
        if(value.split(':')[0] == "config"):
            if(value.split(':')[1] == "keyboard"):
                numcle=0
                try:
                    while keyboard_config.keys()[numcle] != value.split(':')[2]:
                        numcle += 1

                    self.text = pygame.key.name(eval(keyboard_config.values()[numcle]))
                except:
                    self.text ="not defined"
            elif(value.split(':')[1] == "sounds"):
                self.text = str(sound_config[value.split(':')[2]])
            else:
                if(general[value.split(':')[1]] == 0):
                    self.text = "False"
                else:
                    self.text = str(general[value.split(':')[1]])
        else:
            self.text = value
        if(self.sizex == 0):
            self.sizex = self.sizey
        if self.text == "True" :
            self.image = loaders.image(
                MEDIA_DIRECTORY+
                os.sep+
                'gui'+
                os.sep+
                general['THEME']+
                os.sep+
                "checkbox_full.png", scale=(self.sizex, self.sizey)
                )[0]
        else :
            self.image = loaders.image(
                MEDIA_DIRECTORY+
                os.sep+
                'gui'+
                os.sep+
                general['THEME']+
                os.sep+
                "checkbox_empty.png", scale=(self.sizex, self.sizey)
                )[0]
        

class WidgetIcon(Widget):
    """
    A simple button widget.
    XML : <button sizex="" sizey="" posx="" posy="" action="" value="" id=""/>
    """
    state_str = "norm"
    def draw(self):
        if (self.state_str == "norm"):
            self.drawSimple()
        elif (self.state_str == "click"):
            self.drawClick()
        elif (self.state_str == "hover"):
            self.drawHover()
    def drawSimple(self):
        self.screen.blit(self.background,(self.posx,self.posy))
        self.screen.blit(
            self.game_font.render(
            self.text,
            True,
            self.color
            ),
        (self.posx + self.sizex/10, self.posy+self.sizey/2-self.screen.get_height()/50)
        )
    def drawHover(self):
        self.screen.blit(self.background_hover,(self.posx,self.posy))
        self.screen.blit(
            self.game_font.render(
            self.text,
            True,
            self.color
            ),
        (self.posx + self.sizex/10, self.posy + self.sizey/2-self.screen.get_height()/50)
        )
    def drawClick(self):
        self.screen.blit(self.background_hover,(self.posx,self.posy))
        self.screen.blit(
            self.game_font.render(
            self.text,
            True,
            self.color
            ),
        (self.posx + self.sizex/10, self.posy+self.sizey/2-self.screen.get_height()/50)
        )
    def load(self):
        path = (MEDIA_DIRECTORY+
            os.sep+
            'gui'+
            os.sep+
            general['THEME']+
            os.sep+
            'back_button.png')
        self.background = loaders.image(path, scale=(self.sizex, self.sizey))[0]
        self.background_hover = loaders.image(MEDIA_DIRECTORY+
            os.sep+
            'gui'+
            os.sep+
            general['THEME']+
            os.sep+
            'back_button_hover.png', scale=(self.sizex, self.sizey))[0]


class WidgetImageButton(Widget):
    """
    A simple button image.
    """
    text = ""
    state_str = "norm"
    def drawSimple(self):
        self.screen.blit(
            self.image,
        (self.posx, self.posy)
        )
    def drawHover(self):
        self.screen.blit(
            self.image,
        (self.posx, self.posy)
        )
    def draw(self):
        if (self.state_str == "norm"):
            self.drawSimple()
        elif (self.state_str == "click"):
            self.drawClick()
        elif (self.state_str == "hover"):
            self.drawHover()
    def setText(self, text):
        self.text = text.replace("theme/", MEDIA_DIRECTORY + os.sep)
        self.image = loaders.image(
            MEDIA_DIRECTORY+
            os.sep+
            'gui'+
            os.sep+
            "image"+
            os.sep+
            self.text
            )[0]
        if(self.sizex == 0):
            self.sizex = self.sizey
        self.image = pygame.transform.scale(self.image, (self.sizex, self.sizey))
        

class WidgetImage(Widget):
    """
    A simple widget image.
    """
    text = ""
    def drawSimple(self):
        self.screen.blit(
            self.image,
            (self.posx, self.posy)
            )
    def draw(self):
        self.drawSimple()
    def setText(self, text):
        if(self.sizex == 0):
            self.sizex = self.sizey
        self.text = text.replace("/", os.sep)
        self.image = loaders.image(
            MEDIA_DIRECTORY+
            os.sep+
            self.text, scale=(self.sizex, self.sizey)
            )[0]
        

class WidgetLabel(Widget):
    text = ""
    def drawSimple(self):
        for text in self.text.split("\n"):
            self.screen.blit(
                self.game_font.render(
                _(text),
                True,
                self.color
                ),
            (self.posx, self.posy+self.font_size*self.text.split("\n").index(text))
            )
    def draw(self):
        self.drawSimple()


class WidgetParagraph(Widget):
    """
    Widget which is called in credits screen
    it is animated.
    """
    text = ""
    state_str="norm"
    action = ""
    anim = True
    last_event = 0
    speed = 0.03
    defil = 0
    stop = False
    def drawSimple(self):
        self.surface.fill(pygame.color.Color("black"))
        for i in range(0,len(self.credits.split("\n"))):
            if "==" in self.credits.split("\n")[i]:
                color = "brown"
            else:
                color = "white"
            self.surface.blit(
                self.game_font.render(
                self.credits.split("\n")[i].strip("=="),
                True,
                pygame.color.Color(
                    color
                    )
                ),
                (0, self.screen.get_height()/20*i-self.defil)
                )
        self.screen.blit(self.surface,(self.posx,self.posy))
    def draw(self):
        try:
            self.falseposy
        except:
            self.falseposy = self.posy
        self.drawSimple()
    def click(self, event, sens=True):
        if(type(event) is not type('') and event.type == pygame.MOUSEBUTTONDOWN):
            self.stop = True
            pass
        elif(type(event) is not type('') and event.type == pygame.MOUSEBUTTONUP):
            self.stop = False
            pass
        elif(time.time() - self.last_event > self.speed and not self.stop):
            if(self.falseposy + self.screen.get_height()/20*(len(self.credits.split("\n"))) < self.posy and sens == "1"):
                self.falseposy = self.posy
                return False
            if(self.falseposy >= self.posy and sens == "0"):
                return False
            self.falseposy -= self.screen.get_height()/400
            self.defil += self.screen.get_height()/400
            self.last_event = time.time()
        return True
    def setParagraph(self, text):
        if(text.split(":")[0] == "file"):
            credits_file = open(text.split(":")[1], 'r').readlines()
            self.credits = ""
            for i in range(0, len(credits_file)):
                self.credits += credits_file[i]
        else:
            self.credits = text
        self.surface = pygame.Surface((self.sizex,self.sizey))


class WidgetTextarea(Widget):
    """
    A simple button widget.
    XML : <button sizex="" sizey="" posx="" posy="" action="" value="" id=""/>
    """
    text = ""
    state_str = "norm"
    str_len = 0
    def draw(self):
        if (self.state_str == "norm"):
            self.drawSimple()
        elif (self.state_str == "click"):
            self.drawClick()
        elif (self.state_str == "hover"):
            self.drawHover()
    def drawSimple(self):
        self.screen.blit(self.background,(self.posx,self.posy))
        self.screen.blit(
            self.game_font.render(
            self.text,
            True,
            pygame.color.Color(
                "white"
                )
            ),
        (self.posx + self.sizex/10, self.posy+self.sizey/2-self.screen.get_height()/50)
        )
    def drawHover(self):
        self.screen.blit(self.background_hover,(self.posx,self.posy))
        self.screen.blit(
            self.game_font.render(
            self.text,
            True,
            pygame.color.Color(
                "white"
                )
            ),
        (self.posx + self.sizex/10, self.posy + self.sizey/2-self.screen.get_height()/50)
        )
    def drawClick(self):
        self.screen.blit(self.background_hover,(self.posx,self.posy))
        self.screen.blit(
            self.game_font.render(
            self.text,
            True,
            pygame.color.Color(
                "white"
                )
            ),
        (self.posx + self.sizex/10, self.posy+self.sizey/2-self.screen.get_height()/50)
        )
    def load(self):
        self.background = pygame.image.load(MEDIA_DIRECTORY+
            os.sep+
            'gui'+
            os.sep+
            general['THEME']+
            os.sep+
            'back_button.png').convert_alpha()
        self.background  = pygame.transform.scale(self.background, (self.sizex, self.sizey))
        #self.background.set_colorkey((255,255,255))
        self.background_hover = pygame.image.load(MEDIA_DIRECTORY+
            os.sep+
            'gui'+
            os.sep+
            general['THEME']+
            os.sep+
            'back_button_hover.png').convert_alpha()
        self.background_hover  = pygame.transform.scale(self.background_hover, (self.sizex, self.sizey))
        #self.background_hover.set_colorkey((255,255,255))
pygame.font.init()
game_font = pygame.font.Font(
            MEDIA_DIRECTORY +
            os.sep +
            "gui" +os.sep + general['THEME'] + os.sep +
            "font.otf", general['HEIGHT']/20)
            
class WidgetCoverflow(Widget):
    """
    A simple button image.
    """
    text = ""
    state_str = "norm"
    elements = {}
    hover =''
    def drawSimple(self):
        self.surface = pygame.Surface((self.sizex,self.sizey/2))
        """self.screen.blit(
            self.image,
        (self.posx, self.posy)
        )"""
        self.surface.blit(
            self.frameleft,
        (self.sizex-self.frameleft.get_width(), 0)
        )
        self.surface.blit(
            self.frameright,
        (0,0)
        )
        self.surface.blit(
            self.frame,
        (self.sizex/2-self.frame.get_width()/2, 0)
        )
        
        self.screen.blit(
            self.surface,
        (self.posx, self.posy)
        )
        self.surface_ = pygame.transform.flip(self.surface, False, True)
        self.surface_.blit(self.foreground, (0,0))
        self.screen.blit(
           self.surface_,
        (self.posx, self.posy+self.sizey-self.surface.get_height())
        )
        
    def drawHover(self):
        self.drawSimple()
    def draw(self):
        if (self.state_str == "norm"):
            self.drawSimple()
        elif (self.state_str == "click"):
            self.drawClick()
        elif (self.state_str == "hover"):
            self.drawHover()
    def setText(self, text):
        self.text = text.replace("theme/", MEDIA_DIRECTORY + os.sep)
        self.image = loaders.image(
            MEDIA_DIRECTORY+
            os.sep+
            'gui'+
            os.sep+
            "image"+
            os.sep+
            self.text
            )[0]
        if(self.sizex == 0):
            self.sizex = self.sizey
        self.image = pygame.transform.scale(self.image, (self.sizex, self.sizey))
    def load(self):
        self.surface = pygame.Surface((self.sizex,self.sizey/2))
        self.foreground = loaders.image(
            MEDIA_DIRECTORY+
            os.sep+
            'gui'+
            os.sep+
            general['THEME']+
            os.sep+
            "cover-foreground.png", scale=(self.sizex, self.sizey/2)
            )[0]
        self.elements['frameright'] = {}
        self.elements['frameright']['posx'] = self.posx
        self.elements['frameright']['posy'] = self.posy
        self.elements['frameright']['width'] = self.sizex/3
        self.elements['frameright']['height'] = self.sizey/3
        self.frameright = loaders.image(
            MEDIA_DIRECTORY+
            os.sep+
            'gui'+
            os.sep+
            general['THEME']+
            os.sep+
            "cover-frame-small.png", scale=(self.sizex/3, self.sizey/3)
            )[0]
        self.elements['frame'] = {}
        self.elements['frame']['posx'] = self.posx + self.sizex/2-self.sizex/2/2
        self.elements['frame']['posy'] = self.posy
        self.elements['frame']['width'] = self.sizex/2
        self.elements['frame']['height'] = self.sizey/2
        self.frame = loaders.image(
            MEDIA_DIRECTORY+
            os.sep+
            'gui'+
            os.sep+
            general['THEME']+
            os.sep+
            "cover-frame-big.png", scale=(self.sizex/2, self.sizey/2)
            )[0]
        self.elements['frameleft'] = {}
        self.elements['frameleft']['posx'] = self.posx + self.sizex-self.sizex/3
        self.elements['frameleft']['posy'] = self.posy
        self.elements['frameleft']['width'] = self.sizex/3
        self.elements['frameleft']['height'] = self.sizey/3
        self.frameleft = pygame.transform.flip(self.frameright, True, False)
    def click(self,event):
        try:
            mousex = event.dict['pos'][0]
            mousey = event.dict['pos'][1]
            if(mousex in range(self.elements['frameright']['posx'],
                                 self.elements['frameright']['posx']+self.elements['frameright']['width']) and
               mousey in range(self.elements['frameright']['posy'],
                                 self.elements['frameright']['posy']+self.elements['frameright']['height'])):
                if self.hover != 'frameright':
                    self.hover = 'frameright'
                    self.frameright = self.frameright.copy()
                    self.frameright.blit(loaders.image(
                                            MEDIA_DIRECTORY+
                                            os.sep+
                                            'gui'+
                                            os.sep+
                                            general['THEME']+
                                            os.sep+
                                            "light.png", scale=(self.elements['frameright']['width'], self.elements['frameright']['height'])
                                            )[0], (0,0))
            elif self.hover == 'frameright':
                self.frameright = loaders.image(
                    MEDIA_DIRECTORY+
                    os.sep+
                    'gui'+
                    os.sep+
                    general['THEME']+
                    os.sep+
                    "cover-frame-small.png", scale=(self.sizex/3, self.sizey/3)
                    )[0]
                self.hover = ''
            if event.type == pygame.MOUSEBUTTONUP:
                self.frameright = loaders.image(
                    MEDIA_DIRECTORY+
                    os.sep+
                    'gui'+
                    os.sep+
                    general['THEME']+
                    os.sep+
                    "cover-frame-small.png", scale=(self.sizex/2, self.sizey/2)
                    )[0]
        except:
            print "it is a str"
        pass
