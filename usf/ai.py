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

    result = set()
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
    return s in ('walk','jump','scnd-jump','smash-up-jumping','roll')

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

def heuristic_distance(game, iam):
    """ return a score for the current state of the game, allow to chose a set
    of movement to do.

    value to take into account:
        number of lives
        % of damages
        number of lives of others
        % of damages to others
    """
    player = game.players[iam]
    others = (p for p in game.players if p is not player)

    return (0
        + (1500 if not player.rect.colliderect(game.level.rect) else 0)
        - player.invincible * 100               # being invincible is good
        - player.lives * 100                    # avoid dying, ain't no fun kid
        - player.onGround * 50                  # more conservative about jumps
        - player.upgraded * 100                 # being upgraded is cool
        + min((player.dist(p) for p in others))
        )

def heuristic_fight(game, iam):
    player = game.players[iam]
    others = (p for p in game.players if p is not player)

    return (0
        + (500 if not player.rect.colliderect(game.level.rect) else 0)
        + player.percents                       # avoid being hurt
        + sum((p.lives for p in others)) * 100  # kill people!
        - player.invincible * 100               # being invincible is good
        - player.onGround * 50                  # more conservative about jumps
        - player.upgraded * 100                 # being upgraded is cool
        - sum((p.percents for p in others))     # hurt people, it's good
        )

def search_path(game, iam, max_depth):
    gametime = game.gametime
    scores = []
    if heuristic_distance(game, iam) > 100:
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
            simulate(game, iam, M)
            scores.append((h(game, iam), M, game.backup()))
            game.restore(b)

    scores.sort()
    #print len(scores), [x[0] for x in scores]

    b = game.backup()
    if max_depth == 0:
        result = [(x[0],[x[1],]) for x in scores[:2]]
    else:
        result = []
        for p in scores[:2]:
            game.restore(p[2])
            score, movements = search_path(game, iam, max_depth - 1)
            result.append((p[0] + score, [p[1],] + movements))

    #print "max_depth", max_depth, "best result", result
    game.restore(b)
    return min(result)

class Movement(object):
    def __init__(self, time, movement, reverse, walk):
        self.time = time
        self.reverse = reverse
        self.walk = walk
        self.movement = movement

    def __str__(self):
        return ' '.join((str(self.time), str(self.movement)))


class AI(object):
    def __init__(self):
        self.status = 'searching'
        self.sequences_ai = dict()
        self.last_update = None

    def update(self, game, iam):
        """
        iam represent the index of the player being controlled in the
        game.players list, this method will either create a list of future
        actions to do, or use actions that where planned before if there are
        some left to do.
        """
        self.last_update = game.gametime
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

