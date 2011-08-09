################################################################################
# copyright 2008-2011 Gabriel Pettier <gabriel.pettier@gmail.com>              #
#                                                                              #
# This file is part of UltimateSmashFriends                                    #
#                                                                              #
# UltimateSmashFriends is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation, either version 3 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# UltimateSmashFriends is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.#
################################################################################

'''
This module provide the Entity classe, that represent any physical object in
the game, character or item.

'''

# python modules imports.
import pygame
import math
import os

# my modules imports.
from usf.entity_skin import EntitySkin
import usf.loaders as loaders

from usf.font import fonts

from usf.config import Config

CONFIG = Config()

from usf.debug_utils import draw_rect

class Actor(object):
    """ An actor is the physical presence of something
    """
    (TOP_RIGHT, UPPER_RIGHT, LOWER_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT, LOWER_LEFT,
     UPPER_LEFT, TOP_LEFT) = range(8)

    def __init__(self, game, **kwargs):

        # the 'center' of the entity is at the bottom middle.
        # so this is the point that move the least beetwen two frames.
        self._game = game
        self._gravity = kwargs.get('gravity', True)
        self._on_ground = False
        self._physic = kwargs.get('physic', True)
        self._physics = kwargs.get('physics', True)
        self._place = kwargs.get('place', (550, 1))
        self._present = kwargs.get('present', False)
        self._reversed = kwargs.get('reverse', False)
        self._vector = list(kwargs.get('vector', (0, 0)))
        self._walking_vector = [0.0, 0.0]
        self.foot_rect = None
        self.in_water = False
        self.old_pos = []

    @property
    def place(self):
        """
        current position in level of the entity
        """

        return self._place

    def set_place(self, value):
        """
        move the entity to an arbitrary position
        """

        self._place = value

    @property
    def present(self):
        """
        return True if the entity is currently in game
        """
        return self._present

    def is_present(self):
        """
        callable form of the property
        """
        return self._present

    def set_present(self, value):
        """
        set the entity presence in game
        """
        assert value in (True, False)
        self._present = value

    @property
    def vector(self):
        """
        current dx/dt and dy/dt of the entity
        """
        return tuple(self._vector)

    def set_vector(self, value):
        """
        set the (dx/dt, dy/dt) of the entity
        """
        assert isinstance(value, list)
        self._vector = value

    @property
    def walking_vector(self):
        """
        current walking vector of the entity (this is different of the vector,
        as it's defined only by the fact the player uses direction keys)
        """
        return tuple(self._walking_vector)

    def set_walking_vector(self, value):
        """"
        set entity walking vector
        """
        if value[1] is None:
            self._walking_vector = (value[0], self._walking_vector[1])
        else:
            self._walking_vector = value

    @property
    def gravity(self):
        """
        True if the entity should react to gravity
        """
        return self._gravity

    def set_gravity(self, value):
        """
        Set if the player is bound to obey gravity
        """
        assert value in (True, False)
        self._gravity = value

    @property
    def on_ground(self):
        """
        True if the entity is currently in collision with the ground
        """
        return self._on_ground

    @property
    def physic(self):
        """
        True if the entity should have any physical reaction
        """
        return self._physic

    @property
    def reversed(self):
        """
        is the entity looking left
        """
        return self._reversed

    def set_reversed(self, value):
        """
        set the direction of the entity
        """
        assert value in (True, False)
        if value != self._reversed:
            self._vector[0] *= -1
            self._reversed = value

    @property
    def physics(self):
        """
        Set if the player has to manage collisions properly, if not, it will be
        destroyed when colliding anything
        """
        return self._physics

    def dist(self, entity):
        """
        Return the distance to a Rect or to another entity.

        """
        if isinstance(entity, pygame.Rect):
            return (
                (self.place[0] - entity.centerx) ** 2 +
                (self.place[1] - entity.centery) ** 2) ** .5

        elif isinstance(entity, Entity):
            return (
                (self.place[0] - entity.place[0]) ** 2 +
                (self.place[1] - entity.place[1]) ** 2) ** .5
        else:
            raise ValueError("param 1 is neither a Rect or an Entity")

    def _get_block_vector(self, level_vector_blocs):
        """
        If the entity is in a block associated with a vector, return this
        vector.

        """
        vector = [0, 0]

        for part in level_vector_blocs:
            if self.foot_rect.collidelist(part.collide_rects) != -1:
                if part.relative and not self.reversed:
                    vector = [
                    vector[0] + part.vector[0],
                    vector[1] + part.vector[1]]

                else:
                    vector = [
                    vector[0] - part.vector[0],
                    vector[1] + part.vector[1]]
        return vector

    def _get_env_collision(self, blocks):
        """
        DEPRECATED? react to collision with some environments as water
        """
        for block in blocks:
            if self.foot_rect.colliderect(block) == 1:
                if not self.in_water:
                    loaders.track(os.path.join(CONFIG.sys_data_dir,
                        "sounds",
                        "splash1.wav")).play()

                self.in_water = True
                return 5
        self.in_water = False
        return 1

    def _update_floor_vector(self, level_moving_parts):
        """
        When the entity is on one (or more) moving (horizontaly) floors, the
        entity should move accordingly to the sum of this movements, This
        method return the sum of the horizontal movement of these floors for
        this frame, to add to the position of the character.  This is done by
        testing collision of a small rect under the feet of the entity and each
        of the moving parts of the level, passed in parameters, and asking the
        ones that collides, their horizontal movement.

        """
        vector = [0, 0]
        for part in level_moving_parts:
            if self.foot_rect.collidelist(part.collide_rects)!= -1:
                vector = [
                        vector[0] + part.get_movement()[0],
                        vector[1] + part.get_movement()[1]]

        return vector

