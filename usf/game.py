# set encoding: utf-8
################################################################################
# copyright 2008-2011 Gabriel Pettier <gabriel.pettier@gmail.com>              #
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

'''
The game module is centered about the core of the game, the Game class initiate
and update all elements of the game, namely level, entities and events.

'''

# standards import
import pygame
import time
import math
import os
import logging

# my modules import
from usf.config import Config
from usf.event_manager import EventManager
from usf.font import fonts
from usf.level import Level
from usf.loaders import image
from usf.entity import Entity
import usf.loaders as loaders

from usf.translation import _

GAME_FONT = fonts['sans']['normal']

CONFIG = Config()


if not pygame.font:
    logging.debug('Warning, fonts disabled')
if not pygame.mixer:
    logging.debug('Warning, sound disabled')


class BadPlayersNetworkParamError(Exception):
    """
    Raised when the player params of a network server game is not correct.

    """
    pass


class Game(object):
    """
    The game base object, initiate and update everything when in game (not in
    menu).
    """

    def __init__(self, screen, level="biglevel", players_=(None, None, None,
        None)):
        """
        Initialize a game with a list of player and a level,
        level is the basename of the level in levels/
        """

        self.size = (
            CONFIG.general['WIDTH'],
            CONFIG.general['HEIGHT'])

        self.first_frame = True
        self.notif = []
        self.type = 'local'
        self.screen = screen

        self.items = []
        self.events = EventManager()
        self.gametime = 0

        #we load the bool for smooth scrolling here, for a better performance
        self.smooth_scrolling = CONFIG.general["SMOOTH_SCROLLING"]

        self.level = Level(level)
        if screen is not None:
            self.zoom = 1
            # loading level
            self.level_place = [0, 0]
            self.icon_space = self.size[0]/len(players_)

            # loading players

        self.load_players(players_)

        #the optional progress bar for the players lives
        self.progress_bar_size = (
                82.5*CONFIG.general["WIDTH"]/800,
                12.5*CONFIG.general["WIDTH"]/800)

        self.progress_bar_x = (
                CONFIG.general["HEIGHT"] - 25 * CONFIG.general["WIDTH"] / 800)

        # a countdown to the game end
        self.ending = 5.0

        self.max_fps = CONFIG.general['MAX_FPS']
        self.last_clock = 0

    def add_world_event(self):
        '''
        #XXX this currently add an itemshower to the game, should probably switch to
        starting level configured events.
        '''

        self.events.add_event(
                'ItemShower',
                (None, None),
                {'freq': 15, 'world': self})

        for e in self.level.get_events():
            self.events.add_event(e[0], e[1], {'world':self})

    def load_player(self, i, player):
        logging.debug('player '+str(i)+' loaded')
            #logging.debug(player)
        if player.split(os.sep)[1][:2] == 'AI':
            try:
                ai = int(player[player.index('AI') + 2])
                player = player.replace('AI'+str(ai), '')
            except ValueError:
                # support old syntax with no number
                ai = 5
                player = player.replace('AI', '')

        else:
            ai = False

        self.players.append(
                Entity(
                    num=i+1,
                    game=self,
                    entity_skinname=player,
                    place=((i + 1) * self.size[0] / 5, 100)))

        if ai:
            self.players[len(self.players)-1].ai = ai

    def load_players(self, players_):
        """
        this function is responsible of adding the requested players to the
        game.
        """

        logging.debug('loading players')
        self.players = []
        for i, player in enumerate(players_):
            self.load_player(i, player)

    def add_item(
        self,
        item='heal',
        place=(550, 50),
        reverse=False,
        upgraded=False,
        vector=(0, 0),
        bullet=False,
        physics=True,
        animation='static'):
        """
        Insert an item into game.

        """
        try:
            os.listdir(os.path.join(CONFIG.sys_data_dir, 'items', item))
            e = Entity(
                        num=None,
                        game=self,
                        entity_skinname=os.path.join('items', item),
                        place=place,
                        vector=vector,
                        reverse=reverse,
                        visible=True,
                        present=True,
                        upgraded=upgraded,
                        gravity=not bullet,
                        physic=not bullet,
                        animation=animation,
                        physics=physics)

            e.entity_skin.change_animation(animation, self, {'entity': e})

            self.items.append(e)

        except OSError, e:
            if e.errno is 22:
                logging.debug(item+' is not a valid item.')
            else:
                raise
        except IOError, e:
            if e.errno is 2:
                logging.debug(item+' is not a valid item directory.')
                raise

        return e

    def draw_progress_bar_for_lives(self, player):
        """ heh, draw progree bar for lives of the player
        """
        self.screen.blit(
                image(
                    os.path.join(
                        CONFIG.sys_data_dir,
                        'misc',
                        'progress_bar_bg.png'),
                    scale=self.progress_bar_size)[0],
                (
                -0.5*self.icon_space+player.num*self.icon_space,
                self.progress_bar_x))

        if (self.progress_bar_size[0] -
                self.progress_bar_size[0] * (player.percents * 0.1 + 0.01) > 0):
            self.screen.blit(
                    image(
                        os.path.join(
                            CONFIG.sys_data_dir,
                            'misc',
                            'progress_bar.png'),
                        scale=(self.progress_bar_size[0] -
                            self.progress_bar_size[0] * (
                                player.percents * 0.1 + 0.01),
                            self.progress_bar_size[1]))[0],
                    (
                    -0.5*self.icon_space+player.num*self.icon_space,
                self.progress_bar_x))

    def draw_player_portrait(self, player):
        """ draw, like... the player portrait? :D
        """
        self.screen.blit(
                 image(player.entity_skin.image, scale=(30, 30))[0],
                    (
                    -0.5*self.icon_space+player.num*self.icon_space,
                    self.size[1]*.9))

        if loaders.get_gconfig().get("game", "displaylives") == "y":
            self.screen.blit(
                     GAME_FONT.render(str(player.percents*10)[:3]+"%",
                     True,
                     pygame.color.Color("red")),
                        (
                        -0.5*self.icon_space+player.num*self.icon_space,
                        self.size[1]*.9))

        elif loaders.get_gconfig().get("game",
                "display_progress_bar_for_lives") == "y":
            self.draw_progress_bar_for_lives(player)

        self.draw_player_lives(player)

    def draw_player_lives(self, player):
        """ draw as much hearth as the player has lives on it's portrait
        """
        for i in range(player.lives):
            self.screen.blit(
                    image(
                        os.path.join(
                            CONFIG.sys_data_dir,
                            'misc',
                            'heart.png'))[0],
                    (
                        -0.5 * self.icon_space +
                            player.num * self.icon_space +
                            32 +
                            i * self.icon_space / 40,
                        self.size[1]*.9+10))

    def draw_debug_player_coords(self, num, player):
        """ draw player coords, useful for debugging.
        """
        self.screen.blit(
                GAME_FONT.render(
                    str(player.place[0])+
                    ':'+
                    str(player.place[1]),
                    True,
                    pygame.color.Color('red')),
                (
                 self.size[0] * 3 / 4,
                 num*self.size[1] / 4))


    def draw_debug_player_controls(self, num, controls):
        """ displays current key sequence of player, useful for debuging
        """
        for i, k in enumerate(controls.player_sequences[num]):
            self.screen.blit(
                    loaders.image(
                        os.path.join(
                            CONFIG.sys_data_dir,
                            'misc','key_' + k[0].lower() + '.png'))[0],
                    (num * self.size[0] / 4 + i * 50, 0 + 100 * (num % 2)))

    def draw_debug(self, debug_params):
        """ manae all de debug drawings provided by the class
        """
        for num, player in enumerate(self.players):
            if 'coords' in debug_params:
                self.draw_debug_player_coords(num, player)

            if debug_params.get('controls', False):
                self.draw_debug_player_controls(num, debug_params['controls'])

    def draw_portraits(self):
        """
        Draw player's portraits at bottom of the screen
        """
        #draw the background of the block where the lives are displayed
        hud_height = 75 * CONFIG.general["WIDTH"] / 800
        self.screen.blit(loaders.image(os.path.join(
            CONFIG.sys_data_dir,
            "misc",
            "hud.png"),
            scale=(CONFIG.general["WIDTH"], hud_height))[0],
            (0, CONFIG.general["HEIGHT"]-hud_height))

        for player in self.players:
            self.draw_player_portrait(player)

    def draw(self, debug_params=dict()):
        """
        Draw every parts of the game on the screen.

        """
        self.center_zoom_camera()
        self.level.draw_before_players(
            self.screen, self.level_place, self.zoom,
            'levelshape' in debug_params and debug_params['levelshape'])

        for e in self.players + self.items:
            if e.present:
                e.draw(self.level_place, self.zoom, self.screen,
                        debug_params=debug_params)

        self.level.draw_after_players(
            self.screen, self.level_place, self.zoom,
            'levelmap' in debug_params and debug_params['levelmap'])

        self.draw_portraits()
        self.draw_debug(debug_params)

        self.display_game_state()
        self.update_notif()

    def display_game_state(self):
        """
        Display if the game is ended by a won, or a draw, does nothing if the
        game is still running
        """

        alive_players = filter(Entity.alive, self.players)

        if len(alive_players) == 1:
            self.screen.blit(
                    loaders.text(
                        alive_players[0].name.capitalize()+_(" WON!"),
                        fonts["bold"][15], 0, 0, 0),
                    (self.size[0]/2, self.size[1]/2))

        elif len(alive_players) == 0:
            self.screen.blit(GAME_FONT.render(
                _("OOPS... DRAW!!!"),
                True,
                pygame.color.Color("#"+
                    str(math.sin(self.ending/10)) [3:5]+
                    "50"+
                    str(math.sin(self.ending/10)) [3:5]+
                    "30")),
                (self.size[0]/2, self.size[1]/2))

    def draw_notif(self, notif):
        """ drow notifications on the screen
        """
        self.screen.blit(
                GAME_FONT.render(
                    str(notif[1]),
                    True,
                    pygame.color.Color("black")),
                (
                 self.size[0]/4,
                 self.notif.index(notif)*self.size[1]/20))

    def update_notif(self):
        """ update and draw notifs,
        """
        for notif in self.notif:
            if CONFIG.general['NOTIF_EFFECT'] == "True":
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
            x = [i.place[0] for i in self.present_players]
            y = [i.place[1] for i in self.present_players]

            return min(
                    self.size[0] / max(self.size[0], (max(x) - min(x)) * 1.25),
                    self.size[1] / max(self.size[1], (max(y) - min(y)) * 1.5))

    @property
    def players_barycenter(self):
        """ return the barycenter of all present players, to help place the
        camera
        """
        if len(self.present_players) == 1:
            return self.present_players[0].rect[0:2]
        else:
            return (
                    sum(i.place[0] for i in self.present_players) /
                    len(self.present_players),
                    sum(i.place[1] for i in self.present_players) /
                    len(self.present_players))

    def center_zoom_camera(self):
        """ set the camera place and zoom to display as much player as
        possible, without moving the camera too fast.
        """
        self.present_players = [i for i in self.players if i.present]
        if self.present_players:
            # there is a trade between zoom sharpness and speed so we force
            # the zoom level to be a limited precision value here, so the
            # image cache is more useful.
            self.zoom = (
                int(self.precise_zoom * CONFIG.general['ZOOM_SHARPNESS'])/
                (CONFIG.general['ZOOM_SHARPNESS'] * 1.0))

            players_barycenter = self.players_barycenter
            # calculate coordinates of top left corner of level
            # rect the barycenter of players at the center of the screen
            level_place = [
                 -(players_barycenter[0]) * self.zoom + self.size[0] / 2,
                 -(players_barycenter[1]) * self.zoom + self.size[1] / 2]

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
                if target is not entity and not target.invincible:
                    entity.test_hit(target)

        # collision between players and items -- tests and consequences
        for player in filter(lambda x: "pick" in
            x.entity_skin.current_animation, self.players):
            for item in self.items:
                if player.rect.collidelist([item.rect, ]) != -1:
                    item.entity_skin.change_animation(
                            'triger',
                            self,
                            params={'player': player, 'entity': item})

    def update_items(self, deltatime):
        """ trigger update on all the present items
        """
        for item in self.items:
            item.update(
                         deltatime,
                         self.gametime,
                         self)

            if not item.rect.colliderect(self.level.border):
                item.set_lives(0)

            if not item.lives:
                del(self.items[self.items.index(item)])

    def update_players(self, deltatime):
        """ trigger update on all the present players
        """
        for player in filter(Entity.is_present, self.players):
            player.update(
                    deltatime,
                    self.gametime,
                    self)

            # if the player is out of the level zone
            if not player.rect.colliderect(self.level.border):
                self.events.add_event(
                        'PlayerOut',
                        (self.gametime, 0),
                        params={
                            'entity': player,
                            'world': self,
                            'gametime': self.gametime})

            if player.lives <= 0:
                player.set_present(False)

    def backup_items(self):
        """ return a backup of the state of the items in game
        """
        return (self.items[:], tuple((i.backup() for i in self.items)))

    def restore_items(self, backup):
        """ restore items and their states from a known backup state in the
        game
        """
        self.items = backup[0]
        for i, b in zip(self.items, backup[1]):
            i.restore(b)

    def backup_players(self):
        """ return a backup of the state of the players in game 
        """
        return tuple((p.backup() for p in self.players))

    def restore_players(self, backup):
        """ restore players and their states from a known backup state in the
        game
        """
        for p, b in zip(self.players, backup):
            p.restore(b)

    def backup_skins(self):
        """ return a backup of the entity skins current state 
        """
        return tuple((e.entity_skin.backup() for e in self.players+self.items))

    def restore_skins(self, backup):
        """ restore skins of entities from a known backup state
        """
        for e, b in zip(self.players + self.items, backup):
            e.entity_skin.restore(b)

    def backup(self):
        """
        save last_clock, events, items, levels, players of the game in their
        current state
        """
        return {
                'ending': self.ending,
                'events': self.events.backup(),
                'gametime': self.gametime,
                'items': self.backup_items(),
                'level': self.level.backup(),
                'players': self.backup_players(),
                'skins': self.backup_skins(),
                }

    def restore(self, backup):
        """
        restore the game state from _backup
        """
        self.ending = backup['ending']
        self.events.restore(backup['events'])
        self.gametime = backup['gametime']
        self.level.restore(backup['level'])
        self.restore_items(backup['items'])
        self.restore_players(backup['players'])
        self.restore_skins(backup['skins'])

    def update_clock(self, was_paused):
        """ update the clock of the game, and return the time passed since last
        update, is was_paused is set to True, then deltatime returned is 0 and
        no calculations are done, time is simply update.
        """
        if was_paused:
            deltatime = 0
        else:
            # calculate elapsed time if we are not in simulation
            # frame limiter
            deltatime = time.time() - self.last_clock
            while deltatime < 1.0 / self.max_fps:
                deltatime = time.time() - self.last_clock

            if deltatime >= 0.3:
                deltatime = 0
            self.gametime += deltatime

        self.last_clock = time.time()
        return deltatime

    def update(self, deltatime):
        """
        sync everything to current time. Return "game" if we are still in game
        mode, return "menu" otherwise.

        At the beggining of the game, we add world events, and then wait for
        the next frame before adding players, resolve bug 76585 on slower
        machines.
        """
        if self.first_frame:
            self.first_frame = False
            self.second_frame = True
            ## adding test events.
            self.add_world_event()

        elif self.second_frame:
            self.second_frame = False
            # events to make players appear into game
            # logging.debug('players insertion in game')
            for pl in self.players:
                self.events.add_event(
                        'DropPlayer',
                        (None, self.gametime + 1),
                        params={
                            'world': self,
                            'entity': pl,
                            'gametime': self.gametime})

        self.events.update(deltatime, self.gametime)
        self.level.update(self.gametime, deltatime)
        self.update_players(deltatime)
        self.update_physics()
        self.update_items(deltatime)

        players_left = len(filter(Entity.alive, self.players))

        if players_left <= 1:
            # there is only one player left then the game need to end after a
            # short animation
            #decount time
            self.ending -= deltatime

        # if animation time elapsed, return to menu
        if self.ending <= 0:
            return 'menu'

        if players_left == 1:
            return 'victory'

        return 'game'


class NetworkServerGame(Game):
    """ This class is intended for defining network server game implementation,
    not yet implemented!
    """
    def __init__(self):
        super(NetworkServerGame, self).__init__(self)
        raise NotImplementedError("NetworkServerGame is not implemented yet")


class NetworkClientGame(Game):
    """ This class is intended for defining network client game implementation,
    not yet implemented!
    """
    def __init__(self):
        super(NetworkClientGame, self).__init__(self)
        raise NotImplementedError("NetworkClientGame is not implemented yet")


