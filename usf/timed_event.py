###############################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>
#
# This file is part of ultimate-smash-friends
#
# ultimate-smash-friends is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# ultimate-smash-friends is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# ultimate-smash-friends.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
'''
This module allow to create timed and condition based events, to create
complexe effects and behaviours in the game.

'''

import random
import math
import logging

from usf.config import Config

CONFIG = Config()
SIZE = (CONFIG.general['WIDTH'],
        CONFIG.general['HEIGHT'])


class TimedEvent (object):
    """
    An event allow to define a function to be executed later and/or during a
    certain period of time.
    """

    def __init__(self, manager, period, params=dict()):
        """
        Action must be a callable, it will be called every frames in the
        period.
        Condition must be a callable, when it return false the event will die.
        Period must be a period of time defined as a tupple of value, if the
        first value is None, then it will replaced by current time and if the
        second is None, the event will happen until dying.
        """

        self.params = params
        self.period = period[0], period[1] or None
        self.done = False
        self.event_manager = manager

    def update(self, deltatime, gametime):
        """
        This method make the event up to date, by executing the various
        functions of the event.
        """

        if self.period[1] is not None and gametime > self.period[1]:
            self.done = True

        elif gametime > self.period[0]:
            if not self.condition():
                self.done = True

            else:
                self.execute(deltatime)

    def backup(self):
        """
        This method return the state of the event in a dict, to restore latter
        """

        backup = {}
        for k in self.__dict__:
            backup[k] = self.__dict__[k]
        return backup

    def restore(self, backup):
        """
        This method restore the event in a previous state from a backup()
        """

        self.__dict__.update(backup)

    def execute(self, deltatime):
        """
        This method must be overriden, it will be called every frame by the
        event.
        """

        raise NotImplementedError

    def condition(self):
        """
        This method must be overriden, it will be called every frame by the
        event, to verify if the event must continue.
        """

        raise NotImplementedError

    def delete(self):
        """
        you can override this one if you want special behaviour
        """

        pass

    def del_(self):
        """
        please don't override this method if you want a special behaviour,
        override "delete" method instead.
        """

        #logging.info(str(self.__class__) + ' event deleted')
        self.delete()


class HealEvent(TimedEvent):
    """
    Event used to timely drop a player's percentage to zero.
    """

    def execute(self, deltatime):
        # at this rate it should take 5 seconds to go from 100% to 0%
        self.params['player'].add_percents(-deltatime*2)

    def condition(self):
        return self.params['player'].percents > 0


class ShieldUpdateEvent(TimedEvent):
    """
    This event, launched for one character, update the energy of it's shield at
    every loop, depending on if it's on or off.
    """

    def execute(self, deltatime):
        if self.params['player'].shield['on']:
            self.params['player'].shield['power'] -= deltatime/10
        elif self.params['player'].shield['power'] < 1:
            self.params['player'].shield['power'] += deltatime/10
        if self.params['player'].shield['power'] <= 0:
            self.params['player'].shield['on'] = False

    def condition(self):
        return True


class DelItemEvent(TimedEvent):
    """
    Event used to timely delete an item, because it was used, or because it got
    a timeout.
    """

    def execute(self, deltatime):
        pass

    def condition(self):
        return True

    def delete(self):
        if self.params is not None and 'entity' in self.params:
            target = self.params['entity']
        else:
            try:
                target = self.target
            except AttributeError:
                logging.error(
                'DelItemEvent no entity in params, and no self.target!!!')
        target.set_lives(0)


class BombExplode(TimedEvent):
    """
    This Event timely trigger the bomb explostion.
    """

    def execute(self, deltatime):
        self.params['entity'].set_gravity(False)
        self.params['entity'].entity_skin.change_animation(
                'explode',
                self.params['world'])

        self.done = True

    def condition(self):
        return True


