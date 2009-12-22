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
from translation import _
import pygame
class WidgetLabel(Widget):
    text = ""
    def drawSimple(self):
        self.screen.blit(
            self.game_font.render(
            _(self.text),
            True,
            pygame.color.Color(
                "white"
                )
            ),
        (self.posx, self.posy)
        )
    def draw(self):
        self.drawSimple()
