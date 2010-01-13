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

import sys

# my modules import
from loaders import image
import music
import animations
import entity
#from AI import AI
import timed_event
import network
from level import Level
from controls import Controls
from config import config

from debug_utils import LOG, draw_rect

if not pygame.font: LOG().log('Warning, fonts disabled')
if not pygame.mixer: LOG().log('Warning, sound disabled')

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
        self.ended = False
        self.type = 'local'
        self.screen = screen

        self.LOG = LOG()
        self.events = []

        self.gametime = 0

        self.level = Level(level)
        if screen is not None:
            self.font = pygame.font.Font(None, 20)
            self.zoom = 1
            #self.testimage=load_image(os.path.join(MEDIA_DIRECTORY,'items','item-heal'+os.extsep+'png')[0]
            # time for a loading screen ain't it?
            # loading level
            self.level_place = [0, 0]
            self.game_font = pygame.font.Font(None, 50)
            image_src = os.path.join(
                        config['MEDIA_DIRECTORY'],
                        'misc',
                        'loading.png'
                        )

            self.heart = os.path.join(
                        config['MEDIA_DIRECTORY'],
                        'misc',
                        'heart.png'
                        )

            self.screen.blit(image(image_src)[0],(0,0))
            self.screen.blit(
                    self.game_font.render(
                        "level...",
                        True,
                        pygame.color.Color("white")
                        ),
                    ( 30, 4*config['SIZE'][1]/5 )
                    )

            pygame.display.flip()

            self.tmp_surface = self.screen.copy()

            # loading players
            self.screen.blit(image(image_src)[0],(0,0))
            self.screen.blit(
                    self.game_font.render(
                        "players...",
                        True,
                        pygame.color.Color("white")
                        ),
                    ( 30, 4*config['SIZE'][1]/5 )
                    )

            pygame.display.flip()

        self.players = []
        LOG().log('loading players')
        for i,player in enumerate(players_):
            LOG().log('player '+str(i)+' loaded')
            if player is not None:
                #LOG().log(player)
                if player.split(os.sep)[1][:2] == "AI":
                    self.players.append(
                            entity.Entity(
                                i+1,
                                self,
                                "characters" + os.sep + "stick-tiny",
                                ((i+1)*config['SIZE'][0]/5,100)
                                )
                            )
                    self.players[len(self.players)-1].ai = True
                else:
                    self.players.append(
                            entity.Entity(
                                i+1,
                                self,
                                player,
                                ((i+1)*config['SIZE'][0]/5,100)
                                )
                            )
        if screen is not None:
            self.icon_space = config['SIZE'][0]/len(players_)

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
        #LOG().log('players insertion in game')
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
        #LOG().log('DONE')

    def __del__(self):
        """
        destructor method of game, free as much resources as possible.

        """
        LOG().log('game deleted')
        del(self.__dict__)
        del(self)

    def addItem(self, item='heal', place=(550,50), reversed=False,vector=(0,0)):
        """
        Insert an item into game.

        """
        try:
            os.listdir(
                    os.path.join(
                        config['MEDIA_DIRECTORY'],
                        'items',
                        item
                        )
                    )
            the_item = entity.Entity(
                    None,
                    self,
                    os.path.join( 'items', item,),
                    place=place,
                    vector=vector,
                    reversed=reversed
                    )
            the_item.present = True
            the_item.visible = True
            self.items.append(the_item)
            return the_item

        except OSError, e:
            if e.errno is 22:
                self.LOG.log(item+' is not a valid item.')
            else:
                raise
        except IOError, e:
            if e.errno is 2:
                self.LOG.log(item+' is not a valid item directory.')
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
        self.level.draw_background( self.tmp_surface, (0,0))
        self.level.draw_level( self.tmp_surface ,self.level_place, self.zoom )
        #LOG().log(self.level.moving_blocs)
        for block in self.level.moving_blocs:
            block.draw( self.tmp_surface, self.level_place, self.zoom)

        for block in self.level.vector_blocs:
            block.draw( self.tmp_surface, self.level_place, self.zoom)

        for entity in self.players+self.items:
            entity.present and entity.draw(
                self.level_place, self.zoom, self.tmp_surface
                )

        self.level.draw_foreground(self.tmp_surface,self.level_place, self.zoom)
        self.screen.blit(self.tmp_surface,(0,0) )

        # minimap
        for rect in self.level.map:
            draw_rect(
                    self.screen,
                    pygame.Rect(
                        (rect[0])/8,
                        (rect[1])/8,
                        rect[2]/8,
                        rect[3]/8
                        ),
                    pygame.Color('grey')
                    )

        # draw players portraits at bottom of screen
        for num, player in enumerate(self.players):
            self.screen.blit(
                     player.entity_skin.image,
                        (
                        -0.5*self.icon_space+player.num*self.icon_space,
                        config['SIZE'][1]*.9
                        )
                    )

            self.screen.blit(
                     self.font.render(str(player.percents*10)[:3]+"%",
                     True,
                     pygame.color.Color("white")),
                        (
                        -0.5*self.icon_space+player.num*self.icon_space,
                        420
                        )
                    )
            # draw player's lives.
            for i in range(player.lives):
                self.screen.blit(
                                 image(self.heart)[0],
                                    (
                                    -0.5*self.icon_space+player.num*\
                                    self.icon_space+i*self.icon_space/40,
                                    config['SIZE'][1]*.95
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
                         config['SIZE'][0] * 3 / 4,
                         num*config['SIZE'][1] / 4
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
                         num*config['SIZE'][1] / 4
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
                         num*config['SIZE'][1] / 4
                        )
                        )

        if len([player for player in self.players if player.lives > 0]) == 1:
            self.screen.blit(self.game_font.render(
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
                                              config['SIZE'][0]/2,
                                              config['SIZE'][1]/2)
                                            )

        if len([player for player in self.players if player.lives > 0]) == 0:
            # there is no more player in games, the game is tailed.
            self.screen.blit(self.game_font.render(
                                        _("OOPS... DRAW!!!"),
                                        True,
                                        pygame.color.Color("#"+
                                            str(math.sin(self.ending/10)) [3:5]+
                                            "50"+
                                            str(math.sin(self.ending/10)) [3:5]+
                                            "30"
                                        )),
                                            (
                                              config['SIZE'][0]/2,
                                              config['SIZE'][1]/2
                                            )
                                        )

    def update(self, debug_params={}):
        """
        sync everything to current time. Return "game" if we are still in game
        mode, return "menu" otherwise.

        """
        # calculate elapsed time
        deltatime = 0

        # frame limiter
        while deltatime < 1.0/config['MAX_FPS']:
            deltatime = time.time() - self.last_clock

        self.gametime += deltatime
        sys.stdout.write("\r"+str(self.gametime))
        sys.stdout.flush()

        self.last_clock = time.time()

        if deltatime > .25:
            # if true we are lagging, prevent anything from happening until next
            # frame (and forget about passed time).
            LOG().log("too slow, forget this frame!")
            return "game"

        present_players = [ i for i in self.players if i.present ]
        if len(present_players) is not 0:
            if len(present_players) == 1:
                players_barycenter = present_players[0].rect[0:2]
                precise_zoom = 1
                self.zoom = int(precise_zoom * 0.70 *
                            config['ZOOM_SHARPNESS'])/(config['ZOOM_SHARPNESS']*
                            1.0 )
            # center the level around the barycenter of present players.
            else:
                ordered = [ i.rect[0] for i in present_players ]
                ordered.sort()
                leftist = max( 1, ordered[0] )
                rightwing = max( 1, ordered[-1] )
                L = max( config['SIZE'][0], rightwing - leftist )

                ordered = [ i.rect[1] for i in present_players ]
                ordered.sort()
                upper,lower = ordered[0], ordered[-1]
                H = max( config['SIZE'][1], lower - upper)

                precise_zoom = min (
                        1.0*config['SIZE'][1] / H,
                        1.0*config['SIZE'][0] / L
                        )

                # there is a trade between zoom sharpness and speed so we force
                # the zoom level to be a limited precision value here, so the
                # cache in level drawing is more useful.

                self.zoom = (
                    int( precise_zoom * 0.70 * config['ZOOM_SHARPNESS'] )/
                    (config['ZOOM_SHARPNESS'] * 1.0)
                )

                players_barycenter = (
                    sum( i.rect[0] for i in present_players ) / len(present_players),
                    sum( i.rect[1] for i in present_players ) / len(present_players)
                    )

            #LOG().log(( self.zoom, lower - upper, rightwing - leftist))
            # calculate coordinates of top left corner of level
            # rect the barycenter of players at the center of the screen
            self.level_place = [
                 -(players_barycenter[0])*self.zoom+config['SIZE'][0]/2 ,
                 -(players_barycenter[1])*self.zoom+config['SIZE'][1]/2 
                 ]

        #sounds.playqueu()

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
                #LOG().log("player's DEAD")
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
            return 'menu'

        return "game"

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
        Game.__init__(self, None, level, players)
        # wait fot clients to connect
        #TODO

        # choose level
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
        Game.update(self, debug_params)
        self.gamestring = ";".join(
            [ x.serialize() for x in self.players+self.items]
        )+'|'+self.level.serialize()


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
        pass

    def begin( self, players=[], level='' ):
        """
        Initiation of the game itself, we load the level, and the skins of the
        player we know of, we create a pool of entities skin on demand, to be
        able to display any required entity skin without dubble loading the
        same artworks.

        """
        pass

    def update(self, time):
        pass

