####################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>
#
# This file is part of ultimate-smash-friends
#
# ultimate-smash-friends is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ultimate-smash-friends is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ultimate-smash-friends.  If not, see <http://www.gnu.org/licenses/>.
##################################################################################

import exceptions
import os
import random
import logging

from new_config import Config

config = Config.getInstance()
general = config.general
SIZE = (general['WIDTH'], 
        general['HEIGHT'])

class TimedEvent (object):
    """
    An event allow to define a function to be executed later and/or during a
    certain period of time.
    """
    def initiate(self):
        """
        Overriding this fonction allow a better control on initialisation of
        the event

        """
        pass

    def __init__( self, period, params={} ):
        """
        Action must be a callable, it will be called every frames in the
        period.
        Condition must be a callable if false the event will die.
        Period must be a period of time defined as a tupple of value, if the
        first value is None, then it will replaced by current time and if the
        second is None, the event will happen until dying.

        """
        #logging.debug(str(self)+str(params))
        self.params = params
        self.period = period
        self.done = False
        self.initiate()

    def update(self, deltatime, gametime):
        """
        This method make the event up to date, by executing the various
        functions of the event.

        """
        # FIXME: events don't care for the game being paused!!!

        if self.period[0] is None or gametime > self.period[0]:
            if not self.condition() or self.done:
                return False
            if self.period[1] is None or gametime < self.period[1]:
                self.execute(deltatime)
                return True
            else:
                return False
        else:
            return True

    def execute(self, dt):
        """
        This method must be overriden, it will be called every frame by the
        event.

        """
        raise exceptions.NotImplementedError

    def condition(self):
        """
        This method must be overriden, it will be called every frame by the
        event, to verify if the event must continue.

        """
        raise exceptions.NotImplementedError

class HealEvent(TimedEvent):
    """
    Event used to timely drop a player's percentage to zero.

    """
    def execute(self, dt):
        self.params['player'].percents -= dt*2 # at this rate it should take 5
                                               # seconds to go from 100% to 0%
        self.params['player'].percents = max(self.params['player'].percents, 0)

    def condition(self):
        return self.params['player'].percents > 0

class ShieldUpdateEvent(TimedEvent):
    """
    This event, launched for one character, update the energy of it's shield at
    every loop, depending on if it's on or off.

    """
    def execute(self, dt):
        if self.params['player'].shield['on']:
            self.params['player'].shield['power'] -= dt/10
        elif self.params['player'].shield['power'] < 1:
            self.params['player'].shield['power'] += dt/10
        if self.params['player'].shield['power'] <= 0:
            self.params['player'].shield['on'] = False

    def condition(self):
        return True

class DelItemEvent(TimedEvent):
    """
    Event used to timely delete an item, because it was used, or because it got
    a timeout.

    """
    def execute(self, dt):
        pass

    def condition(self):
        return True

    def __del__(self):
        if self.params is not None and 'entity' in self.params :
            target = self.params['entity']
        else:
            target = self.target
        target.lives = 0

class BombExplode(TimedEvent):
    """
    This Event timely trigger the bomb explostion.

    """
    def execute(self, dt):
        self.params['entity'].gravity = False
        self.params['entity'].entity_skin.change_animation(
                'explode',
                self.params['world']
        )
        self.done = True

    def condition(self):
        return True

class DropRandomItem(TimedEvent):
    """
    Add a random item in game.

    """
    def execute(self, dt):
        try:
            self.params['world'].addItem(
                    random.sample(['heal','bomb'],1)[0],
                    place=(random.random()*SIZE[0],50)
            )
            self.done = True
        except:
            raise
            pass

    def condition(self):
        return True

class ItemShower(TimedEvent):
    """
    Add periodicaly an item into game.

    """
    def execute(self,dt):
        if 'freq' in self.params :
            freq=self.params['freq']
        else:
            freq=2
        try:
            self.elapsed += dt
        except:
            self.elapsed = dt

        if self.elapsed >= freq:
            try:
                self.params['world'].addItem(
                        random.sample(
                            [
                            'heal',
                            'invincibility',
                            'trunk',
                            'bomb',
                            ],
                            1
                            )[0],
                        place=(random.random()*SIZE[0],50)
                        )
                self.elapsed -= freq
            except:
                raise
                pass

    def condition(self):
        return True

class ThrowBomb(TimedEvent):
    """
    Launch a bomb in front of the player.

    """
    def execute(self, deltatime):
        self.done = True
        self.params['world'].addItem(
                'bomb',
                place=(self.params['entity'].rect[0:2]),
                reversed=self.params['entity'].reversed,
                vector=(1000, -1000)
                )

    def condition(self):
        return True

class ThrowFireBall(TimedEvent):
    """
    Launch a fireball (bouncing) in front of the player.

    """
    def execute(self, deltatime):
        self.done = True
        self.params['world'].addItem(
                'fireball',
                place=(self.params['entity'].rect[0:2]),
                reversed=self.params['entity'].reversed,
                vector=(100, -1000)
                )

    def condition(self):
        return True

class Gost(TimedEvent):
    """
    Chasing 'AI' for a little chasing gost.

    """
    def execute(self, deltatime):
        self.target_player = None

        for p in (
                player
                for player in self.params['world'].players
                if player is not self.params['entity']
                ):
            if self.target_player is None or None <\
            self.params['entity'].dist(p) <\
            self.target_player.dist( self.params['entity']):
                self.target_player = p

        self.params['entity'].vector = [
        ( self.target_player.place[0] - self.params['entity'].place[0]) * 3,
        ( self.target_player.place[1] - self.params['entity'].place[1]) * 3
        ]
    def condition(self):
        return True

