#!/usr/bin/env python
# -*- coding : utf-8 -*-
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

from pygame.locals import QUIT
import pygame
import os
import sys
from optparse import OptionParser
import logging

# our modules
from usf.config import Config
config = Config.getInstance()
SIZE = (config.general['WIDTH'], 
        config.general['HEIGHT'])


from usf.game import Game, NetworkServerGame, NetworkClientGame
from usf.gui import Gui
from usf.controls import Controls
from usf import loaders, music

#logging.basicConfig(filename=config['LOG_FILENAME'],level=logging.DEBUG)

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


        self.game_type = ''
        self.level = None
        self.players = []
        self.num = None
        self.address = None

        self.parse_options()

        if self.game_type == "server":
            self.game = NetworkServerGame()

        elif self.game_type == "client":
            self.init_screen()
            self.init_sound()

            self.game = NetworkClientGame(level, players)
            self.state = "game"
            self.menu = Gui()

        else:
            self.init_screen()
            self.init_sound()

            if len(self.players) > 1 and self.level is not None:
                self.game = Game(self.screen, self.level, self.players)
                self.state = "game"
                self.menu = Gui(self.screen)
                self.menu.goto_screen('ingame.usfgui')

            else:
                """self.screen.blit(
                    self.game_font.render(
                        "menus...",
                        True,
                        pygame.color.Color(
                            "white"
                            )
                        ),
                    (30, 4*SIZE[1]/5)
                    )"""

                pygame.display.update()

                self.menu = Gui(self.screen)

                self.state = "menu"

                self.game = None
                self.level = None

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
            self.address = option.client

        pygame.init()

        self.clock = pygame.time.Clock()
        self.controls = Controls()
        self.menu = None
        self.state = ""

    def init_screen(self):
        self.screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption('Ultimate Smash Friends')
        icon = loaders.image(os.path.join(config.sys_data_dir, 'gui',
                                          'icon.png'))[0]
        pygame.display.set_icon(icon)
        if config.general['FULLSCREEN'] == "True":
            pygame.display.toggle_fullscreen()

    def init_sound(self):
        if config.audio['MUSIC']:
            try:
                self.music = music.Music()
            except:
                pass
                #TODO: add more useful error handling
                #exit(0)

    def go(self):
        """
        The main game loop, take care of the state of the game/menu.

        """
        while (True):
            # update the fps counter
            self.clock.tick()

            # poll controls and update informations on current state of the UI
            if self.state != "menu" :
                self.state = self.controls.poll(self.game, self.menu, self.state)
            if self.state == "menu":
                # return of the menu update function may contain a new game
                # instance to switch to.
                newgame, game_ = self.menu.update(self.state, self.game, 
                                                  self.controls)
                if newgame:
                    if game_ is not self.game:
                        #logging.debug('new game')
                        del(self.game)
                        self.game = game_

                    self.state = 'game'
            else:
                self.state = self.game.update()
                if self.state == 'game':
                    self.game.draw(
                        debug_params={
                            #'controls': self.controls,
                            #'action':None,
                            }
                        )
                    self.menu.load = False

            pygame.display.update()
            if config.audio['MUSIC']:
                self.music.update(self.state)
            # verify there is not a QUIT event waiting for us, in case of we
            # have to quit.
            self.ended = pygame.event.get(QUIT)
            if self.ended :
                logging.debug('fps = '+str(self.clock.get_fps()))
                pygame.quit()
                break

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


if __name__ == '__main__':
    """
    Entry point of the game, if not imported from another script, launch the
    main class with parameters (appart from program self name) if any.

    """

    Main()
