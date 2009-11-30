################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>
#
# This file is part of UltimateSmashFriends
#
# UltimateSmashFriends is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UltimateSmashFriends is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.
# ##############################################################################

# Standard modules imports
import random
import time

# Custom modules imports
from entity import Entity
from config import config

# FIXME : Those global vars have to be set in the AI class, don't they ?
# This var defines the max distance, when two players are able to hit themselves
# without moving
CRITICAL_DISTANCE = 25
# This var defines the distance within two players are considered as engaged
MIN_FIGHT_DISTANCE = 100

class AI (Entity):
    """
    Provide a computer controlled player
    Can be used like a normal entity (same methods)
    """

    def __init__ (self, num, game, entity_skinname = 'stick-tiny', skill = 'easy', place = (550, 1), lives = 3, carried_by = None, vector = (0, 0), reversed = False) :

        Entity.__init__ (self, num, game, entity_skinname, place, lives, carried_by, vector, reversed)

        self.enemy_position = []
        self.enemy_distance = []
        self.enemy_number = []

        self.current_target = -1

        self.target_x_offset = -1
        self.target_y_offset = -1
        self.target_x_relative_state = -1
        self.target_y_relative_state = -1

        self.in_jump = 0
        self.fight_engaged = 0
        self.need_change_target = 0

        # TODO : Change that system, it's deprecated. Change the vars names too. And maybe those descriptions in a xml file ?
        self.skill = skill # Utiliser un dico qui contiendra toutes les caracs ci-dessous
        if self.skill == 'simplest' :
            self.make_fall_priority = 0.00 # Ajouter un pourcentage d'action intelligentes realisees
        elif self.skill == 'bad' :
            self.make_fall_priority = 0.15
        elif self.skill == 'easy' :
            self.make_fall_priority = 0.30
        elif self.skill == 'normal' :
            self.make_fall_priority = 0.50
        elif self.skill == 'good' :
            self.make_fall_priority = 0.70
        elif self.skill =='smart' :
            self.make_fall_priority = 0.85
        elif self.skill == 'extreme' :
            self.make_fall_priority = 1.00
        #self.min_limit_make_fall = 1.00 - self.make_fall_priority

        """
        Very important list, which will contain a list of actions to do, in the very near future
        Structure : lifetime, remaining lifetime, action, options (player, etc... (in a list))
        If there is no options, must be told with -1
        If there is more than one action to do, they are listed in order, each one owning it own structure, like previously
        Possible action : w = wait, k = kick (option : kind of kick, direction), m = walk (option : direction)

        """
        self.strategy = []

        # If we need to ignore a player. If not use, TODO : remove
        self.ignored_pl = []
        
        # This is used to know how much time use AI every turn
        self.begin_computing_time = -1;
        self.average_computing_time = [0, 0]


    def update_enemy (self, game) :
        """
        This function update the information about different enemys
        """

        self.enemy_number = []
        self.enemy_position = []
        self.enemy_distance = []

        for pl in [pl for pl in game.players if pl is not self] :
            self.enemy_number.append (pl.num)
            self.enemy_position.append (pl.place)
            self.enemy_distance.append (self.dist (pl))

    def get_enemy_num_by_rank (self, rank) :
        """
        This function is used when you choose a enemy with it's rank in a list
        It will return you it's number
        """

        return self.enemy_number[rank]

    def get_enemy_rank_by_num (self, num) :
        """
        This function is used when you got the number of an enemy,
        and you need it's rank in lists
        It will return you that
        """

        for rank, number in enumerate (self.enemy_number) :
            if number == num :
                return rank

    def get_entity_by_num (self, num, game) :
        """
        This function simply returns an entity when you give it the entity
        number

        """

        for pl in game.players :
            if pl.num == num :
                return pl
        # If not found, throw an exception ?


    def reversed_or_not (self, side) :
        """
        This function defines if the AI player must be reversed or not,
        depending on the side it must go, This is used to avoid some side test,
        particularily in choose_strategy().

        """

        if side == 'left' :
            self.reversed = True
        elif side == 'right' :
            self.reversed = False


    def kick (self, game, type = 'kick') :
        """
        This function is called by the others one when they decided to try to
        hit a enemy. It could be used with any of the kick/combo types
        """

        # TODO: /!\ this should verify if the movement is allowed by sequences.cfg
        # TODO : Decide who verify : self.kick or the function which call it ? (because if we can't make
        # some kind of kick, the 'strategy' function must know it
        # TODO : decide if we verify sequences.cfg or just implement another system thanks to strategy
        self.entity_skin.change_animation (type, game, {'entity' : self})


    def jump (self, game, type = 'simple') :
        """
        This function provide the different jumps
        """

        # TODO: /!\ this should verify if the movement is allowed by
        # sequences.cfg
        if not self.in_jump and type == 'simple' :
            self.entity_skin.change_animation ('jump', game, {'entity' : self})
            self.in_jump = 1

        elif self.in_jump <= 1 and type == 'double' :
            self.entity_skin.change_animation ('scnd-jump', game, {'entity' : self})
            self.in_jump = 2



    # TODO : add 2 functions : one which allow to know if AI is doing something
    # (i mean, like jumping or kick), and a second one, which allow
    # to know if one particular kind of kick is possible
    
    
    def compute_computing_time () :
        """
        This function just compute an average of the CPU time spent by AI
        It uses a big aweful inline, but this one is useful in order 
        not to much time to loose
        """
        
        self.average_computing_time [0] = (self.average_computing_time [0] * self.average_computing_time [1]\
        + (time.clock () - self.begin_computing_time)) / (self.average_computing_time [1] + 1)
        self.average_computing_time [1] += 1 


    def update_current_target (self, game) : # TODO
        """
        This function updates the current target
        If the AI entity already got a target, it will probably keep the same, excepted if :
        - An other function require a change
        - An other target is really really near of the AI entity

        If no target is actually defined :
        In most case, it chooses the nearest target
        It could also choose another one, if random.random () decide something else :)

        And finally, if a enemy is really close, it will calculate some vars needed to choose a strategy
        """
        # TODO : when this function will work, it will need to be optimised (numerous call to get_*, etc...)

        # We only want alive players, that are not us.
        players_left = [
                        player\
                        for player\
                        in game.players\
                        if player.lives > 0\
                        and player is not self\
                       ]

        # Case of a one-vs-one fight
        if len(players_left) == 1 :
            self.current_target = players_left[0].num

        # TODO : write the else to choose the nearest enemy
        # The following code must be in this "else"
        
        """

            # FIXME : errors in following code, i think
            # If the closest enemy is really too close, or the current target too far,
            # change current target to closest enemy
            if closest[1] <= MIN_FIGHT_DISTANCE or closest[1] <= self.enemy_distance[self.get_enemy_rank_by_num (self.current_target.num)] :
                self.current_target = closest[0]
        """

        if  self.get_entity_by_num (self.current_target, game).dist (self) <= MIN_FIGHT_DISTANCE :
            self.fight_engaged = True
        elif self.get_entity_by_num (self.current_target, game).dist (self) >= MIN_FIGHT_DISTANCE :
            self.fight_engaged = False
        
        
        self.target_x_offset = self.place [0] - self.get_entity_by_num (self.current_target, game).place [0]
        self.target_y_offset = self.place [1] - self.get_entity_by_num (self.current_target, game).place [1]

        # If an enemy is critically close, set up new vars to choose a strategy
        if self.fight_engaged :
            if self.target_x_offset > CRITICAL_DISTANCE :
                self.target_x_relative_state = 'left'
            elif self.target_x_offset < - CRITICAL_DISTANCE :
                self.target_x_relative_state = 'right'
            else :
                self.target_x_relative_state = 'critical'
                self.walk ("stop")

            if self.target_y_offset > CRITICAL_DISTANCE :
                self.target_y_relative_state = 'up'
            elif self.target_y_offset < CRITICAL_DISTANCE :
                self.target_y_relative_state = 'down'
            else :
                self.target_y_relative_state = 'critical'

        else : # The AI's not engaged, so empty the 'strategy' vars
            self.target_x_relative_state = self.target_y_relative_state = ''

    def test_on_ground (game, lenght = 5) :
        return 'not implemented :P'


    def jump_update (self, game) :
        """
        This function updates the in_jump var, for example if the entity just
        landed or if it was walking and just fell It allows other AI function to
        know it the entity is in the air, or on the ground

        Possibles values for self.in_jump :
        0 - on ground
        1 - flying, but can still make a big jump (second jump)
        2 - flying and locked, it means the player already done the big jump

        """

        # FIXME : hack ! worldCollide () is too heavy for a single var !
        self.worldCollide (game)
        # Future form : self.test_on_ground (game, 5)

        if self.onGround and self.in_jump :
            self.in_jump = 0

        if not self.onGround and not self.in_jump :
            self.in_jump = 1


    def localize_fall_zone (self, player, map) :
        """
        This function is called for a enemy the AI need to know where he can
        fall

        """

        test_len = 50 # FIXME : This is a constant which must be put somewhere else

        # The two next rect are used to discover holes : the first one is higher
        # than the ground, and must never collide (else, it means that there is
        # an obstacle -- not a good way)
        # The second, is 'in' the ground, and must always collide : else, we
        # found an hole \o/
        test_rect_high = pygame.rect(
                                        player.place [0] - test_len,
                                        (
                                            player.list_sin_cos [3][1]\
                                            * player.entity_skin.animation.hardshape[3:4]\
                                            / 2\
                                            + player.entity_skin.animation.hardshape[3:4]\
                                            / 2
                                            + player.place[1]
                                        ),
                                        test_len,
                                        1
                                    )
        test_rect_low = pygame.rect(
                                        player.place [0] - test_len,
                                        (
                                            player.list_sin_cos [3][1]\
                                            * player.entity_skin.animation.hardshape[3:4]\
                                                / 2
                                            + player.entity_skin.animation.hardshape[3:4]\
                                                / 2\
                                            + player.place [1]
                                        ) - 1,
                                        test_len,
                                        1
                                   )

        distance = {'left' : -1, 'right' : -1}

        # Left side test
        while true :
            if test_rect_high.colliderect (map) or test_rect_low [0] < 0:
                break
            elif not test_rect_low.colliderect (map) :
                distance ['left'] = player.place [0] - (test_rect_low [0] + test_len)
                break
            else :
                test_rect_high [0] -= test_len
                test_rect_low [0] -= test_len

        # TODO : when a hole is detected, why not add a more accurate test ?

        test_rect_high [0] = test_rect_low [0] = player.place [0]

        # Right side test now
        while true :
            if test_rect_high.colliderect (map) or test_rect_low [0] > SIZE [0] :
                break
            elif not test_rect_low.colliderect (map) :
                distance ['right'] = test_rect_low [0] - player.place [0]
                brek
            else :
                test_rect_high [0] += test_len
                test_rect_low [0] += test_len

        # TODO : need something else now, or not ?

        if distance ['left'] == distance ['right'] == -1 :
            result = ('none', -1)
        elif distance ['left'] == -1 :
            result = ('right', distance ['right'])
        elif distance ['right'] == -1 :
            result = ('left', distance ['left'])
        else :
            if distance ['left'] < distance ['right'] :
                result = ('left', distance ['left'])
            elif distance ['right'] < distance ['left'] :
                result = ('right', distance ['right'])
            else :
                result = ('both', distance ['left'])

        return result


    def choose_strategy (self, game) : # TODO
        """
        This function defines self.strategy, and triggers action if necessairy
        It means that it chooses the way which will be used to attack a enemy,
        placed near of the AI entity It will choose :
        - A kick/combo
        - A time
        - A place with a direction
        """
        # TODO : delete this one or the other one
        self.update_current_target (game)
        
       
        if self.in_jump : # TODO : We need to modify self.strategy here            WTF ?
            # Target is upper and AI is going down

            # FIXME : regler prob des entity_skin.animation.vector
            if self.target_y_relative_state == 'up'\
            and self.entity_skin.animation.vector\
            and self.entity_skin.animation.vector[1] >= 0:
                if self.target_x_relative_state == 'critical':
                    self.kick (game, 'smash-up')
                    self.strategy = [0.1, 0.1, "w", -1] # TODO : the time (100) must be the duration of the kick

                elif self.in_jump == 2 :
                    # AI is not completely under the target, and can't jump, so
                    # move to the entity
                    self.walk (self.target_x_relative_state)

                    # Wait and update
                    self.strategy = [0.1, 0.1, "m", self.target_x_relative_state] # TODO : is 50 too short, too long ?

                else :
                    self.reversed_or_not (self.target_x_relative_state)
                    self.jump ('double')

                    # Same as above, and same TODO
                    self.strategy = [0.1, 0.1, "w", -1]

            # Target is lower and AI is going up
            if self.target_y_relative_state == 'down'\
            and self.entity_skin.animation.vector\
            and self.entity_skin.animation.vector[1] <= 0 :
                if self.target_x_relative_state == 'critical' :
                    self.kick (game, 'smash-down')

                    # We are hiting, AI must wait
                    self.strategy = [0.1, 0.1, "w", -1] # TODO : Modidy 50 with the duration of a kick


                else :
                    self.walk (self.target_x_relative_state)
            if self.target_y_relative_state == 'up'\
            and self.entity_skin.animation.vector\
            and self.entity_skin.animation.vector[1] <= 0\
            or self.target_y_relative_state == 'down'\
            and self.entity_skin.animation.vector\
            and self.entity_skin.animation.vector [1] >= 0 :


                self.strategy = [0.1, 0.1, "w", -1] # TODO : Duration ?

            if self.target_y_relative_state == 'critical' :
                if self.target_x_relative_state == 'critical' :
                    self.kick (game, 'smash-up')

                    self.strategy = [0.1, 0.1, "w", -1] # TODO : Duration of kick

                else :
                    self.reversed_or_not (self.target_x_relative_state)
                    self.kick (game, 'smash-straight')

                    self.strategy = [0.1, 0.1, "w", -1] # TODO : duration

        elif self.fight_engaged : 
            if self.target_y_relative_state == 'critical' :
                if self.target_x_relative_state is not 'critical' :
                    self.reversed_or_not (self.target_x_relative_state)
                    self.kick (game, 'kick-jumping')
                    
                    self.strategy = [0.1, 0.1, "w", -1]
                    
                    
            if self.target_y_relative_state == 'up' :
                if self.target_x_relative_state is 'critical' :
                    self.kick (game, 'smash-up')
                    
                    self.strategy = [0.1, 0.1, "w", -1]
        
        

    def use_strategy (self, game, dt) : # TODO
        """
        This function is the main AI function.
        It chooses what the AI entity will do the next frames
        It could choose to :
        - Find a long path to the target (which is far away)
        - Just move simply to the target, if it is near and on the same level
        - Choose a strategy (what to kick, when, in what direction) if a enemy
          is near enought
        """

        # TODO : delete this one or the other one
        self.update_current_target (game)
        
        # Okay, strategy already set, verify (really ?) and apply it
        if self.strategy :
            if self.strategy [2] == "m" :
                self.walk (self.strategy [3])

            elif self.strategy [2] == "k" :
                self.reversed_or_not (self.strategy [3][1])
                self.kick (game, self.strategy [3][0])
                

            # Now, let decrease remaing lifetime of this strategy, and delete it if decaprecated
            self.strategy [1] -= dt
            if self.strategy [1] <= 0 :
                # Delete only 4 element, in case there is more than one action to do
                del self.strategy [0 : 4]
                

        # No strategy, lets find one or simply move to the target
        else :
            if self.fight_engaged :
                self.choose_strategy (game)

            else :
                self.find_path (game)
                
        print self.strategy, self.fight_engaged, self.target_x_relative_state, self.target_y_relative_state


    def walk (self, side = 'left' ) :
        """
        This function, of course, allows the AI entity to walk and aims to
        reproduce the human player move

        """
        if side == 'left' :
            self.walking_vector [0] = WALKSPEED
            self.reversed = True

        elif side == 'right' :
            self.walking_vector [0] = WALKSPEED
            self.reversed = False

        elif side == 'stop' :
            self.walking_vector [0] = 0


    def find_path (self, game) : # TODO
        """
        This function is used when a target is far away from the AI entity
        It will find a way to the target

        """
        
        # All that is only debug, it's not a real pathfinder
        self.target_x_offset = self.place [0] - self.get_entity_by_num (self.current_target, game).place [0]
        
        if self.target_x_offset > 0 :
            self.walk ("left")
        else :
            self.walk ("right")

        if (self.target_x_offset ** 2)** 0.5 <= 5 :
            self.walk ('stop')


    def update (self, dt, t, surface, game, coords = (0 ,0), zoom = 1) : # TODO
        """
        This function is the function called each game loop It call all the
        functions needed to update the AI, and to allow it to
        find actions to do

        """
        
        begin_computing_time = time.clock ()

        # Get the position of other players (potential target), and the distance to them
        self.update_enemy (game)

        # Update the jump status
        self.jump_update (game)

        # Choose action to do
        self.use_strategy (game, dt)

        # Apply pending moves and gravity
        self.update_physics (dt, game)

        # Update animation of entity
        if self.entity_skin.update (t, self.reversed) == 0 :
            del (self)
            
        end_computing_time = time.clock ();
