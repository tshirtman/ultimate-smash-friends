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
import os
import time
import pygame
from pygame.locals import (
        KEYDOWN,
        KEYUP,
        MOUSEMOTION,
        MOUSEBUTTONUP,
        MOUSEBUTTONDOWN,
        USEREVENT,
        )
# my imports
from usf_modules.config  import (
    config,
    keyboard_config,
    sound_config,
    reverse_keymap,
    save_keys_conf
    )
from debug_utils import LOG
import game

class Sequence (object):
    """
    Used to bind an animation of a player to a sequence of key.
    """
    def __init__(self, player, keys, action, condition=None):
        self.player = player
        self.keys = keys
        self.action = action
        self.condition = condition

    def compare(self, seq, game_instance):
        if self.condition == ""\
        or len(game_instance.players) > self.player\
            and game_instance.players[self.player].entity_skin.current_animation\
            in self.condition :
            keyseq = [i[0] for i in seq]
            return self.keys == keyseq[-len(self.keys):]
        else:
            return False

    def __str__():
        return [str(i) for i in self.keys]

class Controls (object):
    """
    Catch pygame keyboard events and decides of the interraction with the game,
    game menu and entity instances. Key configuration are taken from
    sequences.cfg. This class can update and save configuration.

    """
    def __init__(self):
        #loaders.load_keys()
        self.keys = keyboard_config
        self.sequences = []
        self.player_sequences = [[],[],[],[]]
        sequences_file = open(os.path.join(
                config['SHARE_DIRECTORY'],
                'sequences'+os.extsep+'cfg')
                              , 'r')
        sequence_tmpl = []
        condition = ""
        for i in sequences_file.readlines():
            if i=='\n' or i[0] == '#':
                continue
            if i[0] == '=':
                condition=i.split('=')[1].split('\n')[0].split(',')
                continue
            tmp = i.replace(' ','').split('\n')[0].split(':')
            sequence_tmpl.append([condition[:], tmp[0].split('+'), tmp[1]])
        sequences_file.close()

        for player in range(4):
            for condition,seq,act in sequence_tmpl:
                tab=["PL"+str(player)+'_'+btn for btn in seq]
                self.sequences.append(Sequence(player-1, tab, act, condition))

            for i in range(4): self.player_sequences.append([])

    def getKeyByAction(self, action):
        if action in self.keys.values():
            return reverse_keymap[
                self.keys.keys()[
                        self.keys.values().index(action)
                        ]
            ]

    def assignKey(self, action):
        while True:
            event = pygame.event.wait()
            if event.type == KEYDOWN:
                try:
                    self.keys.pop(eval(self.getKeyByAction(action)))
                except TypeError:
                    pass
                self.keys[event.key] = action
                break

    def save(self):
        save_keys_conf(self.keys)

    def reload(self):
        self.keys = load_key_config()

    def handle_menu_key( self, state, key, game):
        ret = "menu"
        if state is KEYDOWN:
            if key in self.keys :
                #LOG().log(self.keys[key])
                if self.keys[key] == "MENU_TOGGLE":
                    ret = "game"
                elif self.keys[key] == "QUIT":
                    if config['CONFIRM_EXIT']:
                        pygame.event.post(
                                pygame.event.Event(
                                    USEREVENT,
                                    key=self.keys[key]
                                    )
                                )
                    else:
                        pygame.event.post(
                                pygame.event.Event(QUIT)
                        )
                elif self.keys[key] == "TOGGLE_FULLSCREEN":
                    pygame.display.toggle_fullscreen()

                elif self.keys[key] == "VALIDATE":
                    pygame.event.post(
                            pygame.event.Event(
                                USEREVENT,
                                key=self.keys[key]
                                )
                            )
                else: pygame.event.post(
                        pygame.event.Event(
                            USEREVENT,
                            player = int(self.keys[key].split('_')[0][-1]),
                            key = self.keys[key].split('_')[1]
                                          )
                                        )
        return ret

    def handle_game_key( self, state, key, game_instance ):
        ret = "game"
        if state is KEYDOWN:
            if key in self.keys:
                #FIXME: test if the player is not an AI.
                try:
                    numplayer = int(self.keys[key].split('_')\
                                [0][-1])-1
                    if(not game_instance.players[numplayer].ai):
                        self.player_sequences[numplayer].append((self.keys[key],time.time()))
                except:
                    pass # fail when the key not associated to a player eg:
                         # toggle_menu
                if isinstance(game_instance, game.NetworkClientGame):
                    game_instance.client.send(key,'down')

                elif isinstance(game_instance, game.NetworkServerGame):
                    pass
                else:
                    if self.keys[key] == "QUIT":
                        ret = "menu"
                        #pygame.event.set_grab(False)
                    elif self.keys[key] == "TOGGLE_FULLSCREEN":
                        pygame.display.toggle_fullscreen()
                    
                    if(not game_instance.players[numplayer].ai):
                        for player in game_instance.players:
                            pl = "PL"+str(player.num)
                            the_key = self.keys[key]
                            if pl not in the_key: continue
                            if "_LEFT" in the_key:
                                player.walking_vector[0] = config['WALKSPEED']
                                player.reversed = True

                            elif "_RIGHT" in the_key:
                                player.walking_vector[0] = config['WALKSPEED']
                                player.reversed = False

                        #test sequences
                        for sequence in self.player_sequences:
                            for i in self.sequences:
                                if i.compare( sequence, game_instance ):
                                    game_instance.players[i.player].entity_skin.change_animation\
                                            (
                                              i.action,
                                              game_instance,
                                              params={
                                                        'entity':game_instance.players[i.player]
                                                     }
                                            )

        elif state is KEYUP:
            if isinstance(game_instance,  game.NetworkClientGame):
                game_instance.client.send(key,'up')

            elif isinstance(game_instance, game.NetworkServerGame):
                pass
            else:
                try:
                    numplayer = int(self.keys[key].split('_')\
                                [0][-1])-1
                    if(not game_instance.players[numplayer].ai):
                        for player in game_instance.players:
                            if key not in self.keys : break
                            pl = "PL"+str(player.num)
                            if pl not in self.keys[key]: continue
                            if key in self.keys :
                                if "_LEFT" in self.keys[key]:
                                    player.walking_vector[0] = 0
                                    if player.entity_skin.current_animation == "walk":
                                        player.entity_skin.change_animation(
                                                "static",
                                                game_instance,
                                                params={'entity': player}
                                                )
                                elif "_RIGHT" in self.keys[key]:
                                    player.walking_vector[0] = 0
                                    if player.entity_skin.current_animation == "walk":
                                        player.entity_skin.change_animation(
                                                "static",
                                                game_instance,
                                                params={'entity': player}
                                                )
                except:
                    pass
        return ret

    def poll(self, game_instance, menu, state):
        """
        This function manages key events aquiered from local keyboard or sent
        by clients in the case of a networkk game.

        """
        if isinstance(game_instance, game.NetworkServerGame):
            while True:
                k = game_instance.server.fetch()
                if k == None: break
                else: self.handle_game_key( "game", k, game_instance )

        else:
            pygame.event.pump()
            for event in pygame.event.get( [ KEYDOWN, KEYUP ] ):
                if state is "game":
                    if game is not None:
                        state = self.handle_game_key( event.type, event.key, game_instance)
                    # forget other events
                    pygame.event.clear()

                elif state is "menu":
                    state = self.handle_menu_key( event.type, event.key, menu )

            # eliminate unwanted events that fill the pool and break the controls.
            pygame.event.clear( [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN] )

            # clean sequences from outdated keys
            for index, sequence in enumerate(self.player_sequences):
                limit_time = time.time()-.500
                # clean the entire sequence if the last key is outdated.
                if sequence != [] and sequence[-1][1] < limit_time:
                    self.player_sequences[index] = []

        return state

