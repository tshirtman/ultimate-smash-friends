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
from copy import deepcopy
from os import path


import game
import config
from loaders import memoize
conf = config.Config()

#controls = controls.Controls()

TIMESTEP = 250
MAXDEPTH = 2

@memoize
def possible_movements(movement):
    """ return the list of current legal movements for the player
    """
    result = list()
    with open(path.join(conf.sys_data_dir, 'sequences.cfg')) as f:
        line = f.readline().split('#')[0].split('\n')[0]
        print line
        while not line or "=" not in line and movement not in line:
            line = f.readline()
        line = f.readline()
        while "=" not in line:
            if line.split('#')[0].split('\n')[0] != '':
                result.append(line.split(':')[1].split('#')[0])

    return result

def simulate(game, iam, movement=None):
    """ change the player movement to movement, and jump 100ms in the future.
    if movement is none, just jump 100ms in the future.
    """
    game.players[iam].entity_skin.change_animation(movement)
    game.update(deltatime=TIMESTEP)

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
            game.players[iam].lives * 100 -
            game.players[iam].percents -
            reduce(lambda x, y: x + y.lives, [0,] + game.players) * 100 +
            reduce(lambda x, y: x + y.percents, [0,] + game.players) +
            game.players[iam].place[1] / 4
            )

def search_path(game, iam, max_depth):
    if max_depth == 0:
        return heuristic(game, iam), [Movement(game.gametime,None), ]

    result = (0, ())
    for movement in [None, ] + possible_movements(game.players[iam].entity_skin.current_animation):
        work_game = deepcopy(game)
        print "work_game: ", work_game
        simulate(work_game, iam, movement)
        score, movements = search_path(work_game, iam, max_depth-1)
        print "done"
        if score > result[0]:
            result = score, movements.append(Movement(game.gametime, movement))

    return result


class Movement(object):
    def __init__(self,time, movement):
        self.time = time
        self.movement = movement


class AI(object):
    def __init__(self):
        self.status = 'searching'
        self.sequences_ai = list()

    def update(self, game, iam):
        print "game: ",game
        entity = game.players[iam]
        open_positions = set()
        closed_positios = set()
        max_depth = MAXDEPTH # plan depth

        if not self.sequences_ai:
            self.sequences_ai = search_path(game, iam, max_depth)
        else:
            if game.gametime > self.sequence_ai[0].time:
                game.players[iam].entity_skin.change_animation(
                        self.sequence_ai.pop(0).movement)

