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
from os import path
import pygame
from copy import deepcopy

import config
from memoize import memoize
conf = config.Config()
from threading import Thread
import random

#controls = controls.Controls()

TIMESTEP = 0.25
MAXDEPTH = 1

walkspeed = conf.general['WALKSPEED']
sequences_file = path.join(conf.sys_data_dir, 'sequences.cfg')


@memoize
def possible_movements(movement='static'):
    """ return the list of current legal movements for the player
    """
    with open(sequences_file) as f:
        lines = f.readlines()

    result = set(('walk', )) if 'jump' not in movement else set()
    possible = False
    for l in lines:
        line = l.split('#')[0].split('\n')[0]

        if "=" in line:
            possible = movement in line
            continue

        elif possible:
            if ":" in line:
                result.add(line.split(':')[1])

    return tuple(result)


@memoize
def displacement_movement(s):
    return s in (
            'walk', 'jump', 'scnd-jump', 'smash-up-jumping', 'roll', 'pick')


@memoize
def fight_movement(s):
    return not displacement_movement(s)


def simulate(game, iam, m):
    """ change the player movement to movement, and jump TIMESTEP in the future.
    if movement is none, just jump TIMESTEP in the future.
    """
    entity = game.players[iam]
    entity.set_reversed(m.reverse)
    entity.set_walking_vector([m.walk and walkspeed or 0, None])
    entity.entity_skin.change_animation(
            m.movement,
            game,
            {'entity': entity})

    game.update(deltatime=TIMESTEP)


def under_lowest_plateform(game, player):
    for p in game.level.map:
        if p[1] > player.place[1]:
            return False

    return True


def over_some_plateform(game, player):
    for p in game.level.map:
        if p[1] > player.place[1] and p[0] < player.place[0] < p[0] + p[2]:
            return True

    return False


def heuristic_state(game, iam, player, others):
    """ return a score for the current state of the game, allow to chose a set
    of movement to do.

    value to take into account:
        number of lives
        % of damages
        number of lives of others
        % of damages to others
    """
    return (0
        + (0 if player.rect.colliderect(game.level.rect) else 1000)
        + (0 if player.invincible else 200)      # being invincible is good
        + (0 if player.onGround else 45)         # more conservative about jumps
        + (0 if player.upgraded else 100)        # being upgraded is cool
        + (0 if not under_lowest_plateform(game, player) else 1000)
        + (0 if over_some_plateform(game, player) else 30))

def heuristic_distance(game, iam, player, others):
    return min((player.dist(p) for p in others))


def heuristic_fight(game, iam, player, others):
    return (0
        + player.percents                       # avoid being hurt
        + sum((p.lives for p in others)) * 100  # kill people!
        - sum((p.percents for p in others)))    # hurt people, it's good


def search_path(game, iam, max_depth):
    gametime = game.gametime
    scores = []
    player = game.players[iam]
    others = (p for p in game.players if p is not player)

    if heuristic_distance(game, iam, player, others) > 100:
        if player.ai == 1:
            return (0, [Movement(gametime, 'static', player.reversed, False),])

        f = displacement_movement
        h = heuristic_distance
    else:
        f = fight_movement
        h = heuristic_fight

    movements = filter(f, possible_movements(
        game.players[iam].entity_skin.current_animation))

    if not movements:
        return (0, [])

    for movement in movements:
        for walk, reverse in (
                (True, True),
                (True, False),
                (False, True),
                (False, False)):
            M = Movement(gametime, movement, reverse, walk)
            b = game.backup() #no, this can't be factorized by moving it upper

            player = game.players[iam]
            others = (p for p in game.players if p is not player)

            simulate(game, iam, M)
            scores.append((
                h(game, iam, player, others) +
                heuristic_state(game, iam, player, others),
                M,
                game.backup()))

            game.restore(b)

    scores.sort()
    #print len(scores), [x[0] for x in scores]

    b = game.backup()
    if max_depth == 0:
        result = [(x[0], [x[1], ]) for x in scores[:2]]

    else:
        result = []
        r = (
                scores[5 - player.ai:5] if len(scores) >= 5
                else scores[max(0, len(scores) - player.ai):])

        for p in r:
            game.restore(p[2])
            score, movements = search_path(game, iam, max_depth - 1)
            result.append((p[0] + score, [p[1], ] + movements))

    #print "max_depth", max_depth, "best result", result
    game.restore(b)
    return min(result)


class Movement(object):
    """ #FIXME: doc!
    """

    def __init__(self, time, movement, reverse, walk):
        self.time = time
        self.reverse = reverse
        self.walk = walk
        self.movement = movement

    def __str__(self):
        return ' '.join((str(self.time), str(self.movement)))


class AI(object):
    """ #FIXME: doc!
    """

    def __init__(self):
        self.status = 'searching'
        self.sequences_ai = dict()
        self.next_update = dict()

    def update(self, game, iam):
        """
        iam represent the index of the player being controlled in the
        game.players list, this method will either create a list of future
        actions to do, or use actions that where planned before if there are
        some left to do.
        """

        if (iam in self.next_update and self.next_update[iam] > game.gametime):
            return

        # random is there to avoid too much ai being updated in the same frame
        self.next_update[iam] = game.gametime + (random.randint(20, 60)/100.0)

        #print "game: ",game
        if iam not in self.sequences_ai:
            self.sequences_ai[iam] = list()

        entity = game.players[iam]
        open_positions = set()
        closed_positions = set()
        max_depth = MAXDEPTH # plan depth

        s = search_path(game, iam, max_depth)
        if not s[1]:
            return

        self.sequences_ai[iam] = s[1]
        if game.gametime >= self.sequences_ai[iam][0].time:
            m = self.sequences_ai[iam].pop(0)
            entity.entity_skin.change_animation(
                    m.movement,
                    game,
                    {'entity': entity})
            entity.set_reversed(m.reverse)
            entity.set_walking_vector([m.walk and
                walkspeed or 0, entity.walking_vector[1]])

