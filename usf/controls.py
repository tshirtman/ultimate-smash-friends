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

# standards import
import os
import time
import logging
import pygame
from pygame import locals
from pygame.locals import (
        KEYDOWN,
        KEYUP,
        MOUSEMOTION,
        MOUSEBUTTONUP,
        MOUSEBUTTONDOWN,
        USEREVENT,
        )
# my imports
from config import Config
config = Config()

import game
from ai import AI


class Sequence(object):
    """
    Used to bind a character animation to a sequence of key of a player.
    condition allow to restrict the avaiability of the animation to certain
    current animation (the player can only double jump if he is already jumping
    for example)
    """

    def __init__(self, keys, action, condition=None):
        self.keys = keys
        self.action = action
        self.condition = condition

    def compare_local(self, seq, player, index):
        """Compare a sequence of key events against our sequence
        """

        current = player.entity_skin.current_animation.replace('_upgraded', '')
        # if conditions are matched, and the sequence tested is as least as
        # long as our
        if ((not self.condition or current in self.condition)
                and len(seq) - index >= len(self.keys)):
            # test keys are the same, up to length of our combination
            for i, j in enumerate(self.keys):
                # not the good one? stop here
                if seq[i + index][0] != j:
                    return False

            # all keys are good but sequence was already validated? exit
            if seq[i + index][2]:
                return False

            # first time this sequence is met, validate!
            else:
                seq[i + index][2] = True
                print "ok!"
                return True

    def compare(self, seq, player):
        for i, j in enumerate(seq):
            if self.compare_local(seq, player, i):
                return True
        return False

    def mark_sequence(self, seq):
        """
        mark self.keys keys in sequence, so each sequence is only activated one
        time.
        """

        seq[0][2] = True
        i = 0
        while seq and i < len(self.keys):
            if seq[i] != self.keys[i]:
                i = 0
            else:
                i += 1

    def __str__():
        return [str(i) for i in self.keys]


