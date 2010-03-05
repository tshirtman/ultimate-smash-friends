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
import os

from usf_modules.new_config import Config
config = Config()
general = config.general
sound_config = config.audio
SHARE_DIRECTORY = config.config_dir
MEDIA_DIRECTORY = config.data_dir
SIZE = (general['WIDTH'], 
        general['HEIGHT'])
import pygame
class AI(object):
    sequences_ai = []
    last_vector =0
    wait_for= "static:mesure"
    walk = False
    max_height = 0
    max_height_verif = 0
    def __init__(self):
        self.game_font = pygame.font.Font(
            MEDIA_DIRECTORY +
            os.sep +
            "gui" +os.sep + general['THEME'] + os.sep +
            "font.otf", 40)
    def update_enemy (self) :
        """
        This function update the information about different enemys
        """

        self.enemy_number = []
        self.enemy_position = []
        self.enemy_distance = []
        self.enemy_distanceh = []

        for pl in [pl for pl in self.game.players if pl is not self.iam] :
            self.enemy_number.append (pl.num)
            self.enemy_position.append (pl.place)
            self.enemy_distance.append (self.iam.dist (pl))
            self.enemy_distanceh.append (pl.place[1]- self.iam.place[1])
    def update(self, game, iam):
        self.sequences_ai = []
        self.num = iam
        self.iam = game.players[iam]
        self.game = game
        self.update_enemy()
        self.choose_strategy()
    def choose_strategy(self):
        """if(self.iam.place[0] <self.enemy_position[0][0]):
            self.sequences_ai.append(("PL"+ str(self.num) + "_RIGHT",time.time()))
            self.iam.walking_vector[0] = config['WALKSPEED']
            self.iam.reversed = False
        if(self.iam.place[0] >self.enemy_position[0][0]):
            self.sequences_ai.append(("PL"+ str(self.num) + "_LEFT",time.time()))
            self.iam.walking_vector[0] = config['WALKSPEED']
            self.iam.reversed = True"""
        aix = self.iam.place[0]/8
        aiy = self.iam.place[1]/8
        enx = self.enemy_position[0][0]/8
        eny = self.enemy_position[0][1]/8
        for block in self.game.level.map:
            pygame.draw.line(self.game.screen, pygame.Color("green"), (block.left/8,block.top/8), (block.right/8,block.top/8))
            pygame.draw.line(self.game.screen, pygame.Color("green"), (block.left/8,block.bottom/8), (block.right/8,block.bottom/8))
        pygame.draw.line(self.game.screen, pygame.Color("red"), (aix,aiy), (enx,eny))
        pygame.draw.line(self.game.screen, pygame.Color("red"), (aix,aiy), (aix,aiy-self.max_height_verif/8))
        
        try:
            self.game.screen.blit(
                self.game_font.render(
                    "Height : " + str(general['HEIGHT']-self.iam.place[1]),
                    True,
                    pygame.color.Color("red")
                    ),
                (int(general['WIDTH']-200), 50)
            )
            self.game.screen.blit(
                self.game_font.render(
                    "Left : " + str(self.iam.place[0]),
                    True,
                    pygame.color.Color("red")
                    ),
                (int(general['WIDTH']-200), 100)
            )
        except:
            print "error"
            pass
        pygame.display.update()
        if self.enemy_position[0][0] < self.iam.place[0] :
            self.iam.reversed = True
        else :
            self.iam.reversed = False
        """if self.wait_for.split(":")[1] == "mesure2" :
            if self.iam.place[1] - self.start_event  > self.max_height :
                self.max_height = self.iam.place[1] - self.start_event
            elif self.max_height_verif is 0:
                print "max_height ="
                self.max_height_verif = self.max_height
                print self.max_height_verif
        anim = self.iam.entity_skin.current_animation
        #print anim
        if anim == self.wait_for.split(":")[0] :
            if self.wait_for.split(":")[1] == "mesure" :
                self.sequences_ai.append(("PL"+ str(self.num+1) + "_UP",time.time()))
                self.start_event = self.iam.place[1]
                self.wait_for = "static:mesure2"""
        if self.enemy_distance[0] < 100 :
            self.sequences_ai.append(("PL"+ str(self.num+1) + "_B",time.time()))
        elif self.enemy_distanceh[0] < 20 and self.enemy_distanceh[0] > -20:
            self.iam.walking_vector[0] = general['WALKSPEED']
            self.sequences_ai.append(("PL"+ str(self.num+1) + "_LEFT",time.time()))
            self.walk = True
        elif self.walk == True :
            self.iam.walking_vector[0] = 0
            if self.iam.entity_skin.current_animation == "walk":
                self.iam.entity_skin.change_animation(
                        "static",
                        self.game,
                        params={'entity': self.iam}
                        )
            