class Entity(Actor):
    """
    Provide an entity object, which will take care of lifes, movements,
    collisions of an Entity. Players and Items are Entities.

    This is a big class, and it uses a few counter intuitive concepts, first,
    its vectors are defined relatively, that mean moving "forward/backward"
    instead of moving "left/right", also the vector representing the walking
    movement of the entity is seperated from the main vector.

    """

    # Precalculation of some sin-cos list to speed up collision detection.
    # number of points cannot be changed currently due to not adaptative
    # collision method.
    nb_points = 8
    ai = False
    ai_ = None
    list_sin_cos = [[
                math.sin(i * math.pi / (nb_points/2) + math.pi / nb_points),
                math.cos(i * math.pi / (nb_points/2) + math.pi / nb_points)]
            for i in range(nb_points)]

    list_sin_cos_1 = map(lambda (x, y): (x+1, y+1), list_sin_cos)

    # this counter will allow us to correctly update entities.
    counter = 0

    def __init__(self, **kwargs):
        super(Entity, self).__init__(**kwargs)

        number = kwargs.get('num')

        if number:
            self._num = number

        else:
            self._num = Entity.counter
            Entity.counter += 1

        self._game = kwargs.get('game')
        self._upgraded = kwargs.get('upgraded', False)
        self._lighten = False
        self._shield = {'on': False, 'power': 1.0, 'date': 0}
        self._carried_by = kwargs.get('carried_by', None)
        # the entity is reversed when looking at left.
        self._percents = 0
        self._lives = kwargs.get('lives', 3)
        self._invincible = False
        self._visible = kwargs.get('visible', False)

        entity_skinname = kwargs.get(
                'entity_skinname',
                'characters' + os.sep + 'stick')

        if entity_skinname is not None:
            animation = kwargs.get('animation', 'static')
            self._name = entity_skinname.split(os.sep)[-1]
            self.entity_skin = EntitySkin(
                    entity_skinname,
                    not self._game or not self._game.screen,
                    animation=animation)

            self._armor = self.entity_skin.armor
            self._rect = pygame.Rect(0, 0, 0, 0)
            self._rect[:2] = (
                    self._place[0] - self._rect[2]/2,
                    self._place[1] - self._rect[3])

            self._rect[2:] = self.entity_skin.animation.rect[2:]
            self.entity_skin.update(0,
                    server=(self._game is None or self._game.screen is None))

            self._game.events.add_event(
                    'ShieldUpdateEvent',
                    (None, None),
                    {'world': self._game, 'player': self})

    @property
    def num(self):
        """
        return entity number
        """
        return self._num

    @property
    def hardshape(self):
        """
        return current hardshape from entity_skin
        """
        return self.entity_skin.hardshape

    @property
    def name(self):
        """
        name of the entity
        """
        return self._name

    @property
    def lives(self):
        """
        return current number of lives of the entity
        """
        return self._lives

    def set_lives(self, value):
        """
        change current number of lives of the entity
        """

        assert isinstance(value, int)
        self._lives = value

    @property
    def armor(self):
        """ return current armor state
        """
        return self._armor

    @property
    def percents(self):
        """
        return current percents
        """
        return self._percents

    def set_percents(self, value):
        """
        change percents value
        """
        self._percents = value

    def add_percents(self, value):
        """
        increment the current player percents
        """
        self._percents += value
        self._percents = max(self.percents, 0)

    @property
    def shield(self):
        """
        return current state of the shield
        """
        return self._shield

    @property
    def upgraded(self):
        """
        return True if the player is currently upgraded
        """
        return self._upgraded

    def set_upgraded(self, value):
        """
        Set the upgraded state of the player, True or False
        """
        assert value in (True, False)
        self._upgraded = value

    @property
    def visible(self):
        """
        set if the entity is currently visible on screen
        """
        return self._visible

    def set_visible(self, value):
        """
        Set the visibility statue of the entity
        """
        self._visible = value

    @property
    def invincible(self):
        """
        status of the entity vulnerability to hits
        """
        return self._invincible

    def set_invincible(self, value):
        """
        set the entity invulnerability status
        """
        assert value in (True, False)
        self._invincible = value

    @property
    def lighten(self):
        """
        True if the entity should be currently displayed lightened
        """
        return self._lighten

    def set_lighten(self, value):
        """
        Set lighten attribute of entity to value
        """
        assert value in (True, False)
        self._lighten = value

    def backup(self):
        """
        save important attributes of the state of the player, to a dict
        """
        assert isinstance(self._vector, list)
        d = {
            '_lives': self.lives,
            '_place': self.place[:],
            '_rect': pygame.Rect(self.rect[:]),
            '_vector': self._vector[:],
            '_walking_vector': self.walking_vector[:]}

        # would be easier with a dict comprehension, but not yet in 2.6
        for k in ('_reversed', '_percents', '_upgraded', '_present',
                '_visible'):
            d[k] = self.__dict__[k]
        return d

    def restore(self, backup):
        """
        restore the game to the state described in backup
        """
        self.__dict__.update(backup)
        assert isinstance(self._vector, list)

    @property
    def agressiv_points(self):
        """
        return agressiv points of the current frame
        """
        return self.entity_skin.animation.agressivpoints

    def test_hit(self, entity):
        """
        test entity aggressive points collisions with other entity
        """
        for point in self.agressiv_points:
            if entity.rect.colliderect(
                    self.rect[0] + point[0][0] - 3,
                    self.rect[1] + point[0][1] - 3,
                    6,
                    6):
                entity.hit(point, self.reversed)

    def hit(self, point, reverse):
        """
        enforce the effect of a collision with an aggressive point, the
        point is a list of x, y,dx, dy coords, and reverse is a flag indicating
        if the attacking entity is reversed (to apply projection vectors)
        """

        if self.shield['on']:
            self.shield['power'] -= (math.sqrt(
                point[1][0]**2 + point[1][1]**2)
                / CONFIG.general['SHIELD_SOLIDITY'])

            self.shield['power'] = max(0, self.shield['power'])
            self._percents += (math.sqrt(point[1][0] ** 2 + point[1][1]**2)
                    / (30 * (100 - self.armor)) / 2)

        else:
            direction = reverse != self.reversed and -1 or 1

            self.set_vector([direction * point[1][0] * (1 + self._percents),
                          point[1][1] * (1 + self._percents)])

            self._percents += math.sqrt((
                point[1][0] ** 2 +point[1][1] ** 2) / (30 * (100 - self.armor)))

            self.entity_skin.change_animation(
                    'take',
                    self._game,
                    params={'entity': self})

    def alive(self):
        """
        True if the player still have lives left
        """
        return self.lives > 0

    def _draw_debug(self, coords, zoom, surface, debug_params):
        """
        This method just call all specific debug draw methods
        """
        self._draw_debug_levelmap(surface, debug_params)
        self._draw_debug_hardshape(coords, zoom, surface, debug_params)
        self._draw_debug_footrect(coords, zoom, surface, debug_params)
        self._draw_debug_current_animation(coords, surface, debug_params)

    def _draw_debug_levelmap(self, surface, debug_params):
        """
        show the level map directly, usefull to debug
        """
        if debug_params["levelmap"]:
            draw_rect(
                    surface,
                    pygame.Rect(self.place[0]/8, self.place[1]/8, 2, 2),
                    pygame.Color('red'))

    def _draw_debug_hardshape(self, coords, zoom, surface, debug_params):
        """
        if hardshape debug is set, draw the hardshape of the player on the screen
        """
        if self.visible:
            if debug_params.get('hardshape', False):
                draw_rect(
                        surface,
                        pygame.Rect(
                            coords[0] + self.hardshape[0] * zoom,
                            coords[1] + self.hardshape[1] * zoom,
                            self.hardshape[2] * zoom,
                            self.hardshape[3] * zoom),
                        pygame.Color(255, 0, 0, 127))

                for n, i in enumerate(self.update_points()):
                    draw_rect(
                            surface,
                            pygame.Rect((
                                coords[0] + (i[0] - self.rect[0])* zoom,
                                coords[1] + (i[1] - self.rect[1])* zoom,
                                2, 2)),
                            n > 3 and pygame.Color('green') or
                            pygame.Color('blue'))

    def _draw_debug_footrect(self, coords, zoom, surface, debug_params):
        """
        if footrect debug is set, draw the footrect collision rect to the screen
        """
        if self.visible:
            if debug_params.get('footrect', False):
                r = self.foot_rect
                draw_rect(
                        surface,
                        pygame.Rect(
                            coords[0] + (r[0] - self.rect[0]) * zoom,
                            coords[1] + (r[1] - self.rect[1]) * zoom,
                            r[2] * zoom,
                            r[3] * zoom),
                        pygame.Color(255, 255, 0, 127))

    def _draw_debug_current_animation(self, coords, surface, debug_params):
        """
        if the current_animation debug is set, write the name of the current
            animation near of the character
        """
        if self.visible:
            if debug_params.get('current_animation', False):
                surface.blit(
                    loaders.text(self.entity_skin.current_animation,
                    fonts['mono']['25']),
                    (coords[0], coords[1] - self.entity_skin.animation.rect[3]))

    def draw(self, coords, zoom, surface, debug_params=dict()):
        """
        Draw the entity on the surface(i.e: the screen), applying coordinates
        offsets and zoom scaling as necessary, implementation depends on the
        definition of the global "SIZE", as a 2 elements list of in integers,
        containing respective height and width of the screen.

        coords is a tuple containing the current position of the camera, zoom is
        the current zoom of the camera.

        """
        # Draw a point on the map at the entity position.
        if not self.present:
            return

        if self.visible:
            if not self.reversed:
                place = (
                    self.rect[0] - self.hardshape[0],
                    self.rect[1] - self.hardshape[1])
            else:
                place = (
                    self.rect[0],
                    self.rect[1] - self.hardshape[1])

            real_coords = (
                    int(place[0]*zoom)+coords[0],
                    int(place[1]*zoom)+coords[1])

            self._draw_debug(real_coords, zoom, surface, debug_params)
            if self.entity_skin.animation.trails and self.old_pos:
                for i, (x, y) in enumerate(reversed(self.old_pos)):
                    img = self.entity_skin.animation.trails[
                            len(self.old_pos)-(i+1)]

                    surface.blit(
                          loaders.image(
                              img,
                              reversed=self.reversed,
                              zoom=zoom)[0],
                          (
                              int(x * zoom) + coords[0] - (
                                  not self.reversed and self.hardshape[0] or 0),
                              int(y * zoom) + coords[1] - self.hardshape[1]))

            skin_image = loaders.image(
                    self.entity_skin.animation.image,
                    reversed=self.reversed,
                    lighten=self.lighten,
                    zoom=zoom)

            surface.blit(
                    skin_image[0],
                    real_coords)

            if self.shield['on']:
                image = loaders.image(
                        os.path.sep.join(
                            (CONFIG.sys_data_dir, 'misc', 'shield.png')),
                        zoom=zoom*self.shield['power']*3)

                shield_coords = (
                        coords[0] + int(
                            self.rect[0]
                            + self.entity_skin.shield_center[0]
                            - .5 * image[1][2]) * zoom,
                        coords[1] + int(
                            self.rect[1]
                            + self.entity_skin.shield_center[1]
                            - .5 * image[1][3]) * zoom)
                surface.blit(image[0], shield_coords)

    def update(self, deltatime, gametime, game):
        """
        Global function to update everything about entity, deltatime is the
        time ellapsed since the precedent frame, gametime is the time since
        beginning of the game
        """

        self.old_pos = [self.rect[:2], ] + self.old_pos
        if (not self.entity_skin.animation.trails or len(self.old_pos) >
                len(self.entity_skin.animation.trails)):
            self.old_pos.pop()

        if self.present:
            self.entity_skin.update(gametime, self.reversed, self.upgraded)
            self._update_physics(deltatime, game)

    def _update_rect(self):
        """
        update entity rect using position and harshape place/size, necessary
        when entity moved or animation frame changed.

        """
        h = self.hardshape
        self._rect = [
                self._place[0] - h[2] / 2 - h[0],
                self._place[1] - h[1],
                h[2],
                h[3]]

    def _foot_collision_rect(self):
        """
        return current foot collusion rect
        """
        return pygame.Rect(
                self.rect[0] + self.hardshape[0],
                self.rect[1] + self.hardshape[3],
                self.hardshape[2],
                15)

    def point(self, n):
        """
        Return a collision point of the entity
        """
        h = self.hardshape
        r = self._rect
        # i think r[0] and r[1] should be used in this formules, but they break
        # it, so maybe i'm wrong
        return (int(Entity.list_sin_cos_1[n][0] * h[2] / 2 + r[0]),
                int(Entity.list_sin_cos_1[n][1] * h[3] / 2 + r[1]))

    def update_points(self, x = 0, y = 0):
        """
        creation of points, there are 8 points placed like this:
         7. .0   counted clockwise and starting from the upper right one
        6.   .1  (in fact it's the opposite but the screen is (0, 0) at the
        5.   .2  top left, what actualy means right or left is not important
         4. .3   as long as you stay consistent, I hope I do :P).

         """

        h = self.hardshape
        r = self._rect
        n = Entity.nb_points

        # reference version, non optimized and then should be easier to
        # understand
        #l = Entity.list_sin_cos
        #return [
        #        (
        #            int(l[i][0] * h[2] / 2 + h[2] / 2 + h[0] + r[0] + x),
        #            int(l[i][1] * h[3] / 2 + h[3] / 2 + h[1] + r[1] + y))
        #        for i in xrange(Entity.nb_points)]

        # optimised version
        h2_2 = h[2] / 2
        h3_2 = h[3] / 2
        hrx, hry = h[0] + r[0] + x, h[1] + r[1] + y
        l2 = Entity.list_sin_cos_1

        return [
                (
                    int(l2[i][0] * h2_2 + hrx),
                    int(l2[i][1] * h3_2 + hry))
                for i in xrange(n)]

    def collide_top(self, game):
        """
        if one of the two lowers points collide, the entity bounce up and it's
        horizontal speed is lowered
        """
        return (game.level.collide_rect(self.point(self.TOP_LEFT))
                or game.level.collide_rect(self.point(self.TOP_RIGHT)))

    def collide_bottom(self, game):
        """
        test of points and consequences on vectors if one of the two uppers
        points collide, the entity bounce down.
        """
        return (game.level.collide_rect(self.point(self.BOTTOM_RIGHT))
                or game.level.collide_rect(self.point(self.BOTTOM_LEFT)))

    def collide_front(self, game):
        """
        if one of the two left points collide and the entity is not
        reversed or one of the two right points collide and the entity is
        reversed and the player is pushed forward.
        """

        return (self.reversed and (
            game.level.collide_rect(self.point(self.UPPER_RIGHT)) or
            game.level.collide_rect(self.point(self.LOWER_RIGHT))) or
            not self.reversed and (
                game.level.collide_rect(self.point(self.LOWER_LEFT))
                or game.level.collide_rect(self.point(self.UPPER_LEFT))))

    def collide_back(self, game):
        """
        if one of the two left points collide and the entity is reversed or one
        of the two right points collide and the entity is not reversed and the
        player bounce back.
        """

        return (not self.reversed and (
            game.level.collide_rect(self.point(self.UPPER_RIGHT)) or
            game.level.collide_rect(self.point(self.LOWER_RIGHT))) or
            self.reversed and (
                game.level.collide_rect(self.point(self.UPPER_LEFT)) or
                game.level.collide_rect(self.point(self.LOWER_LEFT))))

    def _world_collide(self, game):
        """
        This test collision of the entity with the map (game.level.map).

        Method:
        Generation of a contact test circle (only 8 points actualy).
        Then we test points of this circle and modify entity vector based on
        points that gets collided, moving the entity in the right direction to
        get out of each collision.

        """

        if not self.physic:
            if game.level.collide_rect(self.point(self.TOP_LEFT)):
                self.set_lives(0)

        # this test should optimise most situations.
        elif game.level.collide_rect(self.rect[:2], self.rect[2:]) != -1:

            if self.collide_top(game):
                self._vector[1] = -math.fabs(
                    self.vector[1] * CONFIG.general['BOUNCE'])

                self._vector[0] /= 2
                while self.collide_top(game):
                    self.move((0, -1))

            elif self.collide_bottom(game):
                if self.vector[1] < 0:
                    self._vector[1] = int(
                            -self.vector[1] * CONFIG.general['BOUNCE'])

                self._vector[0] /= 2
                while self.collide_bottom(game):
                    self.move((0, 1))

            if self.collide_front(game):
                self._vector[0] = math.fabs(self.vector[0])/2
                while self.collide_front(game):
                    self.move((2, 0))

            elif self.collide_back(game):
                self._vector[0] = -math.fabs(self.vector[0])/2
                while self.collide_back(game):
                    self.move((-2, 0))

    def _update_physics(self, deltatime, game):
        """
        This function apply current movemements and various environemental
        vectors to the entity, and calculate collisions.

        """
        # Move in walking direction.
        self.move((
                    self.walking_vector[0] * deltatime,
                    self.walking_vector[1] * deltatime))

        self.foot_rect = self._foot_collision_rect()
        self._on_ground = game.level.collide_rect(
                self.foot_rect[:2],
                self.foot_rect[2:])

        # follow the floor if it's moving
        floor_vector = self._update_floor_vector(game.level.moving_blocs)

        # get environemental vector if we collide some vector-block
        environnement_vector = self._get_block_vector(
                game.level.vector_blocs)

        environnement_friction = self._get_env_collision(
                game.level.water_blocs)

        self._vector = [
                self.vector[0] + environnement_vector[0],
                self.vector[1] + environnement_vector[1]]

        self._place = [
                self.place[0] + floor_vector[0],
                self.place[1] + floor_vector[1]]

        # Gravity
        if self.gravity and self.physic and not self.on_ground:
            self._vector[1] += float(CONFIG.general['GRAVITY']) * deltatime

        elif not self.physic:
            #FIXME : it is a bit hackish
            self._vector[1] += -0.00001

        # Application of air friction.
        f = CONFIG.general['AIR_FRICTION'] * environnement_friction

        if self.physic: #FIXME: and not a bullet
            self._vector[0] -= (f * self.vector[0] * deltatime)
            self._vector[1] -= (f * self.vector[1] * deltatime)

        # apply the vector to entity.
        self.move((self.vector[0] * deltatime, self.vector[1] * deltatime))

        if not self.physics:
            return

        # Avoid collisions with the map
        self._world_collide(game)

    @property
    def rect(self):
        """
        return current player rect
        """
        return pygame.Rect(self._rect)

    def move(self, (x, y)):
        """
        move the entity relatively to his referencial (if he look left, moving
        positively on x mean going left).

        """
        if self._reversed:
            x = -x

        self.set_place((self._place[0]+ x, self._place[1] + y))

        self._update_rect()

