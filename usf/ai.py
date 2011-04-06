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
MAXDEPTH = 3

@memoize
def possible_movements(movement='static'):
    """ return the list of current legal movements for the player
    """
    with open(path.join(conf.sys_data_dir, 'sequences.cfg')) as f:
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

def simulate(game, iam, m):
    """ change the player movement to movement, and jump TIMESTEP in the future.
    if movement is none, just jump TIMESTEP in the future.
    """
    entity = game.players[iam]
    entity.set_reversed(m.reverse)
    entity.set_walking_vector([m.walk and conf.general['WALKSPEED'] or 0, None])
    entity.entity_skin.change_animation(
            m.movement,
            game,
            {'entity': entity})
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
    player = game.players[iam]
    others = (p for p in game.players if p is not player)

    return (
            max(200, min((player.dist(p) for p in others)))
            - player.lives * 100
            + player.percents
            + sum((p.lives for p in others)) * 100
            - sum((p.percents for p in others))
            )

def search_path(game, iam, max_depth):
    if max_depth == 0:
        return heuristic(game, iam), [Movement(game.gametime,None, False,
            False),]

    gametime = game.gametime
    scores = []
    for movement in possible_movements(movement=game.players[iam].entity_skin.current_animation):
        for walk, reverse in (
                (True, True),
                (True, False),
                (False, True),
                (False, False)):
            M = Movement(gametime, movement, reverse, walk)
            b = game.backup() #no, this can't be factorized by moving it upper
            simulate(game, iam, M)
            scores.append((heuristic(game, iam), M, game.backup()))
            game.restore(b)

    scores.sort()

    b = game.backup()
    result = []
    for p in scores[:2]:
        game.restore(p[2])
        score, movements = search_path(game, iam, max_depth - 1)
        print score, movements
        result.append((p[0] + score, [p[1],] + movements))

    #print "max_depth", max_depth, "best result", result
    game.restore(b)
    print min(result)
    return min((0, []), result)

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

    def update(self, game, iam):
        #print "game: ",game
        if iam not in self.sequences_ai:
            self.sequences_ai[iam] = list()
        entity = game.players[iam]
        open_positions = set()
        closed_positions = set()
        max_depth = MAXDEPTH # plan depth

        print game.gametime
        print 'before', '; '.join(map(str, self.sequences_ai[iam]))
        if not self.sequences_ai[iam]:
            s = search_path(game, iam, max_depth)
            print s
            print "sequences updated", s[0], ' '.join(map(str, s[1]))
            self.sequences_ai[iam] = s[1]
        else:
            print "ho", self.sequences_ai[iam][0].time
            if game.gametime >= self.sequences_ai[iam][0].time:
                print "hey!"
                m = self.sequences_ai[iam].pop(0)
                entity.entity_skin.change_animation(
                        m.movement,
                        game,
                        {'entity': entity})
                entity.set_reversed(m.reverse)
                entity.set_walking_vector([m.walk and
                    conf.general['WALKSPEED'] or 0, entity.walking_vector[1]])


class AiThreadRunner(object):
    """
    This class will update the players AI when possible, in a thread-safe way
    """
    def __init__(self, game):
        """
        AI object must be given as a parameter
        """
        self.AI = AI(game)
        self.ended = True
        self.thread = None

    def update(self, game):
        while not self.ended:
            pygame.time.wait(50)
            for i,j in enumerate(game.players):
                if j.ai and j.present:
                    self.AI.update(game, i)

    def start_AI(self, game):
        """
        """
        if self.ended:
            self.ended = False
            self.thread = Thread(target = self.update, args=(game,))
            self.thread.start()
            print "AI started"
        else:
            logging.warning('AI aleady already running!')

    def stop_AI(self):
        """
        """
        if self.ended == False:
            self.ended = True
            print "waiting for thread to stop"
            self.thread.join()
            print "ai stopped"


