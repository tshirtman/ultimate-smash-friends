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

'''
This module manage controls, mainly on the keyboard, and either trigger
player's animations, or pass events to the menu system.

'''

# standards import
import os
import pygame
from pygame import locals as pygame_locals
from pygame.locals import (
        KEYDOWN,
        KEYUP,
        MOUSEMOTION,
        MOUSEBUTTONUP,
        MOUSEBUTTONDOWN,
        )

# my imports
from usf.config import Config
CONFIG = Config()

import usf.game as game


def key_shield(the_key, player, game_instance):
    """ activate shield if asked by the player, and if possible, return
    True, if the shield was activated
    """
    if ("_SHIELD" in the_key and
        player.entity_skin.current_animation in (
        'static', 'static_upgraded',
        'walk', 'walk_upgraded')):
        player.shield['on'] = True
        player.entity_skin.change_animation(
            'static',
            game_instance,
            params={'entity': player, 'anim_name': 'static'})

        player.set_walking_vector((0, player.walking_vector[1]))
        return True
    return False


def key_down_left(the_key, player, game_instance):
    """ manage incidence on walk animation if the player push down his left key
    """
    if "_LEFT" in the_key:
        if player.on_ground:
            player.entity_skin.change_animation(
                'walk',
                game_instance,
                params={'entity': player, 'anim_name': 'walk'})

        player.set_walking_vector([CONFIG.general['WALKSPEED'],
                player.walking_vector[1]])
        player.set_reversed(True)
        return True
    return False


def key_down_right(the_key, player, game_instance):
    """ manage incidence on walk animation if the player push down his right key
    """
    if "_RIGHT" in the_key:
        if player.on_ground:
            player.entity_skin.change_animation(
                    'walk',
                    game_instance,
                    params={'entity': player, 'anim_name': 'walk'})

        player.set_walking_vector([CONFIG.general['WALKSPEED'],
            player.walking_vector[1]])
        player.set_reversed(False)
        return True
    return False


def key_up_left(player, game_instance):
    """ manage incidence on walk animation if the player release his left key
    """
    if player.reversed:
        player.set_walking_vector([0, player.walking_vector[1]])

    if (player.entity_skin.current_animation in ('walk', 'walk_upgraded')):
        player.entity_skin.change_animation("static", game_instance,
                params={'entity': player})


def key_up_right(player, game_instance):
    """ manage incidence on walk animation if the player release his right key
    """
    if not player.reversed:
        player.set_walking_vector([0, player.walking_vector[1]])

    if (player.entity_skin.current_animation in ('walk', 'walk_upgraded')):
        player.entity_skin.change_animation("static", game_instance,
                params={'entity': player})


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
        """
        compare a sequence of keys events against our sequence starting from
        index
        """

        current = player.entity_skin.current_animation.replace('_upgraded', '')
        # if conditions are matched, and the sequence tested is as least as
        # long as our
        if ((not self.condition or current in self.condition)
                and len(seq) - index >= len(self.keys)):
            # test keys are the same, up to length of our combination

            i, j = 0, None
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
                return True

    def compare(self, seq, player):
        """Compare a sequence of key events against our sequence
        """

        for i in enumerate(seq):
            if self.compare_local(seq, player, i[0]):
                return True

        return False

    def __str__(self):
        """return a string representation of the sequence
        """

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
        self.keys = {}
        self.sequences = []
        self.load_keys()
        self.load_sequences()

    def load_keys(self):
        """ load player keys from configuration
        """
        self.keys = dict([[pygame_locals.__dict__[CONFIG.keyboard[key]], key]
                         for key in CONFIG.keyboard])

    def load_sequences(self):
        """ construct player combo sequences, using config (sequences.cfg) and
        known player keys
        """
        sequences_file = open(os.path.join(
                    CONFIG.sys_data_dir,
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

    def test_sequences(self, game_instance, numplayer):
        """
        test all sequences against player state/sequence
        if a sequence is recognized, the animation is applied
        """

        player = game_instance.players[numplayer]
        sequence = self.player_sequences[numplayer]
        for i in self.sequences:
            if i.compare(sequence, player):
                player.entity_skin.change_animation(
                        i.action,
                        game_instance,
                        params={'entity': player, 'anim_name': i.action})


    def handle_game_key_down(self, key, game_instance):
        """ manage key_down events
        """
        ret = 'game'
        if key in self.keys:
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

                    if not player.shield['on']:
                        if not  key_shield(the_key, player, game_instance):
                            if not key_down_left(the_key, player,
                                    game_instance):
                                key_down_right(the_key, player, game_instance)

                    #test sequences
                    self.test_sequences(game_instance, numplayer)
        return ret

    def handle_game_key_up(self, key, game_instance):
        """ manage key up events
        """
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
                    key_up_left(player, game_instance)

                elif "_RIGHT" in the_key:
                    key_up_right(player, game_instance)

    def handle_game_key(self, state, key, game_instance):
        """ Call handle_game_key_down of handle_game_key_up whether if the key
        event is DOWN or UP
        """
        if state is KEYDOWN:
            return self.handle_game_key_down(key, game_instance)

        elif state is KEYUP:
            self.handle_game_key_up(key, game_instance)
            return "game"

    def poll(self, game_instance, state):
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
                state = self.handle_game_key(
                        event.type, event.key, game_instance)


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

