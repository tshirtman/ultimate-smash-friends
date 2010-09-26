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

# Our modules
from usf.config import Config
config = Config()
from usf.font import fonts
from usf import loaders
import pygame

class Screen(object):

    def __init__(self, name, screen):
        self.current_focus = -1
        self.set_name(name)
        self.screen = screen
        self.init()
        self.update_pos()

    def add(self, widget):
        self.widget = widget
        #define the position and the size of the top-level widget
        self.widget.set_size((config.general['WIDTH'],config.general['HEIGHT']))
        self.widget.x = 0
        self.widget.y = 70
        self.widget.update_size()
        self.widget.update_pos()

    def update(self):
        #draw the title of the screen
        self.screen.blit(loaders.text(self.name, fonts['mono']['15']),
                         (self.indent_title,10)
                        )
        
        #draw all the others widgets
        self.widget.draw()

    def load(self):
        loaders.text(self.name, fonts['mono']['15'])
        self.widget.draw()

    def init(self):
        pass

    def callback(self, action):
        pass
        
    def set_name(self, name):
        self.name = name.replace('_', ' ')  
        
        #center the title
        self.indent_title = (config.general['WIDTH']/2 -
                     loaders.text(self.name, fonts['mono']['15']).get_width()/2)
    
    def update_pos(self):
        self.widget.update_size()
        #center the main container (and all the widgets which are in it)
        #verticaly
        self.widget.y = ((config.general['HEIGHT'] - 70) / 2 - self.widget.height/2)+70

        #center it horizontaly
        self.widget.x = config.general['WIDTH']/2 - self.widget.width/2

        self.widget.update_pos()
        
    def check_widgets(self, widgets):
        for widget in widgets:
            if widget.focusable:
                try:
                    self.check_widgets(widget.widgets)
                except AttributeError:
                    self.widgets_known.append(widget)

            else:
                self.widgets_known.append(widget)
                

    def handle_keys(self, event):
        #remumber all widgets that needs to be focusable (= all widgets - boxes)
        try:
            self.widgets_known
        except:
            self.widgets_known = []
            self.check_widgets(self.widget.widgets)
        
        #increase the index of the focused widget and define in wich sens we
        #have to find a focusable widget
        sens = True
        if(event.dict["key"] == pygame.K_DOWN and
           self.current_focus + 1 < len(self.widgets_known)):
            self.current_focus += 1
            sens = True

        if(event.dict["key"] == pygame.K_UP and
           self.current_focus > 0):
            self.current_focus -= 1
            sens = False

        #find a focusable widget, and select it
        attempt = 0
        while(attempt < len(self.widgets_known)):
            #send the event to widget
            callback = self.widgets_known[self.current_focus].handle_keys(event)
            
            #if he wants the event
            if callback[1] != False:
                return callback
            
            #if it doesn't want it:
            attempt += 1
            
            #trying another widget:
            
            #if the users pressed UP
            if sens:
                if self.current_focus + 1 < len(self.widgets_known):
                    self.current_focus += 1
                else:
                    self.current_focus = 0
            
            #if he pressed DOWN
            else:
                if self.current_focus > 0:
                    self.current_focus -= 1
                else:
                    self.current_focus += 1
        
        #this shouldn't happen, excepted if there is no focusable widget
        #in the screen (and it shoudn't happen, since there is back, at least)
        return False,False
