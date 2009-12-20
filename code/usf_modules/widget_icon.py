################################################################################
# copyright 2009 xapantu <xapantu@gmail.com>                                   #
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
from usf_modules.widget import *
import pygame
class WidgetIcon(Widget):
    text = ""
    state = "norm"
    def draw(self):
        if (self.state == "norm"):
            self.drawSimple()
        elif (self.state == "click"):
            self.drawClick()
        elif (self.state == "hover"):
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
        self.background = pygame.image.load(config['MEDIA_DIRECTORY']+
            os.sep+
            'gui'+
            os.sep+
            'back_button.png').convert_alpha()
        self.background  = pygame.transform.scale(self.background, (self.sizex, self.sizey))
        #self.background.set_colorkey((255,255,255))
        self.background_hover = pygame.image.load(config['MEDIA_DIRECTORY']+
            os.sep+
            'gui'+
            os.sep+
            'back_button_hover.png').convert_alpha()
        self.background_hover  = pygame.transform.scale(self.background_hover, (self.sizex, self.sizey))
        #self.background_hover.set_colorkey((255,255,255))
