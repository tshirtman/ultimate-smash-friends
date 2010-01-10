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
from usf_modules.widget import *
import pygame
import time
from usf_modules import loaders
import os
class WidgetParagraph(Widget):
    """
    Widget which is called in credits screen
    it is animated.
    """
    text = ""
    state="norm"
    action = ""
    diff_false_truey = 0
    def drawSimple(self):
        for i in range(0, len(self.credits.split("\n"))):
            try:
                if(self.falseposy + self.screen.get_height()/20*i >= self.posy and self.falseposy + self.screen.get_height()/20*i <= self.posy+self.sizey):
                    self.screen.blit(
                        self.game_font.render(
                        self.credits.split("\n")[i],
                        True,
                        pygame.color.Color(
                            "white"
                            )
                        ),
                        (self.posx, self.falseposy + self.screen.get_height()/20*i)
                        )
            except:
                self.screen.blit(
                    self.game_font.render(
                    self.credits.split("\n")[i],
                    True,
                    pygame.color.Color(
                        "white"
                        )
                    ),
                    (self.posx, self.falseposy + self.screen.get_height()/20*i)
                    )
    def draw(self):
        try:
            self.falseposy
        except:
            self.falseposy = self.posy
        self.drawSimple()
    def click(self, event):
        if(self.diff_false_truey == self.screen.get_height()/20*5):
            self.diff_false_truey = 0
            return False
        if(self.falseposy + self.screen.get_height()/20*(len(self.credits.split("\n"))-10) < self.posy and sens == "1"):
            print "bottom !"
            return False
        if(self.falseposy >= self.posy and sens == "0"):
            print "top !"
            return False
        if(sens == "1"):
            self.falseposy -= self.screen.get_height()/20
        else:
            self.falseposy += self.screen.get_height()/20
        self.diff_false_truey += self.screen.get_height()/20
        return True
    def setParagraph(self, text):
        if(text.split(":")[0] == "file"):
            credits_file = open(text.split(":")[1], 'r').readlines()
            self.credits = ""
            for i in range(0, len(credits_file)):
                self.credits += credits_file[i]
            self.sizey = 150
            self.sizex = self.screen.get_height()/2
        else:
            self.credits = text
