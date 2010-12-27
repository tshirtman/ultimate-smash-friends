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
import time
import pygame

from config import Config

config = Config()

class AI(object):
    sequences_ai = []
    last_vector =0
    wait_for= "static:mesure"
    walk = False
    max_height = 0
    max_height_verif = 0
    global_height = True
    position = []
    block = None
    wait_time = 0

    def escape_routine(self, entity):
        # this routine should decide what action to do next if the AI try to
        # escape from another entity
        pass

    def fight_routine(self, entity):
        # this routine should decide what action to do next if the AI try to
        # fight with an entity
        pass

    def find_routine(self, entity):
        # this routine should decide what action to do next if the AI try to
        # go to the place of an entity
        pass


    def forward_position(self, t):
        # this function should return the position of the player t milliseconds
        # forward in the future, if it persist in it's current movement.
        pass

    def update_enemy (self) :
        """
        This function update the information about different enemys
        """

        self.enemy_number = []
        self.enemy_position = []
        self.enemy_distance = []
        self.enemy_distanceh = []
        self.enemy_width = []

        for pl in [pl for pl in self.game.players if pl is not self.iam] :
            self.enemy_number.append (pl.num)
            self.enemy_position.append (pl.place)
            self.enemy_distance.append (self.iam.dist (pl))
            self.enemy_distanceh.append (pl.place[1]- self.iam.place[1])
            self.enemy_width.append(pl.entity_skin.animation.hardshape[2])

    def calculate_height(self):
        self.global_height = False
        #FIXME : a real function to calculate height
        #self.jump_height = float(self.iam.entity_skin.vectors['jump'][0][0][1])/float(10000)*1500
        self.jump_height = config.general['JUMP_HEIGHT']

    def update(self, game, iam):
        self.sequences_ai = []
        self.num = iam
        self.iam = game.players[iam]
        self.game = game
        #self.position.append(game.players[iam-1].place)
        if self.global_height ==True:
            self.calculate_height()
        self.update_enemy()
        self.choose_strategy()

    def choose_strategy(self):
        aix = self.iam.place[0]/8
        aiy = self.iam.place[1]/8
        enx = self.enemy_position[0][0]/8
        eny = self.enemy_position[0][1]/8
        self.block = None

        for block in self.game.level.map:
            #FIXME : Improve this code using hardshape
            if (block.right+80 > self.enemy_position[0][0] and
                block.left-80 < self.enemy_position[0][0] and
                block.top-80 < self.enemy_position[0][1] and
                block.top+80 > self.enemy_position[0][1]):
                #pygame.draw.line(self.game.screen, pygame.Color("red"), (block.left/8,block.top/8), (block.right/8,block.top/8))
                self.block = block
                break
            else:
                pygame.draw.line(self.game.screen, pygame.Color("green"), (block.left/8,block.top/8), (block.right/8,block.top/8))

        if self.block is not None:
            self.goto()

        #if the ennemy is at left
        if self.enemy_position[0][0] < self.iam.place[0] :
            self.iam.reversed = True
        else :
            self.iam.reversed = False

        if self.enemy_distance[0] < 100 :
            self.sequences_ai.append(("PL"+ str(self.num+1) + "_B",time.time()))

    def goto(self):
        # if not arrived
        if not(
                self.enemy_position[0][0] - self.iam.place[0] <= self.enemy_width and
                self.enemy_position[0][0] - self.iam.place[0] > 0
            ):
            #if i am on the same block :
            if (self.block.right+80 > self.iam.place[0] and
                self.block.left-80 < self.iam.place[0] and
                self.block.top-80 < self.iam.place[1] and
                self.block.top+80 > self.iam.place[1]):

                #self.game.notif.append([time.time(), "I am on your block"])
                self.iam.walking_vector[0] = config.general['WALKSPEED']
                self.walk = True

                if self.enemy_position[0][0] < self.iam.place[0] - self.iam.rect[2]:
                    #self.game.notif.append([time.time(), "I am on your right"])
                    self.sequences_ai.append(("PL"+ str(self.num+1) + "_LEFT",time.time()))
                elif(self.enemy_position[0][0] > self.iam.place[0] + self.iam.rect[2]):
                    #self.game.notif.append([time.time(), "I am on your left"])
                    self.sequences_ai.append(("PL"+ str(self.num+1) + "_RIGHT",time.time()))

                #to jump over another block
                for block in self.game.level.map:
                    if ( ((block.right < self.iam.place[0] and
                           block.right >self.enemy_position[0][0]) or
                          (block.left < self.iam.place[0] and
                           block.left >self.enemy_position[0][0])
                         ) and
                         ((block.top < self.iam.place[1] and
                           block.bottom > self.iam.place[1]) or
                          (block.bottom-100 < self.iam.place[1] and
                           block.top-100 > self.iam.place[1])
                         )
                       ):
                       #self.game.notif.append([time.time(), "I jump"])
                       self.sequences_ai.append(("PL"+ str(self.num+1) + "_UP",time.time()))
                       self.wait_time = time.time()

            elif self.wait_time +1.5 < time.time():
                self.walk = False
                self.iam.walking_vector[0] = 0
        else:
            #print self.enemy_position[0][0] - self.iam.place[0] <= self.enemy_width
            #print self.enemy_position[0][0] - self.iam.place[0]
            self.walk = False
            self.iam.walking_vector[0] = 0