class ThrowMiniGost(TimedEvent):
    """
    Insert a little chasing gost in game.

    """
    def execute(self, deltatime):
        self.done = True
        self.params['world'].addItem(
                                        'mini_gost',
                                        place=(self.params['entity'].rect[0:2]),
                                        vector=(1000, 50)
                                    )

    def condition(self):
        return True

class InvinciblePlayer(TimedEvent):
    """
    The target player is invincible and half invisible during this event.

    """
    def myfilter(self, element):
        return element.__class__ is InvinciblePlayer and\
           element.params['player'] is self.params['player']


    def initiate(self):
        # if we find another invincibility event on the same player we
        # just extend it's time to our limit and we are done.
        invisibilities = filter(self.myfilter, self.params['world'].events)
        if len(invisibilities) is not 0:
            invisibilities[0].period = self.period
            self.done = True
        else:
            self.params['player'].invincible = True

    def execute(self, deltatime):
        self.params['player'].invincible = True
        self.params['player'].lighten = not self.params['player'].lighten

    def condition(self):
        return True

    def __del__(self):
        self.params['player'].lighten = False
        self.params['player'].invincible = False

class VectorEvent(TimedEvent):
    """
    This event is used to assign time-based vector (accelerations) to a player.
    Used by animations.

    """
    def initiate(self):
        #logging.debug("vector Event created "+ str(self.period))
        pass

    def execute(self, deltatime):
        pass

    def condition(self):
        """
        Return false so the addition is only performed once.

        """
        return self.params['anim_name'] ==\
            self.params['entity'].entity_skin.current_animation

    def __del__(self):
        """
        Add the vector to the player vector.

        """
        if self.params['entity'].entity_skin.current_animation:
            self.params['entity'].vector[0] = self.params['vector'][0]
            self.params['entity'].vector[1] = -self.params['vector'][1]
        #logging.debug("vector Event applied")

class UpgradePlayer(TimedEvent):
    """
    This event will upgrade the player to his upper state, that state ends when
    the player dies.

    """
    def initiate(self):
        self.params['player'].upgraded = True

    def execute(self, deltatime):
        pass

    def condition(self):
        return False

class DropPlayer(TimedEvent):
    """
    This event is called to drop a player in game.

    """
    def initiate(self):
        #logging.debug("inserting player in game")
        self.params['entity'].vector = [0, 0]
        self.params['entity'].walking_vector = [0, 0]
        self.params['entity'].percents = 0
        self.params['entity'].upgraded = False

        if len(self.params['world'].level.entrypoints) != 0:
            self.params['entity'].place = random.sample(
                self.params['world'].level.entrypoints, 1
            )[0]

        else:
            #logging.debug('no entry point defined for this level')
            self.params['entity'].place = (
                self.params['world'].level.rect[2]/2, 50
            )

    def execute(self, deltatime):
        pass

    def condition(self):
        return True

    def __del__(self):
        self.params['entity'].visible = True
        self.params['entity'].present = True
        self.params['world'].events.append(
                InvinciblePlayer(
                    (None,
                     self.params['gametime'] + 3),
                    params = {
                    'player':
                    self.params['entity'],
                    'world':
                    self.params['world']
                    }
                )
        )

class PlayerOut(TimedEvent):
    """
    This event is called when a player is hitting the level border

    """
    def execute(self, deltatime):
        self.params['world'].addItem(
                'star',
                place=(self.xy),
                vector=(
                    self.target.level.rect[0]/2-self.xy[0],
                    self.target.level.rect[1]/2-self.xy[1]
                    )
                )

    def initiate(self):
        self.params['entity'].lives -= 1
        self.params['entity'].present = False
        if self.params['entity'].lives > 0:
            self.params['world'].events.append(
                    DropPlayer(
                        (
                         None,
                         self.params['gametime'] + 1
                        ),
                        params = self.params
                        )
                    )
        self.xy = self.params['entity'].place

    def condition(self):
        return True

class PlayerStaticOnGround(TimedEvent):
    """
    This event will set the player on static animation when he tuch the ground

    """
    def execute(self, deltatime):
        pass

    def condition(self):
        """
        Return false if the player is on ground so the event effect occure.

        """
        return not self.params['entity'].onGround

    def __del__(self):
        self.params['entity'].entity_skin.change_animation(
                'static',
                self.params['world']
                )

class Bounce(TimedEvent):
    """
    This event will make the entity bounce when touching the ground

    """
    def execute(self, deltatime):
        if self.params['entity'].onGround:
            self.params['entity'].vector[1] *= -1

    def condition(self):
        return True

    def __del__(self):
        pass

# This list is used to cast an event by name. This is usefull since events are
# configured in players/items xml files.

event_names = {
    'HealEvent' : HealEvent,
    'BombExplode' : BombExplode,
    'DelItemEvent' : DelItemEvent,
    'DropRandomItem' : DropRandomItem,
    'ItemShower': ItemShower,
    'InvinciblePlayer' : InvinciblePlayer,
    'ThrowBomb' : ThrowBomb,
    'ThrowMiniGost' : ThrowMiniGost,
    'Gost' : Gost,
    'PlayerStaticOnGround' : PlayerStaticOnGround,
    'UpgradePlayer' : UpgradePlayer,
    'ThrowFireBall' : ThrowFireBall,
    'Bounce' : Bounce,
}