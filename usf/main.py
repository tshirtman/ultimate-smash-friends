#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
#                                                                              #
# This file is part of UltimateSmashFriends                                    #
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

import logging
import os

from pygame.locals import QUIT
import pygame
import sys
from optparse import OptionParser
import time
import threading
import traceback
from exceptions import AttributeError
# our modules
from config import Config

from game import Game
from gui import Gui
from controls import Controls
import loaders
import music
from font import fonts
from ai import AI

try:
    config = Config()
    logging.basicConfig(
        filename=os.path.join(config.user_data_dir,
            config.debug['LOG_FILENAME']),
        level=eval('logging.' + config.debug['LOG_LEVEL']))

except AttributeError:
    logging.basicConfig(
        filename=os.path.join(config.user_data_dir,
config.debug['LOG_FILENAME']),
        level = logging.WARNING)

    logging.error(_('Bad logging level in user.cfg!'))

logging.debug("User config file: " + config.user_config_file)
logging.debug("User config dir: " + config.user_config_dir)
logging.debug("User data dir: " + config.user_data_dir)
logging.debug("System config file: " + config.sys_config_file)
logging.debug("System data dir: " + config.sys_data_dir)


class Main(object):
    """
    The main class, load some parameters, sets initial states and takes care of
    the game main loop.
    """

    def __init__(self):
        """
        The constructor, create the render surface, set the menu initial state,
        parse command line params if any, launch the menu or the game depending
        on parameters.
        """

        self.lock = threading.Lock()
        self.stop_thread = False
        self.game_type = ''
        self.level = None
        self.players = []
        self.num = None
        self.address = None
        self.text_thread = _("Loading...")

        self.initate_options_parser()
        self.parse_options()

    def init(self):
        if self.game_type == 'server':
            self.init_server()
        elif self.game_type == 'client':
            self.init_client()
        else:
            self.init_standalone()

    def init_server(self):
        self.game = NetworkServerGame()

    def init_client(self):
        self.init_screen()
        self.init_sound()

        self.game = NetworkClientGame(level, players)
        self.state = "game"
        self.menu = Gui(self.screen)

    def init_standalone(self):
        self.init_screen()
        try:
            self.text_thread = "Loading sounds and musics..."
            thread = threading.Thread(None, self.loading_screen)
            thread.start()

            self.init_sound()
            self.ai = AI()

            # if a level was provided and at least two players in the option
            # immediatly jump into game mode
            if len(self.players) > 1 and self.level is not None:
                self.game = Game(self.screen, self.level, self.players)
                self.state = "game"
                self.menu = Gui(self.screen)
                self.menu.handle_reply('goto:resume')

            else:
                self.lock.acquire()
                self.text_thread = "Loading GUI..."
                self.lock.release()

                self.menu = Gui(self.screen)

                self.state = "menu"

                self.game = None
                self.level = None

            self.lock.acquire()
            self.stop_thread = True
            self.lock.release()
            thread.join()
            # end of loading resources

        except Exception as e:
            try:
                if not config.general["DEBUG"]:
                    self.lock.acquire()
                    self.text_thread = (
                            "An error occured:\n" + str(traceback.format_exc()))

                    self.lock.release()
                    time.sleep(5)
                self.lock.acquire()
                self.stop_thread = True
                self.lock.release()
                raise
            except:
                self.lock.acquire()
                self.stop_thread = True
                self.lock.release()
                logging.debug(e)
                raise

    def initate_options_parser(self):
        """
        Set options and usage to parse users choices
        """
        usage = ''.join((
                'ultimate-smash-friends [-h] [-a][-l level-name] ',
                '[-p player1,player2...] [-s num] [-C address] [-t',
                'character,level]\n',
                'If a level and at least two players are selected, a match is',
                ' launched immediately.'))

        version = '%prog 0.1.3'

        self.parser = OptionParser(usage=usage, version=version)
        self.parser.add_option('-a', '--authors',
                          action='store_true', dest='author',
                          help='See authors of this game.')
        self.parser.add_option('-l', '--level',
                          action='store', dest='level', metavar='levelname',
                          help='select level by name')
        self.parser.add_option('-p', '--players',
                          action='store', dest='players', nargs=1,
                          metavar='player1,player2..',
                          help='select up to 4 players by name')
        self.parser.add_option('-s', '--server',
                          action='store', dest='server', metavar='num',
                          help="will launch a game server accepting 'num' " \
                               "players before launching the bame.")
        self.parser.add_option('-C', '--client',
                          action='store', dest='client', metavar='address',
                          help="will attempt to connect to a game server at " \
                               "'address'")
        self.parser.add_option('-t', '--train',
                          action='store', dest='train',
                          metavar='character,level',
                          help=''.join((
                              "will load 4 times the character in the level,",
                              " and use random moves from every place to ",
                              "find path values and store them")))

    def parse_options(self):
        # set up the comand line parser and its options
        (options, args) = self.parser.parse_args()

        # actually parse the command line options
        if options.author:
            self.author()

        if options.level:
            self.level = options.level

        if options.players:
            self.players = map(
                    lambda p: 'characters'+os.sep+p,
                    options.players.split(','))

        if options.server:
            self.game_type = 'server'
            self.num = options.server

        if options.client:
            self.game_type = 'client'
            self.address = options.client

        if options.train:
            self.level = options.train.split(',')[1]
            self.players = (options.train.split(',')[0], )*4
            self.game_type = 'training'

        pygame.init()

        self.clock = pygame.time.Clock()
        self.controls = Controls()
        self.menu = None
        self.state = ""

    def init_screen(self):
        SIZE = (config.general['WIDTH'], config.general['HEIGHT'])
        if (config.general['WIDTH'], config.general['HEIGHT']) == (0, 0):
            if (800, 600) in pygame.display.list_modes():
                (config.general['WIDTH'], config.general['HEIGHT']) = (800, 600)

            else:
                #the old default value...
                (config.general['WIDTH'], config.general['HEIGHT']) = (800, 480)
            config.general['FULLSCREEN'] = False

        SIZE = (config.general['WIDTH'], config.general['HEIGHT'])
        self.screen = pygame.display.set_mode(SIZE)

        pygame.display.set_caption('Ultimate Smash Friends')
        icon = loaders.image(os.path.join(config.sys_data_dir, 'icon',
                                          'icon_50.png'))[0]
        pygame.display.set_icon(icon)
        if config.general['FULLSCREEN']:
            pygame.display.toggle_fullscreen()

    def init_sound(self):
        if config.audio['MUSIC']:
            self.music = music.Music()

    def manage_menu(self):
        # return of the menu update function may contain a new game
        # instance to switch to.
        start_loop = pygame.time.get_ticks()
        newgame, game_ = self.menu.update(self.clock)
        if newgame:
            self.state = 'game'
            if game_ is not self.game:
                print "starting game"
                self.ai = AI()

                del(self.game)
                self.game = game_

        max_fps = 1000/config.general["MAX_GUI_FPS"]

        if self.menu.screen_current == 'about':
            self.music_state = 'credits'
        else:
            self.music_state = self.state

        if pygame.time.get_ticks() < max_fps + start_loop:
            pygame.time.wait(max_fps + start_loop - pygame.time.get_ticks())

    def manage_ai(self):
        for i, p in enumerate(self.game.players):
            if p.ai and p.present:
                self.ai.update(self.game, i)

    def manage_game(self, was_paused):
        d = self.game.update_clock(was_paused or self.game.first_frame)
        self.state = self.game.update(d)
        self.manage_ai()

        if self.state in ('game', 'victory'):
            self.game.draw(
                debug_params={
                    'controls': config.debug['CONTROLS'] and self.controls,
                    'action': config.debug['ACTIONS'],
                    'hardshape': config.debug['HARDSHAPES'],
                    'footrect': config.debug['FOOTRECT'],
                    'current_animation': config.debug['CURRENT_ANIMATION'],
                    'levelshape': config.debug['LEVELSHAPES'],
                    'levelmap': config.debug['LEVELMAP']})

            self.menu.load = False
        else:
            self.menu.screen_current = "main_screen"

        self.music_state = self.state

    def display_fps(self):
            #FPS counter
            if config.general["SHOW_FPS"]:
                self.screen.blit(
                        loaders.text(
                            "FPS: " + str(self.clock.get_fps()),
                            fonts["mono"]["38"]),
                        (10, 5))

    def go(self):
        """
        The main game loop, take care of the state of the game/menu.

        """
        pygame.mouse.set_visible(False)
        #try:
        while (True):
            # update the fps counter
            self.clock.tick()

            # poll controls and update informations on current state of the UI
            state_was = self.state
            if self.state != "menu":
                self.state = self.controls.poll(
                        self.game, self.menu, self.state)
            if self.state == "menu":
                self.manage_menu()
            else:
                self.manage_game(state_was == "menu")

            self.display_fps()
            pygame.display.update()

            if config.audio['MUSIC']:
                self.music.update(self.music_state)
            # verify there is not a QUIT event waiting for us, in case of we
            # have to quit.
            self.ended = pygame.event.get(QUIT)
            if self.ended:
                logging.debug('fps = '+str(self.clock.get_fps()))
                pygame.quit()
                break

    def author(self):
        if 'CREDITS' not in os.listdir(os.path.join(config.sys_data_dir)):
            logging.info(config.sys_data_dir)
            logging.info(
                    '\n'.join(os.listdir(os.path.join(config.sys_data_dir))))
            logging.debug(config.sys_data_dir+'/CREDITS file not found')
        else:
            author_file = open(os.path.join(config.sys_data_dir, 'CREDITS'))
            logging.info(author_file.read())
            author_file.close()

    def loading_screen(self):
        """
        update the screen display during loading
        """
        while not self.stop_thread:
            start_loop = pygame.time.get_ticks()

            self.lock.acquire()
            text = loaders.paragraph(self.text_thread, fonts['mono']['normal'])
            self.lock.release()

            x = self.screen.get_width()/2 - text.get_width()/2
            y = self.screen.get_height()/2 - text.get_height()/2

            self.screen.fill(pygame.color.Color("black"))
            self.screen.blit(text, (x, y))
            pygame.display.update()

            max_fps = 1000/config.general["MAX_GUI_FPS"]
            if pygame.time.get_ticks() < max_fps + start_loop:
                pygame.time.wait(max_fps + start_loop - pygame.time.get_ticks())

if __name__ == '__main__':
    """
    Entry point of the game, if not imported from another script, launch the
    main class with parameters (appart from program self name) if any.
    """

    m = Main()
    m.init()
    m.go()
