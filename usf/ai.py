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

import game
import config
from debug_utils import log_result
from loaders import memoize
conf = config.Config()

#controls = controls.Controls()

TIMESTEP = 250
MAXDEPTH = 2

#@log_result
@memoize
def possible_movements(movement):
    """ return the list of current legal movements for the player
    """
    result = list()
    with open(path.join(conf.sys_data_dir, 'sequences.cfg')) as f:
        line = f.readline().split('#')[0].split('\n')[0]

        while not line or "=" not in line and movement not in line:
            line = f.readline().split('#')[0].split('\n')[0]

        line = f.readline().split('#')[0].split('\n')[0]
        while "=" not in line:
            if line != '':
                result.append(line.split(':')[1])
            line = f.readline().split('#')[0].split('\n')[0]

    return result

def simulate(game, iam, movement=None):
    """ change the player movement to movement, and jump 100ms in the future.
    if movement is none, just jump 100ms in the future.
    """
    game.players[iam].entity_skin.change_animation(
            movement,
            game,
            {'entity': game.players[iam]})
    game.update(deltatime=TIMESTEP)

#@log_result
def heuristic(game, iam):
    """ return a score for the current state of the game, allow to chose a set
    of movement to do.

    value to take into account:
        number of lives
        % of damages
        number of lives of others
        % of damages to others
    """
    return (
            game.players[iam].lives * 100
            - game.players[iam].percents
            - sum((x.lives for x in game.players)) * 100
            + sum((x.percents for x in game.players))
            )

#@log_result
def search_path(game, iam, max_depth):
    assert game is not None
    if max_depth == 0:
        return heuristic(game, iam), [Movement(game.gametime,None), ]

    result = (-1000, ())
    backup = game.backup()
    for movement in [None, ] + possible_movements(game.players[iam].entity_skin.current_animation):
        simulate(game, iam, movement)
        score, movements = search_path(game, iam, max_depth-1)
        if score > result[0]:
            result = score, movements + [Movement(game.gametime, movement),]
        game.restore(backup)

    print "max_depth", max_depth, "best result", result
    return result


class Movement(object):
    def __init__(self,time, movement):
        self.time = time
        self.movement = movement

    def str(self):
        return ' '.join((str(self.time), str(self.movement)))


class AI(object):
    def __init__(self):
        self.status = 'searching'
        self.sequences_ai = dict()

    def update(self, game, iam):
        print "game: ",game
        if iam not in self.sequences_ai:
            self.sequences_ai[iam] = list()
        entity = game.players[iam]
        open_positions = set()
        closed_positions = set()
        max_depth = MAXDEPTH # plan depth

        print self.sequences_ai[iam]
        if not self.sequences_ai[iam]:
            self.sequences_ai[iam] = search_path(game, iam, max_depth)[1]
            print "sequences updated", self.sequences_ai[iam]
        else:
            if game.gametime >= self.sequences_ai[iam][0].time:
                game.players[iam].entity_skin.change_animation(
                        self.sequences_ai[iam].pop(0).movement,
                        game,
                        {'entity': game.players[iam]})