class DropRandomItem(TimedEvent):
    """
    Add a random item in game.
    """

    def execute(self, deltatime):
        try:
            self.params['world'].add_item(
                    random.sample(['heal', 'bomb'], 1)[0],
                    place=(random.random()*SIZE[0], 50))

            self.done = True
        except:
            raise

    def condition(self):
        return True


class ItemShower(TimedEvent):
    """
    Add periodicaly an item into game.
    """

    def execute(self, deltatime):
        if 'freq' in self.params:
            freq = self.params['freq']
        else:
            freq = 2
        try:
            self.elapsed += deltatime
        except AttributeError:
            self.elapsed = deltatime

        if self.elapsed >= freq:
            try:
                self.params['world'].add_item(
                        random.sample(
                            [
                            'heal',
                            'invincibility',
                            'trunk',
                            'bomb',
                            ],
                            1)[0],
                        place=(random.random()*SIZE[0], 50))

                self.elapsed -= freq
            except:
                raise

    def condition(self):
        return True


class ThrowBomb(TimedEvent):
    """
    Launch a bomb in front of the player.
    """

    def execute(self, deltatime):
        self.done = True
        self.params['world'].add_item(
                'bomb',
                place=(self.params['entity'].rect[0:2]),
                reverse=self.params['entity'].reversed,
                vector=[1000, -1000])

    def condition(self):
        return True


class ThrowFireBall(TimedEvent):
    """
    Launch a fireball in front of the player.
    """

    def execute(self, deltatime):
        self.done = True
        entity = self.params['entity']
        place = list(entity.place[0:2])
        place[0] += -100 if entity.reversed else entity.rect[2]
        #place[1] -= entity.rect[3]/3
        self.params['world'].add_item(
                'fireball',
                place=place,
                reverse=entity.reversed,
                upgraded=entity.upgraded,
                bullet=True)

    def condition(self):
        return True


class Gost(TimedEvent):
    """
    Chasing 'AI' for a little chasing gost.
    """

    def execute(self, deltatime):
        self.target_player = None

        for pla in (
                player
                for player in self.params['world'].players
                if player is not self.params['entity']):

            if (self.target_player is None or
                    self.params['entity'].dist(pla) <
                    self.target_player.dist(self.params['entity'])):
                self.target_player = pla

        self.params['entity'].set_vector([
        (self.target_player.place[0] - self.params['entity'].place[0]) * 3,
        (self.target_player.place[1] - self.params['entity'].place[1]) * 3])

    def condition(self):
        return True


class ThrowMiniGost(TimedEvent):
    """
    Insert a little chasing gost in game.
    """

    def execute(self, deltatime):
        self.done = True
        self.params['world'].add_item(
                'mini_gost',
                place=(self.params['entity'].rect[0:2]),
                vector=[1000, 50])

    def condition(self):
        return True


class LaunchBullet(TimedEvent):
    """
    Launch a fireball in front of the player.
    """

    def execute(self, deltatime):
        self.done = True
        entity = self.params['entity']
        place = entity.place[0:2]
        place[0] += entity.reversed and -entity.rect[2] or entity.rect[2]
        place[1] += entity.rect[3]/2
        self.params['world'].add_item(
                'bullet',
                place=place,
                reverse=entity.reversed,
                upgraded=entity.upgraded,
                bullet=True)

    def condition(self):
        return True


class InvinciblePlayer(TimedEvent):
    """
    The target player is invincible and half invisible during this event.
    """

    def __init__(self, manager, period, params=dict()):
        # if we find another invincibility event on the same player we
        # just extend it's time to our limit and we are done.
        super(InvinciblePlayer, self).__init__(manager, period, params)
        invincibilities = list(
                self.event_manager.get_events(cls=InvinciblePlayer,
                params={'player': self.params['player']}))
        if len(invincibilities) != 0:
            invincibilities[0].period = self.period
            self.done = True
        else:
            self.params['player'].set_invincible(True)

    def execute(self, deltatime):
        self.params['player'].set_invincible(True)
        self.params['player'].set_lighten(not self.params['player'].lighten)

    def condition(self):
        return True

    def delete(self):
        self.params['player'].set_lighten(False)
        self.params['player'].set_invincible(False)


