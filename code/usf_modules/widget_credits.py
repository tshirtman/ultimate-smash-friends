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
import time
from usf_modules import loaders
class WidgetCredits(Widget):
    """
    Widget which is called in credits screen
    it is animated.
    """
    text = ""
    action = "self.widget_list[self.screen_current][i].click()"
    def drawSimple(self):
        for i in range(0, len(self.text.split("\\n"))):
            self.screen.blit(
                self.game_font.render(
                self.text.split("\\n")[i],
                True,
                pygame.color.Color(
                    "white"
                    )
                ),
                (self.posx, self.posy + self.screen.get_height()/20*i)
                )
    def draw(self):
        self.drawSimple()
    def click(self):
        image = loaders.image(
            config['MEDIA_DIRECTORY']+
            os.sep+
            'gui'+
            os.sep+
            config['THEME']+
            os.sep+
            'loading.png'
            )[0]
        image = pygame.transform.scale(image, (self.screen.get_width(), self.screen.get_height()))
        print self.posy + self.sizey
        if(self.posy + self.sizey >self.screen.get_height()):
            oldposy = self.posy
            while(oldposy-self.posy< self.screen.get_height()/2):
                self.screen.blit(image,(0,0))
                self.draw()
                time.sleep(0.04)
                pygame.display.update()
                self.posy -= self.screen.get_height()/20
            self.screen.blit(image,(0,0))
