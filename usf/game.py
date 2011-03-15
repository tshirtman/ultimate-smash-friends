#!/usr/bin/env python
# set encoding: utf-8
################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
#                                                                              #
# This file is part of UltimateSmashFriends                                    #
#                                                                              #
# UltimateSmashFriends is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by the Free#
# Software Foundation, either version 3 of the License, or (at your option) any#
# later version.                                                               #
#                                                                              #
# UltimateSmashFriends is distributed in the hope that it will be useful, but  #
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or#
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# You should have received a copy of the GNU General Public License along with #
# UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.           #
################################################################################

# standards import
import pygame
import time
import math
import os
import logging
import sys

import socket
import threading
import SocketServer

# my modules import
from loaders import image
import animations
import entity
import timed_event
import loaders

from level import Level
from event_manager import EventManager
from controls import Controls
from config import Config
#module to load fonts
from font import fonts
#remove game_font
game_font = fonts['sans']['normal']

from debug_utils import draw_rect

config = Config()


if not pygame.font:
    logging.debug('Warning, fonts disabled')
if not pygame.mixer:
    logging.debug('Warning, sound disabled')


class BadPlayersNetworkParamError(Exception):
    """
    Raised when the player params of a network server game is not correct.

    """
    pass


class Game (object):
    """
    The game base object, initiate and update everything when in game (not in
    menu).

    """
    def __init__(self, screen, level="biglevel", players_=(None, None, None, None)):
        """
        Initialize a game with a list of player and a level,
        level is the basename of the level in levels/

        """
        self.SIZE = (
            config.general['WIDTH'],
            config.general['HEIGHT']
            )

        self.notif = []
        self.ingame = True
        self.ended = False
        self.type = 'local'
        self.screen = screen

        self.items = []
        self.events = EventManager()
        self.gametime = 0

        #we load the bool for smooth scrolling here, for a better performance
        self.smooth_scrolling = loaders.get_gconfig().get("game", "smooth_scrolling") == "y"

        self.level = Level(level)
        if screen is not None:
            self.font = game_font
            self.zoom = 1
            # loading level
            self.level_place = [0, 0]
            self.game_font = game_font
            self.icon_space = self.SIZE[0]/len(players_)

            # loading players

        self.load_players(players_)

        #the optional progress bar for the players lives
        self.progress_bar_size = (82.5*config.general["WIDTH"]/800, 12.5*config.general["WIDTH"]/800)
        self.progress_bar_x = config.general["HEIGHT"]-25*config.general["WIDTH"]/800

        # various other initialisations
        self.last_clock = time.time()

        ## adding test events.
        self.add_world_event()

        # a countdown to the game end
        self.ending = 5.0

    def add_world_event(self):
        self.events.add_event(
                'ItemShower',
                (None, None),
                {
                    'freq': 15,
                    'world': self
                    }
                )

    def load_player(self, i, player):
        logging.debug('player '+str(i)+' loaded')
            #logging.debug(player)
        self.players.append(
                entity.Entity(
                    i+1,
                    self,
                    player.replace("AI", ""),
                    ((i+1)*self.SIZE[0]/5,100)
                    )
                )
        if player and "AI" in player.split(os.sep)[1][:2]:
            self.players[len(self.players)-1].ai = True

    def load_players(self, players_):
        """
        this function is responsible of adding the requested players to the
        game.

        """
        logging.debug('loading players')
        self.players = []
        for i,player in enumerate(players_):
            self.load_player(i, player)

        # events to make players appear into game
        # logging.debug('players insertion in game')
        for pl in self.players:
            self.events.add_event(
                    'DropPlayer',
                    (None, self.gametime),
                    params={
                        'world': self,
                        'entity': pl,
                        'gametime': self.gametime
                        })

    def addItem(
        self,
        item='heal',
        place=(550,50),
        reversed=False,
        upgraded=False,
        vector=(0,0),
        bullet=False):
        """
        Insert an item into game.

        """
        physic = not bullet

        try:
            os.listdir(os.path.join( config.sys_data_dir, 'items', item))
            self.items.append(
                    entity.Entity(
                        None,
                        self,
                        os.path.join( 'items', item,),
                        place=place,
                        vector=vector,
                        reversed=reversed,
                        visible=True,
                        present=True,
                        upgraded=upgraded,
                        physic=physic
                        )
                    )

        except OSError, e:
            if e.errno is 22:
                logging.debug(item+' is not a valid item.')
            else:
                raise
        except IOError, e:
            if e.errno is 2:
                logging.debug(item+' is not a valid item directory.')
                raise

    def draw_progress_bar_for_lives(self, player):
        self.screen.blit(
                image(
                    os.path.join(
                        config.sys_data_dir,
                        'misc',
                        'progress_bar_bg.png'
                        ),
                    scale=self.progress_bar_size
                    )[0],
                (
                -0.5*self.icon_space+player.num*self.icon_space,
                self.progress_bar_x
                )
            )
        if self.progress_bar_size[0] - self.progress_bar_size[0]*(player.percents*0.1+0.01) > 0:
            self.screen.blit(
                    image(
                        os.path.join(
                            config.sys_data_dir,
                            'misc',
                            'progress_bar.png'
                            ),
                        scale=(self.progress_bar_size[0] - self.progress_bar_size[0]*(player.percents*0.1+0.01), self.progress_bar_size[1])
                        )[0],
                    (
                    -0.5*self.icon_space+player.num*self.icon_space,
                self.progress_bar_x
                    )
                )

    def draw_player_portrait(self, num, player):
        self.screen.blit(
                 player.entity_skin.image,
                    (
                    -0.5*self.icon_space+player.num*self.icon_space,
                    self.SIZE[1]*.9
                    )
                )

        if loaders.get_gconfig().get("game", "displaylives") == "y" :
            self.screen.blit(
                     self.font.render(str(player.percents*10)[:3]+"%",
                     True,
                     pygame.color.Color("red")),
                        (
                        -0.5*self.icon_space+player.num*self.icon_space,
                        self.SIZE[1]*.9
                        )
                    )
        elif loaders.get_gconfig().get("game", "display_progress_bar_for_lives") == "y":
            self.draw_progress_bar_for_lives(player)

        self.draw_player_lives(player)

    def draw_player_lives(self, player):
        """ draw as much hearth as the player has lives on it's portrait
        """
        for i in range(player.lives):
            self.screen.blit(
                    image(
                        os.path.join(
                            config.sys_data_dir,
                            'misc',
                            'heart.png'
                            )
                        )[0],
                    (
                        -0.5 * self.icon_space +
                            player.num * self.icon_space +
                            32 +
                            i * self.icon_space / 40,
                        self.SIZE[1]*.9+10
                        )
                    )

    def draw_debug_player_coords(self, num, player):
        """ draw player coords, useful for debugging.
        """
        self.screen.blit(
                self.font.render(
                    str(player.place[0])+
                    ':'+
                    str(player.place[1]),
                    True,
                    pygame.color.Color('red')
                    ),
                (
                 self.SIZE[0] * 3 / 4,
                 num*self.SIZE[1] / 4
                )
                )

    def draw_debug_player_movement(self, num, player):
        """displays current key movement of player, useful for debuging
        """
        self.screen.blit(
                self.font.render(
                    player.entity_skin.current_animation,
                    True,
                    pygame.color.Color('red')
                    ),
                (
                 0,
                 num*self.SIZE[1] / 4
                )
                )

    def draw_debug_player_controls(self, num, player):
        """ displays current key sequence of player, useful for debuging
        """
        self.screen.blit(
                self.font.render(
                    str(debug_params['controls'].player_sequences[num+1]),
                    True,
                    pygame.color.Color('red')
                    ),
                (
                 0,
                 num*self.SIZE[1] / 4
                )
                )

    def draw_debug(self, debug_params):
        for num, player in enumerate(self.players):
            if 'coords' in debug_params:
                self.draw_debug_player_coords(num, player)

            if debug_params.get('actions', False):
                self.draw_debug_player_movement(num, player)

            if debug_params.get('controls', False):
                self.draw_debug_player_controls(num, player)

    def draw_portraits(self):
        """
        Draw player's portraits at bottom of the screen
        """
        #draw the background of the block where the lives are displayed
        hud_height = 75*config.general["WIDTH"]/800
        self.screen.blit(loaders.image(os.path.join(
            config.sys_data_dir,
            "misc",
            "hud.png"
            ), scale=(config.general["WIDTH"], hud_height))[0],
          (0,config.general["HEIGHT"]-hud_height)
        )

        for num, player in enumerate(self.players):
            self.draw_player_portrait(num, player)

    def draw(self, debug_params={}):
        """
        Draw every parts of the game on the screen.

        """
        self.center_zoom_camera()
        self.level.draw_before_players(
            self.screen, self.level_place, self.zoom,
            'levelshape' in debug_params and debug_params['levelshape'],
        )
        for entity in self.players+self.items:
            entity.present and entity.draw(
                self.level_place, self.zoom, self.screen, debug_params=debug_params
                )

        self.level.draw_after_players(
            self.screen, self.level_place, self.zoom,
            'levelmap' in debug_params and debug_params['levelmap'],
        )

        self.draw_portraits()
        self.draw_debug(debug_params)

        self.display_game_state()
        self.update_notif()

    def display_game_state(self):
        """
        Display if the game is ended by a won, or a draw, does nothing if the
        game is still running
        """

        alive_players = filter(entity.Entity.alive, self.players)

        if len(alive_players) == 1:
            self.screen.blit(
                    loaders.text(
                        alive_players[0].name.capitalize()+_(" WON!"),
                        fonts["bold"][15], 0, 0, 0),
                    (self.SIZE[0]/2, self.SIZE[1]/2)
                    )

        elif len(alive_players) == 0:
            self.screen.blit(game_font.render(
                _("OOPS... DRAW!!!"),
                True,
                pygame.color.Color("#"+
                    str(math.sin(self.ending/10)) [3:5]+
                    "50"+
                    str(math.sin(self.ending/10)) [3:5]+
                    "30"
                    )),
                (self.SIZE[0]/2, self.SIZE[1]/2))

    def draw_notif(self, notif):
        self.screen.blit(
                game_font.render(
                    str(notif[1]),
                    True,
                    pygame.color.Color("black")
                    ),
                (
                 self.SIZE[0]/4,
                 self.notif.index(notif)*self.SIZE[1]/20
                )
                )

    def update_notif(self):
        for notif in self.notif:
            if config.general['NOTIF_EFFECT'] == "True":
                if(len(notif) <3):
                    notif.append(notif[1][0])
                elif len(notif[2]) is not len(notif[1]):
                    notif[2] = notif[2] + notif[1][len(notif[2])]
            if(notif[0] +4 > time.time()):
                self.draw_notif(notif)
            else:
                self.notif.remove(notif)

    @property
    def precise_zoom(self):
        """
        Return the minimum scale of the level to use so every player is
        visible on screen, provided there is more than one player
        """
        if len(self.present_players) == 1:
            return 1

        else:
            ordered = sorted([ i.place[0] for i in self.present_players ])
            L = max(
                self.SIZE[0],
                max(1, ordered[-1] + 100)- max(1, ordered[0] - 100) * 1.25
                )

            ordered = sorted([ i.place[1] for i in self.present_players ])

            H = max( self.SIZE[1], ordered[-1] - ordered[0] * 1.25)

            return min (
                    1.0*self.SIZE[0] / L,
                    1.0*self.SIZE[1] / H
                    )

    @property
    def players_barycenter(self):
        if len(self.present_players) == 1:
            return self.present_players[0].rect[0:2]
        else:
            return (
                sum(i.place[0] for i in self.present_players) / len(self.present_players),
                sum(i.place[1] for i in self.present_players) / len(self.present_players)
                )

    def center_zoom_camera(self):
        self.present_players = [ i for i in self.players if i.present ]
        if len(self.present_players) is not 0:
            # there is a trade between zoom sharpness and speed so we force
            # the zoom level to be a limited precision value here, so the
            # image cache is more useful.
            self.zoom = (
                int(self.precise_zoom * config.general['ZOOM_SHARPNESS'])/
                (config.general['ZOOM_SHARPNESS']* 1.0)
            )

            players_barycenter = self.players_barycenter
            # calculate coordinates of top left corner of level
            # rect the barycenter of players at the center of the screen
            level_place = [
                 -(players_barycenter[0])*self.zoom+self.SIZE[0]/2 ,
                 -(players_barycenter[1])*self.zoom+self.SIZE[1]/2
                 ]

            if self.smooth_scrolling:
                # tends to the ideal position (nicer!)
                self.level_place[0] += (level_place[0] - self.level_place[0])/4
                self.level_place[1] += (level_place[1] - self.level_place[1])/4

            else:
                # move immediatly to the ideal position
                self.level_place = level_place

    def update_physics(self):
        """
        all physical interaction here would probably better in a physics
        engine, but lie here for now.

        """
        # agressive point collision between entities players.
        for entity in self.players + self.items:
            for target in self.players + self.items:
                entity.test_hit(target)

        # collision between players and items -- tests and consequences
        for player in filter(lambda x: "pick" in
                x.entity_skin.current_animation, self.players):
            for item in self.items:
                if player.rect.collidelist([item.rect,]) != -1:
                        item.entity_skin.change_animation(
                                'triger',
                                self,
                                params={
                                    'player': player,
                                    'entity': item
                                    }
                                )

    def update_items(self, deltatime):
        for item in self.items:
            item.update(
                         deltatime,
                         self.gametime,
                         self,
                         self.level_place,
                         self.zoom
                        )
            if item.rect.collidelist([self.level.border,]) == -1:
                item.lives = 0
            if item.lives <= 0:
                del(self.items[self.items.index(item)])

    def update_players(self, deltatime):
        for player in (p for p in self.players if p.present ):
            player.update(
                    deltatime,
                    self.gametime,
                    self,
                    self.level_place,
                    self.zoom
                    )

            # if the player is out of the level zone
            if player.rect.collidelist([self.level.border,]) == -1:
                print "player out!"
                self.events.add_event(
                        'PlayerOut',
                        (self.gametime, 0),
                        params={
                            'entity': player,
                            'world': self,
                            'gametime' : self.gametime
                            }
                        )

            if player.lives <= 0:
                logging.debug("player's DEAD")
                player.present = False

    def update(self, debug_params={}, deltatime=0):
        """
        sync everything to current time. Return "game" if we are still in game
        mode, return "menu" otherwise.

        """
        # calculate elapsed time

        # frame limiter
        while deltatime < 1.0/config.general['MAX_FPS']:
            deltatime = time.time() - self.last_clock

        if deltatime < 1.0:
            # #FIXME this is a workaround the bug allowing game to evolve
            # while being "paused" but only works for pause > 1 second
            self.gametime += deltatime

        self.last_clock = time.time()

        self.events.update(deltatime, self.gametime)
        self.level.update(self.gametime)
        self.update_players(deltatime)
        self.update_physics()
        self.update_items(deltatime)

        players_left = len(filter(entity.Entity.alive, self.players))
        if players_left <= 1:
            # there is only one player left then the game need to end after a
            # short animation
            #decount time
            self.ending -= deltatime

        # if animation time elapsed, return to menu
        if self.ending <= 0:
            self.ended = True
            self.ingame=False
            return 'menu'

        if players_left == 1:
            return 'victory'

        return 'game'

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def __init__(self):
        super()
        self.sharedMemory = sharedMemory()

    def handle(self):
        try:
            self.sharedMemory.lock.acquire()
            self.id = self.sharedMemory.get('current_client_id')
            clients = self.sharedMemory.get('clients')
            clients.append({})
            self.sharedMemory.release()
            while True:
                data = self.request.recv(1024)
                if NetworkServerGame().started:
                    pass
                else:
                    if data[:len("<character>")] == "<character>":
                        clients = self.sharedMemory.get('clients')
                        clients[self.id].name = data[len('<character>'):]
                        self.sharedMemory.set('clients', clients)

                    if data[:len("<name>")] == "<name>":
                        clients = self.sharedMemory.get('clients')
                        clients[self.id].name = data[len('<name>'):]
                        self.sharedMemory.set('clients', clients)

                    if data[:len("<level>")] == "<level>":
                        clients = self.sharedMemory.get('level')
                        clients[self.id].name = data[len('<name>'):]
                        self.sharedMemory.set('clients', clients)

                    if data[:len("<message>")] == "<message>":
                        self.sharedMemory.append(
                            'messages',
                            self.sharedMemory.get('clients')[self.id]+
                                ': '+data[len("<message>"):]
                            )
                self.request.send(response)
        except:
            raise
            logging.info("client quit")

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class sharedMemory(object):
    """
    Useful to share information between threads, this is a singleton with thread safe access

    """
    __shared_state = {}
    lock = threading.RLock()
    def __init__(self):
        self.__dict__ = self.__shared_state
        self.dict = {}

    def set(self, key, value):
        if key in self.dict:
            self.dict[key]['lock'].acquire()
            self.dict[key]['value'] = value
            self.dict[key]['lock'].release()
        else:
            self.lock.acquire()
            self.dict[key] = {'lock': threading.RLock(), 'value': value}
            self.lock.release()

    def append(self, key, value):
        """
        append the value to the dict referenced by the key.
        """
        if key in self.dict:
            self.dict[key]['lock'].acquire()
            self.dict[key]['value'].append(value)
            self.dict[key]['lock'].release()
        else:
            self.lock.acquire()
            self.dict[key] = {'lock': threading.RLock(), 'value': [value,]}
            self.lock.release()

    def get(self, key):
        return self.dict[key]['value']