class VectorEvent(TimedEvent):
    """
    This event is used to assign time-based vector (accelerations) to a player.
    Used by animations.
    """

    def __init__(self, manager, period, params=dict()):
        #logging.debug("vector Event created "+ str(self.period))
        super(VectorEvent, self).__init__(manager, period, params)

    def execute(self, deltatime):
        pass

    def condition(self):
        """
        Return false so the addition is only performed once.
        """

        return (self.params['entity'].entity_skin.current_animation in
                (self.params['anim_name'],
                    self.params['anim_name']+'_upgraded'))

    def delete(self):
        """
        Add the vector to the player vector.
        """

        #logging.debug("vector Event applied")
        if self.condition():
            self.params['entity'].set_vector([
                self.params['vector'][0],
                -self.params['vector'][1]])


class UpgradePlayer(TimedEvent):
    """
    This event will upgrade the player to his upper state, that state ends when
    the player dies.
    """

    def __init__(self, manager, period, params=dict()):
        super(UpgradePlayer, self).__init__(manager, period, params)
        self.params['player'].set_upgraded(True)

    def execute(self, deltatime):
        pass

    def condition(self):
        return False


class DropPlayer(TimedEvent):
    """
    This event is called to drop a player in game.
    """

    def __init__(self, manager, period, params=dict()):
        super(DropPlayer, self).__init__(manager, period, params)
        #logging.debug("inserting player in game")
        self.params['entity'].set_vector([0, 0])
        self.params['entity'].set_walking_vector([0, 0])
        self.params['entity'].set_percents(0)
        self.params['entity'].set_upgraded(False)
        entry = random.choice(self.params['world'].level.entrypoints)
        self.params['entity'].set_place(entry)

    def execute(self, deltatime):
        pass

    def condition(self):
        return True

    def delete(self):
        self.params['entity'].set_visible(True)
        self.params['entity'].set_present(True)
        self.params['entity'].entity_skin.change_animation(
            'static',
            self.params['world'])

        self.event_manager.add_event(
                'InvinciblePlayer',
                (None, self.params['gametime'] + 3),
                params = {
                    'player':
                    self.params['entity'],
                    'world':
                    self.params['world']})


class PlayerOut(TimedEvent):
    """
    This event is called when a player is hitting the level border
    """

    def __init__(self, manager, period, params=dict()):
        super(PlayerOut, self).__init__(manager, period, params)
        self.params['entity'].set_lives(self.params['entity'].lives - 1)
        self.params['entity'].set_present(False)
        if self.params['entity'].lives > 0:
            self.event_manager.add_event(
                    'DropPlayer',
                    (None, self.params['gametime'] + 1),
                    params = self.params)

        self.coords = self.params['entity'].place


    def execute(self, deltatime):
        pass

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

        return not self.params['entity'].on_ground

    def delete(self):
        # don't apply if the animation was changed meanwhile
        if (self.params['entity'].entity_skin.current_animation in
                (self.params['anim_name'],
                    self.params['anim_name']+'_upgraded')):

            if tuple(self.params['entity'].walking_vector) != (0, 0):
                anim = 'walk'
            else:
                anim = 'static'

            self.params['entity'].entity_skin.change_animation(
                    anim+self.params['entity'].upgraded*'_upgraded',
                    self.params['world'],
                    params={'entity': self.params['entity']})


class Bounce(TimedEvent):
    """
    This event will make the entity bounce when touching the ground
    """

    def execute(self, deltatime):
        if self.params['entity'].on_ground:
            self.params['entity'].vector[1] *= -1

    def condition(self):
        return True

    def delete(self):
        pass


