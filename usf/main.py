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
config = Config()
SIZE = (config.general['WIDTH'], 
        config.general['HEIGHT'])


from game import Game, NetworkServerGame, NetworkClientGame
from gui import Gui
from controls import Controls
import loaders, music
from font import fonts

try:
    logging.basicConfig(
        filename=config.debug['LOG_FILENAME'],
        level=eval('logging.'+config.debug['LOG_LEVEL'])
        )
except AttributeError:
    logging.basicConfig(
        filename=config.debug['LOG_FILENAME'],
        level = logging.WARNING
        )
    logging.error('Bad logging level in user.cfg!')

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

        self.parse_options()

        if self.game_type == "server":
            self.game = NetworkServerGame()

        elif self.game_type == "client":
            self.init_screen()
            self.init_sound()

            self.game = NetworkClientGame(level, players)
            self.state = "game"
            self.menu = Gui(self.screen)

        else:
            self.init_screen()
            try:
                self.thread = threading.Thread(None, self.loading)
                self.thread.start()

                self.lock.acquire()
                self.text_thread = "Loading sounds and musics..."
                self.lock.release()

                self.init_sound()

                if len(self.players) > 1 and self.level is not None:
                    self.game = Game(self.screen, self.level, self.players)
                    self.state = "game"
                    self.menu = Gui(self.screen)
                    self.menu.handle_reply('goto:resume')

                else:
                    pygame.display.update()

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
            except Exception, e:
                try:
                    if not config.general["DEBUG"]:
                        self.lock.acquire()
                        self.text_thread = "An error occured:\n" + str(traceback.format_exc())
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
                    print e
                    raise
            self.go()

    def parse_options(self):
        # set up the comand line parser and its options
        usage = 'ultimate-smash-friends [-h] [-a][-l level-name] ' \
                '[-p player1,player2...] [-s num] [-C address]\n' \
                'If a level and at least two players are selected, a match is ' \
                'launched immediately.'

        version = '%prog 0.0.7'

        parser = OptionParser(usage=usage, version=version)
        parser.add_option('-a', '--authors', 
                          action='store_true', dest='author',
                          help='See authors of this game.')
        parser.add_option('-c', '--character_creator',
                          action='store_true', dest='character_creator',
                          help='create new character')
        parser.add_option('-l', '--level',
                          action='store', dest='level', metavar='levelname',
                          help='select level by name')
        parser.add_option('-p', '--players',
                          action='store', dest='players', nargs=1,
                          metavar='player1,player2..',
                          help='select up to 4 players by name')
        parser.add_option('-s', '--server',
                          action='store', dest='server', metavar='num',
                          help="will launch a game server accepting 'num' " \
                               "players before launching the bame.")
        parser.add_option('-C', '--client',
                          action='store', dest='client', metavar='address',
                          help="will attempt to connect to a game server at " \
                               "'address'")

        (options, args) = parser.parse_args()

        # actually parse the command line options
        if options.author:
            self.author()

        """ viewer is broken
        if options.character_creator:
            launch_character_creator()
        """


        if options.level:
            self.level = options.level

        if options.players:
            self.players = ['characters'+os.sep+np for np in options.players.split(',')]

        if options.server:
            self.game_type = 'server'
            self.num = options.server

        if options.client:
            self.game_type = 'client'
            self.address = options.client

        pygame.init()

        self.clock = pygame.time.Clock()
        self.controls = Controls()
        self.menu = None
        self.state = ""

    def init_screen(self):
        if (config.general['WIDTH'],
                config.general['HEIGHT']) not in pygame.display.list_modes():
            (config.general['WIDTH'], config.general['HEIGHT']) = pygame.display.list_modes()[0]
            config.general['FULLSCREEN'] = True
        SIZE = (config.general['WIDTH'], config.general['HEIGHT'])
        self.screen = pygame.display.set_mode(SIZE)
        
        pygame.display.set_caption('Ultimate Smash Friends')
        icon = loaders.image(os.path.join(config.sys_data_dir, 'gui',
                                          'icon.png'))[0]
        pygame.display.set_icon(icon)
        if config.general['FULLSCREEN'] == True:
            pygame.display.toggle_fullscreen()

    def init_sound(self):
        if config.audio['MUSIC']:
            self.music = music.Music()

    def go(self):
        """
        The main game loop, take care of the state of the game/menu.

        """
        pygame.mouse.set_visible(False)
        while (True):
            # update the fps counter
            start_loop = pygame.time.get_ticks()
            self.clock.tick()

            # poll controls and update informations on current state of the UI
            if self.state != "menu" :
                self.state = self.controls.poll(self.game, self.menu, self.state)
            if self.state == "menu":
                # return of the menu update function may contain a new game
                # instance to switch to.
                newgame, game_ = self.menu.update(self.clock)
                if newgame:
                    if game_ is not self.game:
                        #logging.debug('new game')
                        del(self.game)
                        self.game = game_

                    self.state = 'game'
            else:
                self.state = self.game.update()
                if self.state in ['game', 'victory']:
                    self.game.draw(
                        debug_params={
                            'controls': config.debug['CONTROLS'] and self.controls,
                            'action': config.debug['ACTIONS'],
                            'hardshape': config.debug['HARDSHAPES'],
                            'footrect': config.debug['FOOTRECT'],
                            'current_animation':
                            config.debug['CURRENT_ANIMATION'],
                            'levelshape': config.debug['LEVELSHAPES'],
                            }
                        )
                    self.menu.load = False
                else:
                    self.menu.screen_current = "main_screen"
            #FPS counter
            if config.general["SHOW_FPS"]:
                self.screen.blit(loaders.text("FPS: " + str(self.clock.get_fps()), fonts["mono"]["38"]), (10, 5))
            pygame.display.update()
            
            if self.menu.screen_current == 'about':
                music_state = 'credits'
            else:
                music_state = self.state

            if config.audio['MUSIC']:
                self.music.update(music_state)
            # verify there is not a QUIT event waiting for us, in case of we
            # have to quit.
            self.ended = pygame.event.get(QUIT)
            if self.ended :
                logging.debug('fps = '+str(self.clock.get_fps()))
                pygame.quit()
                break
            if self.state == "menu":
                #FIXME
                max_fps = 1000/config.general["MAX_GUI_FPS"]
                if pygame.time.get_ticks() < max_fps + start_loop:
                    pygame.time.wait(max_fps + start_loop - pygame.time.get_ticks())
                """
                if pygame.time.get_ticks() - (start_loop + 1.0/float(config.general["MAX_GUI_FPS"])) > 0:
                    pygame.time.wait(int(pygame.time.get_ticks() - (start_loop + 1.0/float(config.general["MAX_GUI_FPS"]))))
                """

    def author(self):
        if 'CREDITS' not in os.listdir(os.path.join(config.sys_data_dir)):
            print config.sys_data_dir
            print '\n'.join(os.listdir(os.path.join(config.sys_data_dir)))
            print "plop?"
            logging.debug(config.sys_data_dir+'/CREDITS file not found')
            #sys.exit(0)
        else:
            author_file = open(os.path.join(config.sys_data_dir,'CREDITS'))
            print author_file.read()
            author_file.close()
            #sys.exit(2)

    """ TODO: Rather than having a BIN_DIRECTORY variable, programmatically determine
        binary location
    def launch_character_creator(self):
        os.popen(os.path.join(config['BIN_DIRECTORY'],'viewer'))
        sys.exit(2)
    """

    def loading(self):
        try:
            while(True):
                start_loop = pygame.time.get_ticks()
                
                self.lock.acquire()

                self.screen.fill(pygame.color.Color("black"))
                x = self.screen.get_width()/2 - loaders.paragraph(self.text_thread, fonts['mono']['normal']).get_width()/2
                y = self.screen.get_height()/2 - loaders.paragraph(self.text_thread, fonts['mono']['normal']).get_height()/2
                self.screen.blit(loaders.paragraph(self.text_thread, fonts['mono']['normal']), (x,y))
                if self.stop_thread:
                    break
                pygame.display.update()
                self.lock.release()

                max_fps = 1000/config.general["MAX_GUI_FPS"]
                if pygame.time.get_ticks() < max_fps + start_loop:
                    pygame.time.wait(max_fps + start_loop - pygame.time.get_ticks())
        except:
            self.lock.release()
            raise

if __name__ == '__main__':
    """
    Entry point of the game, if not imported from another script, launch the
    main class with parameters (appart from program self name) if any.

    """

    Main()