class NetworkServerGame(Game):
    """
    This particular version of the game class will accept connection of client,
    listen their information about keys hit by the players, update physics and
    send new postions of every entities, to every network players.

    """
    def __init__(self):
        """
        Initialize a game with a list of player and a level,
        level is the basename of the level in media/levels/

        """
        self.sharedMemory = sharedMemory()
        self.sharedMemory.set('clients', [])

        players = []
        level = ""

        self.current_client_id = 0
        self.server = ThreadedTCPServer(
            ('0.0.0.0', config.general['NETWORK_PORT']),
            ThreadedTCPRequestHandler
            )
        ip, port = self.server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.setDaemon(True)
        server_thread.start()
        logging.info("Server loop running in thread:", server_thread.getName())

        # choose level

        while len(self.sharedMemory.get('clients')) < 4:
            time.sleep(1)

        Game.__init__(self, None, level, players)
        self.begin(caracters, level)

    def begin(self, level, players_):
        """
        Stop waiting for players, and start the real game.

        """
        pass

    def draw(self):
        """
        As we are in server mode, there will be no drawing.

        """
        logging.info(self.gamestring)
        pass

    def update(self, debug_params={}):
        super(debug_params)
        self.gamestring = ";".join(
            [ x.serialize() for x in self.players+self.items]
        )+'|'+self.level.serialize()

    def __del__(self):
        self.server.shutdown()

class NetworkClientGame(Game):
    """
    This particular version of the game class will try to connect to a server
    game, will send information about the player, his skin and the updates
    about the local player(s)'s movements. And draw the game based on
    informations sent by the server.

    """
    def __init__(self, screen, serverAddress, serverPort,
                 players_=(None, None, None, None), votemap='maryoland'):
        """
        We connect to the server and send information about our players.

        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))

        for i in range(10):
            sock.send(message+" "+str(i))
            response = sock.recv(1024)
            logging.info("Received: %s" % response)
            time.sleep(1)

        sock.close()


    def begin( self, players=[], level='' ):
        """
        Initiation of the game itself, we load the level, and the skins of the
        player we know of

        """
        pass

    def update(self, time):
        pass

