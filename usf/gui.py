################################################################################
# copyright 2010 Lucas Baudin <xapantu@gmail.com>                              #
#                                                                              #
# This file is part of Ultimate Smash Friends                                  #
#                                                                              #
# UltimateSmashFriends is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation, either version 3 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# UltimateSmashFriends is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.#
################################################################################
'''
The Gui module provide interfaces to build custom screens with widgets and
callback to use them.

'''

import pygame
from pygame.locals import QUIT

import os
import time

# Our modules

from usf.config import Config


import usf.loaders as loaders
from usf.game import Game

from usf.skin import Skin

from usf.widgets.widget import optimize_size

from usf.font import fonts

from usf.translation import _

CONFIG = Config()

from usf.screen.main_screen import Main_screen
from usf.screen.configure import Configure
from usf.screen.about import About
from usf.screen.resume import Resume
from usf.screen.sound import Sound
from usf.screen.screen_screen import Screen_screen
from usf.screen.keyboard import Keyboard
from usf.screen.level import Level
from usf.screen.characters import Characters


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

        self.screens['main_screen'] = Main_screen('main_screen', self.screen)
        self.screens['configure'] = Configure('configure', self.screen)
        self.screens['about'] = About('about', self.screen)
        self.screens['resume'] = Resume('resume', self.screen)
        self.screens['sound'] = Sound('sound', self.screen)
        self.screens['screen_screen'] = Screen_screen('screen_screen',
                self.screen)
        self.screens['keyboard'] = Keyboard('keyboard', self.screen)
        self.screens['level'] = Level('level', self.screen)
        self.screens['characters'] = Characters('characters', self.screen)

        self.screen_current = 'main_screen'
        self.skin = Skin()
        self.last_event = time.time()
        self.image = 0
        self.focus = False
        self.state = "menu"
        self.cursor = loaders.image(
                CONFIG.sys_data_dir + os.sep + 'cursor.png')[0]
        self.update_youhere()

    def update(self):
        """
        Update the GUI, it draws the mouse, and the menu.
        """

        #draw the background
        self.skin.get_background()

        self.screens[self.screen_current].update()

        while(True):
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                pygame.event.post(pygame.event.Event(QUIT))
                break

            elif event.type != pygame.NOEVENT:
                if event.type == pygame.KEYDOWN:
                    self.handle_keys(event)
                elif (event.type == pygame.MOUSEBUTTONUP or
                    event.type == pygame.MOUSEBUTTONDOWN or
                    event.type == pygame.MOUSEMOTION):
                    self.handle_mouse(event)

            else:
                break
        #draw the '> you are here :' dialog
        #update the mouse position
        x, y = pygame.mouse.get_pos()
        #x += self.cursor.get_height()
        #y += self.cursor.get_width()
        self.screen.blit(self.cursor, (x, y))

        #if we have a game instance and the state is menu...
        if self.game and self.state != "ingame":
            self.state = "ingame"
            return True, self.game

        return False, None

    def handle_mouse(self, event):
        """
        This function handles mouse event which are send from the update
        function.
        """
        if not self.focus:
            event.dict['pos'] = (
              event.dict['pos'][0] - self.screens[self.screen_current].widget.x,
              event.dict['pos'][1] - self.screens[self.screen_current].widget.y)

            (query, self.focus) = (
                self.screens[self.screen_current].widget.handle_mouse(event))

        else:
            (query, focus) = self.focus.handle_mouse(event)
            if not focus:
                self.focus = False

        if  query:
            reply = self.screens[self.screen_current].callback(query)
            self.handle_reply(reply)
        #remove the event for performance, maybe it is useless
        del(event)

    def handle_keys(self, event):
        """
        This function handles keyboard event which are send from the update
        function.
        """
        #TODO : a complete navigation system with the keyboard.
        reply = False
        query = False

        if self.focus:
            (query, focus) = self.focus.handle_keys(event)
            if not focus:
                self.focus = False
            if  query:
                reply = self.screens[self.screen_current].callback(query)
                self.handle_reply(reply)
        if not self.focus and (not reply and not query):
            if event.dict['key'] == pygame.K_ESCAPE:
                self.handle_reply("goto:back")
            else:
                (query, focus) = (
                        self.screens[self.screen_current].handle_keys(event))
                if not focus:
                    self.focus = False
                else:
                    self.focus = focus
                if  query:
                    reply = self.screens[self.screen_current].callback(query)
                    self.handle_reply(reply)

        #remove the event for performance, maybe it is useless
        del(event)

    def handle_reply(self, reply):
        """
        This function handles the callback return by thz screens
        with the function event_callback().
        This callback needs to be a string; otherwise, it will be ignored.

        The reply can be:
            goto:myscreen
                where my screen is the name of the screen loaded in __init__()
            goto:back
                go to the last menu, it is usually used for a back button
            game:new
                to start a new game
            game:continue
                to resume the game, it is used in the in-game menu
            game:stop
                to stop the game, it is used to qui the game in the
                in-game menu
        """

        if type(reply) == str:
            if reply.split(':')[0] == 'goto':
                sound = loaders.track(
                        os.path.join(CONFIG.sys_data_dir, "sounds",
                            "mouseClick2.wav"))

                sound.set_volume(CONFIG.audio['SOUND_VOLUME']/100.0)
                sound.play()
                if reply.split(':')[1] == 'back':
                    pass
                else:
                    self.screen_history.append(self.screen_current)
                    self.screen_current = reply.split(':')[1]

            if reply.split(':')[0] == 'game':
                if reply.split(':')[1] == "new":
                    self.game = self.launch_game()
                    self.screen_current = 'resume'
                    self.screen_history = []
                    self.state = "menu"
                if reply.split(':')[1] == "continue":
                    self.screen_current = 'resume'
                    self.screen_history = []
                    self.state = "menu"
                if reply.split(':')[1] == "stop":
                    self.state = "menu"
                    self.game = None
                    self.screen_current = 'main_screen'
                    self.screen_history = []

    def screen_back(self):
        """
        Go to the last screen.
        """
        if len(self.screen_history) > 0:
            self.screen_current = self.screen_history[-1]
            del self.screen_history[-1]
            return True
        return False

    def update_youhere(self):
        screen_list = ""
        for scr in self.screen_history:
            screen_list += scr + "/"

        screen_list += self.screen_current + "/"
        self.here = loaders.text("> " + _("you are here:") + screen_list,
            fonts['mono']['30'])

    def transition_slide(self, old_screen, old_surface, new_screen,
            new_surface):
        text = get_text_transparent(old_screen.name)

        for i in range(0, 10):
            time.sleep(1.00/float(CONFIG.general['MAX_FPS']))
            self.skin.get_background()
            text.set_alpha((i * -1 + 10) * 250 / 10)
            self.screen.blit(text,
                (old_screen.indent_title, 10))
            self.screen.blit(old_surface,
                (optimize_size((i * 8 * 10, 0))[0], old_screen.widget.y))

            pygame.display.update()

        text = get_text_transparent(new_screen.name)

        for i in range(0, 10):
            time.sleep(1.00/float(CONFIG.general['MAX_FPS']))
            self.skin.get_background()
            text.set_alpha(i*250/10)
            self.screen.blit(text,
                    (self.screens[self.screen_current].indent_title, 10))
            self.screen.blit(new_surface,
                (optimize_size((i*8*10-800, 0))[0],
                self.screens[self.screen_current].widget.y))

            pygame.display.update()

    def transition_fading(self, old_screen, old_surface, new_screen,
            new_surface):
        text = get_text_transparent(old_screen.name)

        for i in range(0, 5):
            back = self.skin.get_background().convert()
            time.sleep(1.00/float(CONFIG.general['MAX_FPS']))
            self.screen.blit(self.skin.get_background(), (0, 0))
            text.set_alpha((i* -1 + 5) * 250 / 5)
            self.screen.blit(text, (old_screen.indent_title, 10))

            #back.set_alpha( (i*(- 1) + 5) *250/5)
            back.set_alpha(i *250/5)
            self.screen.blit(old_surface,
                    (old_screen.widget.x, old_screen.widget.y))
            self.screen.blit(back, (0, 0))

            pygame.display.update()

        text = get_text_transparent(new_screen.name)

        for i in range(0, 5):
            back = self.skin.get_background().convert()
            time.sleep(1.00/float(CONFIG.general['MAX_FPS']))
            self.screen.blit(self.skin.get_background(), (0, 0))
            text.set_alpha(i*250/5)
            self.screen.blit(text,
                    (self.screens[self.screen_current].indent_title, 10))

            #new_surface.set_alpha(i *250/5)
            back.set_alpha((i * -1 + 5) * 250 / 5)
            self.screen.blit(new_surface,
                    (new_screen.widget.x, new_screen.widget.y))
            self.screen.blit(back, (0, 0))

            pygame.display.update()

    def launch_game(self):
        """
        Function to launch the game, use precedant user choices to initiate the
        game with level and characters selected.

        """
        players = []
        for i in range(0, len(self.screens["characters"].players)):
            if self.screens["characters"].players[i] != 0:
                file_name = (
                        self.screens["characters"].game_data['character_file']
                                [self.screens["characters"].players[i]])
                if self.screens["characters"].checkboxes_ai[i].get_value():
                    file_name = file_name.replace(
                            "characters/", "characters/AI")
                players.append(file_name)

        if len(players) > 1:
            game = Game(
                self.screen,
                self.screens["level"].get_level(),
                players)

            #thread.start_new_thread(self.loading, ())
            #self.goto_screen("ingame.usfgui", False)
            #self.state="game"
            return game


def get_text_transparent(name):
    text = loaders.text(name, fonts['mono']['15']).convert()
    text.fill(pygame.color.Color("black"))
    #TODO: the colorkey should be a property of the skin
    text.set_colorkey(pygame.color.Color("black"))
    text.blit(loaders.text(name, fonts['mono']['15']), (0, 0))
    return text