class BlobSpecial(TimedEvent):
    """ A boomerang like attack with the eye of blob
    """

    def __init__(self, manager, period, params=dict()):
        super(BlobSpecial, self).__init__(manager, period, params)
        self.entity = self.params['entity']

        self.entity_life = self.entity.percents

        try:
            self.target = min([
                (self.entity.dist(e), e) for e in self.params['world'].players
                if e is not self.entity and
                ((e.place[0] < self.entity.place[0]) ==\
                        self.entity.reversed)])[1]

        except ValueError:
            # no suitable target, abort
            self.done = True

        self.angle = 0

    def execute(self, deltatime):
        try:
            self.eye
        except AttributeError:
            self.eye = self.params['world'].add_item('blob-eye',
                    upgraded=self.entity.upgraded, physics=False,
                    reverse=self.entity.reversed)

        self.angle += deltatime * 2 * 3.14159 # enought precision here
        center = (
                (self.entity.place[0] + self.target.place[0]) / 2,
                (self.entity.place[1] + self.target.place[1]) / 2)

        dx_ = self.target.place[0] - self.entity.place[0]
        dy_ = self.target.place[1] - self.entity.place[1]

        xx_ = - math.cos(self.angle) * dx_ / 2 + center[0]
        yy_ = math.sin(self.angle) * dy_ / 2 + center[1] + dy_ * (
                self.angle / (2 * 3.14159) * (1 if self.angle < 3.14159 else
                    -1))

        self.eye.set_place((xx_, yy_))

    def condition(self):
        if (self.angle <= (2 * 3.14159)
                and self.entity_life == self.entity.percents):
            #and
            #   "special" in self.entity.entity_skin.current_animation
            return True

        else:
            return False

    def delete(self):
        try:
            self.eye.set_lives(0)
        except AttributeError:
            # happens if there was no suitable target and event was aborted
            pass


class XeonCharge(TimedEvent):
    """ a charge attack for Xeon
    """

    def __init__(self, manager, period, params=dict()):
        super(XeonCharge, self).__init__(manager, period, params)
        self.size = 0
        self.entity = self.params['entity']
        self.world = self.params['world']
        self.entity_life = self.entity.percents

    def execute(self, deltatime):
        self.size += deltatime

    def condition(self):
        if (self.size <= 1700 and
                self.entity_life == self.entity.percents and
                "special2" in self.entity.entity_skin.current_animation):
            return True

        else:
            return False

    def delete(self):
        if self.entity_life == self.entity.percents:
            size = min(int(self.size / (1.7 / 7)), 6)
            self.world.add_item(
                    "xeon-charge",
                    upgraded=self.entity.upgraded,
                    animation=str(size),
                    reverse=self.entity.reversed,
                    place=[self.entity.place[0] + (-100 if self.entity.reversed
                        else 100), self.entity.place[1]],
                    vector=[300, 0],
                    bullet=True)

# This list is used to cast an event by name. This is usefull since events are
# configured in players/items xml files.

EVENT_NAMES = {
    'BlobSpecial': BlobSpecial,
    'BombExplode': BombExplode,
    'Bounce': Bounce,
    'DelItemEvent': DelItemEvent,
    'DropPlayer': DropPlayer,
    'DropRandomItem': DropRandomItem,
    'Gost': Gost,
    'HealEvent': HealEvent,
    'InvinciblePlayer': InvinciblePlayer,
    'ItemShower': ItemShower,
    'LaunchBullet': LaunchBullet,
    'PlayerOut': PlayerOut,
    'PlayerStaticOnGround': PlayerStaticOnGround,
    'ShieldUpdateEvent': ShieldUpdateEvent,
    'ThrowBomb': ThrowBomb,
    'ThrowFireBall': ThrowFireBall,
    'ThrowMiniGost': ThrowMiniGost,
    'UpgradePlayer': UpgradePlayer,
    'VectorEvent': VectorEvent,
    'XeonCharge': XeonCharge,
}
