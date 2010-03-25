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
from level import Level
from controls import Controls
from config import Config
from widgets import game_font

from debug_utils import draw_rect
from singletonmixin import Singleton

from debug_utils import draw_rect

config = Config.getInstance()
SIZE = (config.general['WIDTH'],
        config.general['HEIGHT'])

if not pygame.font: logging.debug('Warning, fonts disabled')
if not pygame.mixer: logging.debug('Warning, sound disabled')

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
    notif = [[time.time(), "Notif"]]
    ingame = True
    def __init__(self, screen, level="biglevel", players_=(None, None, None, None)):
        """
        Initialize a game with a list of player and a level,
        level is the basename of the level in levels/

        """
        self.ended = False
        self.type = 'local'
        self.screen = screen

        self.events = []
        self.gametime = 0

        self.level = Level(level)
        if screen is not None:
            self.font = pygame.font.Font(None, 20)
            self.zoom = 1
            #self.testimage=load_image(os.path.join(config.data_dir,'items','item-heal'+os.extsep+'png')[0]
            # time for a loading screen ain't it?
            # loading level
            self.level_place = [0, 0]
            self.game_font = pygame.font.Font(None, 50)
            self.tmp_surface = self.screen.copy()

            # loading players

        self.players = []
        logging.debug('loading players')
        for i,player in enumerate(players_):
            logging.debug('player '+str(i)+' loaded')
            if player is not None:
                #logging.debug(player)
                if "AI" in player.split(os.sep)[1][:2]:
                    self.players.append(
                            entity.Entity(
                                i+1,
                                self,
                                player.replace("AI", ""),
                                ((i+1)*SIZE[0]/5,100)
                                )
                            )
                    self.players[len(self.players)-1].ai = True
                else:
                    self.players.append(
                            entity.Entity(
                                i+1,
                                self,
                                player,
                                ((i+1)*SIZE[0]/5,100)
                                )
                            )
        if screen is not None:
            self.icon_space = SIZE[0]/len(players_)

        # various other initialisations
        self.last_clock = time.time()

        self.items = []

        ## adding test events.
        self.events.append(
            timed_event.ItemShower(
                (None, None),
                {
                'freq': 15,
                'world': self
                }
                )
            )

        # insert players in game
        #logging.debug('players insertion in game')
        for pl in self.players:
            self.events.append(
                timed_event.DropPlayer(
                    (None, self.gametime),
                    params={
                    'world':self,
                    'entity':pl,
                    'gametime' : self.gametime
                    }
                    )
                )

        # a countdown to the game end
        self.ending = 5.0
        #logging.debug('DONE')

    def __del__(self):
        """
        destructor method of game, just useful for loging.

        """
        logging.debug('game deleted')

    def addItem(self, item='heal', place=(550,50), reversed=False,vector=(0,0)):
        """
        Insert an item into game.

        """
        try:
            os.listdir(os.path.join( config.data_dir, 'items', item))
            self.items.append(
                    entity.Entity(
                        None,
                        self,
                        os.path.join( 'items', item,),
                        place=place,
                        vector=vector,
                        reversed=reversed,
                        visible=True,
                        present=True
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

    def update_events(self, dt):
        """
        Called every frame, update every instancied event.

        """
        # FIXME: the index is not updated when we remove and element, so we may
        # skip outdated events until next frame. (it's a dit dirty).
        for event in self.events:
            if not event.update( dt, self.gametime ):
                self.events.remove(event)

    def draw(self, debug_params={}):
        """
        Draw every parts of the game on the screen.

        """
        self.level.draw_before_players(
            self.screen, self.level_place, self.zoom
        )
        for entity in self.players+self.items:
            entity.present and entity.draw(
                self.level_place, self.zoom, self.screen
                )

        self.level.draw_after_players(
            self.screen, self.level_place, self.zoom
        )

        # draw players portraits at bottom of screen
        for num, player in enumerate(self.players):
            self.screen.blit(
                     player.entity_skin.image,
                        (
                        -0.5*self.icon_space+player.num*self.icon_space,
                        SIZE[1]*.9
                        )
                    )

            self.screen.blit(
                     self.font.render(str(player.percents*10)[:3]+"%",
                     True,
                     pygame.color.Color("red")),
                        (
                        -0.5*self.icon_space+player.num*self.icon_space,
                        SIZE[1]*.9
                        )
                    )
            # draw player's lives.
            for i in range(player.lives):
                self.screen.blit(
                        image(
                            os.path.join(
                                config.data_dir,
                                'misc',
                                'heart.png'
                                )
                            )[0],
                        (
                         -0.5*self.icon_space+player.num*\
                         self.icon_space+i*self.icon_space/40,
                         SIZE[1]*.95
                        )
                        )

            # displays coords of player, usefull for debuging
            if 'coords' in debug_params:
                self.screen.blit(
                        self.font.render(
                            str(player.place[0])+
                            ':'+
                            str(player.place[1]),
                            True,
                            pygame.color.Color('red')
                            ),
                        (
                         SIZE[0] * 3 / 4,
                         num*SIZE[1] / 4
                        )
                        )
            if 'action' in debug_params:
                # displays current key movement of player, usefull for debuging
                self.screen.blit(
                        self.font.render(
                            player.entity_skin.current_animation,
                            True,
                            pygame.color.Color('red')
                            ),
                        (
                         0,
                         num*SIZE[1] / 4
                        )
                        )
            if 'controls' in debug_params:
                # displays current key sequence of player, usefull for debuging
                self.screen.blit(
                        self.font.render(
                            str(debug_params['controls'].player_sequences[num+1]),
                            True,
                            pygame.color.Color('red')
                            ),
                        (
                         0,
                         num*SIZE[1] / 4
                        )
                        )

        if len([player for player in self.players if player.lives > 0]) == 1:
            self.screen.blit(game_font.render(
                                        [
                                         player for player in self.players if
                                         player.lives > 0
                                        ][0].name.capitalize()+_(" WON!"),
                                        True,
                                        pygame.color.Color("#"+
                                            str(math.sin(self.ending/10)) [3:5]+
                                            "50"+
                                            str(math.sin(self.ending/10)) [3:5]+
                                            "30"
                                        )), (
                                              SIZE[0]/2,
                                              SIZE[1]/2)
                                            )

        if len([player for player in self.players if player.lives > 0]) == 0:
            # there is no more player in games, the game is tailed.
            self.screen.blit(game_font.render(
                                        _("OOPS... DRAW!!!"),
                                        True,
                                        pygame.color.Color("#"+
                                            str(math.sin(self.ending/10)) [3:5]+
                                            "50"+
                                            str(math.sin(self.ending/10)) [3:5]+
                                            "30"
                                        )),
                                            (
                                              SIZE[0]/2,
                                              SIZE[1]/2
                                            )
                                        )
        self.update_notif()

    def update_notif(self):
        for notif in self.notif:
            if config.general['NOTIF_EFFECT'] == "True":
                if(len(notif) <3):
                    notif.append(notif[1][0])
                elif len(notif[2]) is not len(notif[1]):
                    notif[2] = notif[2] + notif[1][len(notif[2])]
                if(notif[0] +4 > time.time()):
                    self.screen.blit(game_font.render(
                                            str(notif[2]),
                                            True,
                                            pygame.color.Color("black")),
                                            (SIZE[0]/4, self.notif.index(notif)*SIZE[1]/20)
                                                )
                else:
                    self.notif.remove(notif)
            else:
                if(notif[0] +4 > time.time()):
                    self.screen.blit(game_font.render(
                                            str(notif[1]),
                                            True,
                                            pygame.color.Color("black")),
                                            (SIZE[0]/4, self.notif.index(notif)*SIZE[1]/20)
                                                )
                else:
                    self.notif.remove(notif)
    def update(self, debug_params={}):
        """
        sync everything to current time. Return "game" if we are still in game
        mode, return "menu" otherwise.

        """
        # calculate elapsed time
        deltatime = 0

        # frame limiter
        while deltatime < 1.0/config.general['MAX_FPS']:
            deltatime = time.time() - self.last_clock

        self.gametime += deltatime
        sys.stdout.write("\r"+str(self.gametime))
        sys.stdout.flush()

        self.last_clock = time.time()

        if deltatime > .25:
            # if true we are lagging, prevent anything from happening until next
            # frame (and forget about passed time).
            logging.debug("too slow, forget this frame!")
            return "game"

        present_players = [ i for i in self.players if i.present ]
        if len(present_players) is not 0:
            if len(present_players) == 1:
                players_barycenter = present_players[0].rect[0:2]
                precise_zoom = 1
                self.zoom = int(precise_zoom * 0.70 *
                            config.general['ZOOM_SHARPNESS'])/(config.general['ZOOM_SHARPNESS']*
                            1.0 )
            # center the level around the barycenter of present players.
            else:
                ordered = sorted([ i.rect[0] for i in present_players ])
                L = max(
                    SIZE[0],
                    max(1, ordered[-1])- max(1, ordered[0])
                    )

                ordered = sorted([ i.rect[1] for i in present_players ])

                H = max( SIZE[1], ordered[-1], ordered[0])

                precise_zoom = min (
                        1.0*SIZE[0] / L,
                        1.0*SIZE[1] / H
                        )

                # there is a trade between zoom sharpness and speed so we force
                # the zoom level to be a limited precision value here, so the
                # image cache is more useful.

                self.zoom = (
                    int( precise_zoom * 0.70 * config.general['ZOOM_SHARPNESS'] )/
                    (config.general['ZOOM_SHARPNESS'] * 1.0)
                )

                players_barycenter = (
                    sum( i.rect[0] for i in present_players ) / len(present_players),
                    sum( i.rect[1] for i in present_players ) / len(present_players)
                    )

            #logging.debug(( self.zoom, lower - upper, rightwing - leftist))
            # calculate coordinates of top left corner of level
            # rect the barycenter of players at the center of the screen
            self.level_place = [
                 -(players_barycenter[0])*self.zoom+SIZE[0]/2 ,
                 -(players_barycenter[1])*self.zoom+SIZE[1]/2 
                 ]

        self.update_events( deltatime )

        # update level
        self.level.update(self.gametime)

        # update players
        for player in (p for p in self.players if p.present ):
            player.update(
                    deltatime,
                    self.gametime,
                    self.tmp_surface,
                    self,
                    self.level_place,
                    self.zoom
                    )

            # if the player is out of the level zone
            if player.rect.collidelist([self.level.border,]) == -1:
                self.events.append(
                        timed_event.PlayerOut(
                            (self.gametime, 0),
                            params={
                            'entity': player,
                            'world': self,
                            'gametime' : self.gametime
                            }
                            )
                        )
            if player.lives <= 0:
                #logging.debug("player's DEAD")
                player.present = False

        # FIXME: would be good to relocate this in an entity method, and
        # just loop on all the entities here.

        # agressive point collision between entities players.
        for entity in self.players+self.items:
            for point in entity.entity_skin.animation.agressivpoints:
                for pl in [ i for i in self.players+self.items\
                                if i is not entity\
                                and i.invincible is False ]:
                    if pl.collide_point([point[0][0]+entity.rect[0],
                                         point[0][1]+entity.rect[1]] )is not -1:
                        if pl.shield['on'] :
                            pl.shield['power'] -= math.sqrt(
                                                point[1][0]**2 + point[1][1]**2
                                                )/6000.0
                            pl.shield['power'] = max(0, pl.shield['power'])
                        else:
                            if entity.reversed != pl.reversed:
                                pl.vector = [-point[1][0]*(1+pl.percents),
                                              point[1][1]*(1+pl.percents)]
                            else:
                                pl.vector = [ point[1][0]*(1+pl.percents),
                                              point[1][1]*(1+pl.percents) ]
                            pl.percents += math.sqrt( point[1][0]**2\
                                                     +point[1][1]**2)/(30 * (100 -
                                                     pl.armor ))

                            pl.entity_skin.change_animation(
                                    "take",
                                    self,
                                    params={
                                    'entity': pl
                                    }
                                    )

        # collision between players and items -- tests and
        # consequences
        for player in self.players:
            for item in self.items:
                if player.rect.collidelist([item.rect,]) != -1 \
                and player.entity_skin.current_animation == "pick":
                        item.entity_skin.change_animation(
                                'triger',
                                self,
                                params={
                                'player': player,
                                'entity': item
                                }
                                )

        #update items
        for item in self.items:
            item.update(
                         deltatime,
                         self.gametime,
                         self.tmp_surface,
                         self,
                         self.level_place,
                         self.zoom
                        )
            if item.rect.collidelist([self.level.border,]) == -1:
                item.lives = 0
            if item.lives <= 0:
                del(self.items[self.items.index(item)])

        if len([player for player in self.players if player.lives > 0]) <= 1:
            # there is only one player left then the game need to end after a
            # short animation
            #decount time
            self.ending -= deltatime

        # if animation time elapsed, return to menu
        if self.ending <= 0:
            self.ended = True
            del(self.game_font)
            del(self.level)
            del(self.players)
            del(self.events)
            self.ingame=False
            return 'menu'

        return "game"

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        try:
            self.sharedMemory.lock.acquire()
            self.id = sharedMemory.get('current_client_id')
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
           print "client quit"

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class sharedMemory(Singleton):
    """
    Useful to share information between threads, this is a singleton with thread safe access

    """
    lock = threading.RLock()
    def __init__(self):
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
    def __init__(self, level="biglevel", players=(None, None, None, None)):
        """
        Initialize a game with a list of player and a level,
        level is the basename of the level in media/levels/

        """
        self.sharedMemory = sharedMemory.getInstance()
        self.sharedMemory.set('clients', [])

        Game.__init__(self, None, level, players)
        self.current_client_id = 0
        server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.setDaemon(True)
        server_thread.start()
        print "Server loop running in thread:", server_thread.getName()

        # choose level

        while len(self.sharedMemory.get(clients)) < 4:
            time.sleep(1)

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
        print self.gamestring
        pass

    def update(self, debug_params={}):
        super(debug_params)
        self.gamestring = ";".join(
            [ x.serialize() for x in self.players+self.items]
        )+'|'+self.level.serialize()

    def __del__(self):
        server.shutdown()

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
            print "Received: %s" % response
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