class Controls (object):
    """
    Catch pygame keyboard events and decides of the interaction with the game,
    game menu and entity instances. Key configuration are taken from
    sequences.cfg. This class can update and save configuration.
    """

    def __init__(self):
        #loaders.load_keys()
        self.player_sequences = [[], [], [], []]
        self.load_keys()
        self.load_sequences()

    def load_keys(self):
        self.keys = dict([[locals.__dict__[config.keyboard[key]], key]
                         for key in config.keyboard])

    def load_sequences(self):
        self.sequences = []
        sequences_file = open(os.path.join(
                    config.sys_data_dir,
                    'sequences'+os.extsep+'cfg'), 'r')

        lines = sequences_file.readlines()
        sequences_file.close()

        for i in lines:
            if i == '\n' or i[0] == '#':
                continue

            if i[0] == '=':
                condition = i.split('=')[1].split('\n')[0].split(',')
                continue

            tmp = i.replace(' ', '').split('\n')[0].split(':')

            seq = tmp[0].split('+')
            act = tmp[1]
            self.sequences.append(Sequence(seq, act, condition))

    def handle_menu_key(self, state, key, game):
        ret = "menu"
        if state is KEYDOWN:
            if key in self.keys:
                #logging.debug(self.keys[key])
                if self.keys[key] == "MENU_TOGGLE":
                    ret = "game"
                elif self.keys[key] == "QUIT":
                    if config.general['CONFIRM_EXIT']:
                        pygame.event.post(
                                pygame.event.Event(
                                    USEREVENT, key=self.keys[key]))
                    else:
                        pygame.event.post(pygame.event.Event(QUIT))

                elif self.keys[key] == "TOGGLE_FULLSCREEN":
                    pygame.display.toggle_fullscreen()

                elif self.keys[key] == "VALIDATE":
                    pygame.event.post(
                            pygame.event.Event(USEREVENT, key=self.keys[key]))
                else:
                    pygame.event.post(
                        pygame.event.Event(
                            USEREVENT,
                            player = int(self.keys[key].split('_')[0][-1]),
                            key = self.keys[key].split('_')[1]))
        return ret

    def test_sequences(self, game_instance, numplayer):
        player = game_instance.players[numplayer]
        sequence = self.player_sequences[numplayer]
        for i in self.sequences:
            if i.compare(sequence, player):
                player.entity_skin.change_animation(
                        i.action,
                        game_instance,
                        params={'entity': player})

                #i.mark_sequence(sequence)

    def key_shield(self, the_key, player, game_instance):
        if ("_SHIELD" in the_key and
            player.entity_skin.current_animation in (
            'static', 'static_upgraded',
            'walk', 'walk_upgraded')):
            player.shield['on'] = True
            player.entity_skin.change_animation(
                'static',
                game_instance,
                params={'entity': player})

            player.set_walking_vector((0, player.walking_vector[1]))
            return True
        return False

    def key_down_left(self, the_key, player, game_instance):
        if "_LEFT" in the_key:
            if player.onGround:
                player.entity_skin.change_animation(
                    'walk',
                    game_instance,
                    params={'entity': player})

            player.set_walking_vector([config.general['WALKSPEED'],
                    player.walking_vector[1]])
            player.set_reversed(True)
            return True
        return False

    def key_down_right(self, the_key, player, game_instance):
        if "_RIGHT" in the_key:
            if player.onGround:
                player.entity_skin.change_animation(
                        'walk',
                        game_instance,
                        params={'entity': player})

            player.set_walking_vector([config.general['WALKSPEED'],
                player.walking_vector[1]])
            player.set_reversed(False)
            return True
        return False

    def key_up_left(self, player, game_instance):
        if player.reversed:
            player.set_walking_vector([0, player.walking_vector[1]])

        if (player.entity_skin.current_animation in ('walk', 'walk_upgraded')):
            player.entity_skin.change_animation("static", game_instance,
                    params={'entity': player})
            return
        return

    def key_up_right(self, player, game_instance):
        if not player.reversed:
            player.set_walking_vector([0, player.walking_vector[1]])

        if (player.entity_skin.current_animation in ('walk', 'walk_upgraded')):
            player.entity_skin.change_animation("static", game_instance,
                    params={'entity': player})
            return
        return

    def handle_game_key_down(self, key, game_instance):
        ret = 'game'
        if key in self.keys:
            #FIXME: test if the player is not an AI.
            the_key = self.keys[key]
            if the_key == "QUIT":
                ret = "menu"
            elif the_key == "TOGGLE_FULLSCREEN":
                pygame.display.toggle_fullscreen()

            elif the_key == "VALIDATE":
                pass

            else:
                numplayer = int(the_key.split('_')[0][-1]) - 1
                keyname = the_key.split('_')[1]

                if numplayer >= len(game_instance.players):
                    return

                player = game_instance.players[numplayer]

                if not player.ai:
                    self.player_sequences[numplayer].append(
                            [keyname, game_instance.gametime, False])

                    # the player can't do anything if the shield is on

                    (player.shield['on']
                            or self.key_shield(the_key, player, game_instance)
                            or self.key_down_left(
                                the_key, player, game_instance)
                            or self.key_down_right(
                                the_key, player, game_instance))

                    #test sequences
                    self.test_sequences(game_instance, numplayer)
        return ret

    def handle_game_key_up(self, key, game_instance):
        if key in self.keys:
            the_key = self.keys[key]

            if the_key == "VALIDATE":
                return
            numplayer = int(self.keys[key].split('_')[0][-1]) - 1

            if numplayer >= len(game_instance.players):
                return

            player = game_instance.players[numplayer]

            if not player.ai:
                if "_SHIELD" in the_key:
                    player.shield['on'] = False

                elif "_LEFT" in the_key:
                    self.key_up_left(player, game_instance)

                elif "_RIGHT" in the_key:
                    self.key_up_right(player, game_instance)

    def handle_game_key(self, state, key, game_instance):
        if state is KEYDOWN:
            return self.handle_game_key_down(key, game_instance)

        elif state is KEYUP:
            self.handle_game_key_up(key, game_instance)
            return "game"

    def poll(self, game_instance, menu, state):
        """
        This function manages key events aquiered from local keyboard or sent
        by clients in the case of a networkk game.
        """

        # if this is a network server game
        if isinstance(game_instance, game.NetworkServerGame):
            while True:
                k = game_instance.server.fetch()
                if not k:
                    break
                else:
                    self.handle_game_key("game", k, game_instance)

        else:
            pygame.event.pump()
            for event in pygame.event.get([KEYDOWN, KEYUP]):
                if state is "game" and game:
                    state = self.handle_game_key(
                            event.type, event.key, game_instance)

                elif state is "menu":
                    state = self.handle_menu_key(event.type, event.key, menu)

            # eliminate unwanted events that fill the pool and break the
            # controls.
            pygame.event.clear([MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN])

            # clean sequences from outdated keys
            for index, sequence in enumerate(self.player_sequences):
                limit_time = game_instance.gametime - .5
                # clean the entire sequence if the last key is outdated.
                if sequence != [] and sequence[-1][1] < limit_time:
                    self.player_sequences[index] = []

        return state

