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

import game
import config
from memoize import memoize
conf = config.Config()
from threading import Thread

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

        while not line or "=" not in line and movement not in line:
            line = f.readline().split('#')[0].split('\n')[0]

        line = f.readline().split('#')[0].split('\n')[0]
        while "=" not in line:
            if line != '':
                result.append(line.split(':')[1])
            line = f.readline().split('#')[0].split('\n')[0]

    return tuple(result)

def simulate(game, entity, movement=None, reverse=False, walk=False):
    """ change the player movement to movement, and jump 100ms in the future.
    if movement is none, just jump 100ms in the future.
    """
    entity.set_reversed(reverse)
    entity.set_walking_vector([walk and conf.general['WALKSPEED'] or 0,
        entity.walking_vector[1]])
    entity.entity_skin.change_animation(
            movement,
            game,
            {'entity': entity})
    assert entity in game.players
    game.update(deltatime=TIMESTEP)

def heuristic(game, entity):
    """ return a score for the current state of the game, allow to chose a set
    of movement to do.

    value to take into account:
        number of lives
        % of damages
        number of lives of others
        % of damages to others
    """
    return (
            min((entity.dist(e) for e in game.players if e is not entity))
            #- entity.lives * 100
            #+ entity.percents
            #+ sum((x.lives for x in game.players)) * 100
            #- sum((x.percents for x in game.players))
            )

def search_path(game, entity, max_depth):
    if max_depth == 0:
        return heuristic(game, entity), [Movement(game.gametime,None, False,
            False), ]

    result = (1000, ())
    gametime = game.gametime
    for movement in possible_movements(entity.entity_skin.current_animation):
        #for walk, reverse in ((True, True), (True, False), (False, True), (False, False)):
        for walk, reverse in ((True, True), (True, False), (False, True)):
            b = game.backup() #no, this can't be factorized by moving it 3 line^
            simulate(game, entity, movement, reverse, walk)
            score, movements = search_path(game, entity, max_depth-1)
            game.restore(b)
            if score < result[0]:
                result = score, movements + [Movement(gametime,
                    movement, reverse, walk),]

    #print "max_depth", max_depth, "best result", result
    return result

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

        #print self.sequences_ai[iam]
        if not self.sequences_ai[iam]:
            s = search_path(game, entity, max_depth)
            #print "sequences updated", s[0], ' '.join(map(str, s[1]))
            self.sequences_ai[iam] = s[1]
        else:
            if game.gametime >= self.sequences_ai[iam][-1].time:
                movement = self.sequences_ai[iam].pop()
                #print (
                        #"I", movement.movement, movement.reverse and "reversed"
                        #or "straight", movement.walk and "walking" or
                        #"not walking")
                entity.entity_skin.change_animation(
                        movement.movement,
                        game,
                        {'entity': entity})
                entity.reverse = movement.reverse
                entity.set_walking_vector([movement.walk and
                    conf.general['WALKSPEED'] or 0, entity.walking_vector[1]])


class AiThreadRunner(object):
    """
    This class will update the players AI when possible, in a thread-safe way
    """
    def __init__(self):
        """
        AI object must be given as a parameter
        """
        self.AI = AI()
        self.ended = True

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
            t = Thread(target = self.update, args=(game,))
            t.start()
        else:
            logging.warning('AI aleady already running!')

    def stop_AI(self):
        """
        """
        self.ended = True

