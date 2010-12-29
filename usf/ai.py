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
import game
import config

conf = config.Config()

import controls

#controls = controls.Controls()
class AI(object):
    def __init__(self):
        self.status = 'searching'
        self.target = None
        self.sequences_ai = list()

    def update(self, game, iam):
        entity = game.players[iam]
        #print "name: ", entity.name
        #print "animation: ", entity.entity_skin.current_animation
        #print "bloc_vector: ", entity.get_block_vector
        #print "invincible: ", entity.invincible
        #print "lives: ", entity.lives
        #print "onGround: ", entity.onGround
        #print "present: ", entity.present
        #print "rect: ", entity.rect
        #print "foot rect: ", entity.foot_collision_rect()
        #print "reversed: ", entity.reversed
        #print "shield power: ", entity.shield['power']
        #print "upgraded: ", entity.upgraded
        #print "vector: ", entity.vector
        #print "walking: ", entity.walking_vector
        #print "map: ",game.level.map
        #print "players: ", game.players
        #print "items: ", game.items
        #print "----------------------"

        if self.status == 'searching':
            targets = []
            bloc = entity.foot_collision_rect().collidelist(game.level.map)
            if bloc != -1:
                for p in game.players:
                    if (
                        p is not entity and
                        p.foot_collision_rect().collidelist(game.level.map) == bloc
                       ):
                       print p.name, entity.name
                       print "on the same bloc than "+p.name
                       targets.append((entity.dist(p), p))

            if targets:
                targets.sort()
                entity.reversed = (targets[0][1].place[0] < entity.place[0])
                if targets[0][0] > 100:#FIXME ugly hard value
                    entity.entity_skin.change_animation(
                        'walk',
                        game,
                        params={'entity': entity}
                        )
                    entity.walking_vector[0] = conf.general['WALKSPEED']

                else:
                    entity.entity_skin.change_animation(
                        'static',
                        game,
                        params={'entity': entity}
                        )
                    entity.walking_vector[0] = 0
                    self.status = 'fighting'
                    print "now fighting"
                    self.target = targets[0][1]

        elif self.status == 'fighting':
            target = self.target
            if entity.entity_skin.current_animation == 'static':
                entity.reversed = (target.place[0] < entity.place[0])
                dist = entity.dist(target)
                if False:
                    pass
                elif dist < 50 and target.place[1] > entity.place[1] + 20:#FIXME ugly hardcoded value
                    entity.entity_skin.change_animation(
                        'smash-up',
                        game,
                        params={'entity':entity}
                    )
                elif dist < 50:
                    entity.entity_skin.change_animation(
                        'hit',
                        game,
                        params={'entity':entity}
                    )
                elif dist < 80:
                    entity.entity_skin.change_animation(
                        'smash-straight',
                        game,
                        params={'entity':entity}
                    )
                elif target.place[1] > entity.place[1] + 100:#FIXME ugly hardcoded value
                    entity.entity_skin.change_animation(
                        'smash-up-jumping',
                        game,
                        params={'entity':entity}
                    )

                if dist > 100:
                    self.status = 'searching'
                    print "now searching"
        else:
            print "WTF?"
            self.status = 'searching'

