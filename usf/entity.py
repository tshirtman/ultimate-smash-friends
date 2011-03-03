###############################################################################
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
###############################################################################

# python modules imports.
import pygame
import math
import os
import logging

# my modules imports.
import entity_skin
import loaders
import timed_event
from font import fonts

from config import Config

config = Config()

from debug_utils import draw_rect

class WrongEntityException(Exception):
    def __init__(self):
        logging.debug("The entity you wanted to unserialize is not this entity:"
                      "Check number.")

class Entity (object):
    """
    Provide an entity object, which will take care of lifes, movements,
    collisions of an Entity. Players and Items are Entities.

    """

    # Precalculation of some sin-cos list to speed up collision detection.
    # number of points cannot be changed currently due to not adaptative
    # collision method: FIXME someday.
    nb_points = 8
    ai = False
    ai_ = None
    list_sin_cos = [[
                math.sin(i * math.pi / (nb_points/2) + math.pi / nb_points),
                math.cos(i * math.pi / (nb_points/2) + math.pi / nb_points)]
            for i in range(nb_points)]

    # this counter will allow us to correctly update entities.
    counter = 0

    (TOP_RIGHT, UPPER_RIGHT, LOWER_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT, LOWER_LEFT,
     UPPER_LEFT, TOP_LEFT) = range(8)

    def __init__(self, num, game,
            entity_skinname='characters'+os.sep+'stick-tiny', place=(550,1),
            lives=3, carried_by=None, vector=[0,0], reversed=False,
            server=False, number=None, visible=False, present=False,
            upgraded=False, physic=True
            ):
        if number is None:
            self.number = Entity.counter
            Entity.counter += 1
        else:
            self.number = number

        self.physic = physic
        self.num = num
        self.upgraded = upgraded
        self.lighten = False
        self.shield = { 'on': False, 'power': 1.0, 'date': 0 }
        self.place = place
        self.carried_by = carried_by
        # the 'center' of the entity is at the bottom middle.
        # so this is the point that move the least beetwen two frames.
        self.vector = [vector[0], vector[1]]
        self.walking_vector = [0.0, 0.0]
        # the entity is reversed when looking at left.
        self.reversed = reversed
        self.percents = 0
        self.lives = lives
        self.gravity = True
        self.invincible = False
        self.present = present
        self.visible = visible
        self.onGround = False
        if entity_skinname is not None:
            self.name = entity_skinname.split(os.sep)[-1]
            self.entity_skin = entity_skin.Entity_skin(
                    entity_skinname,
                    not game or not game.screen
                    )
            self.armor = self.entity_skin.armor
            self.rect = pygame.Rect(0,0,0,0)
            self.rect[:2] = (
                    self.place[0] - self.rect[2]/2,
                    self.place[1] - self.rect[3]
                    )
            self.rect[2:] = self.entity_skin.animation.rect[2:]
            self.entity_skin.update(0, server=(game is None or game.screen is None))
            game.events.append(
                timed_event.ShieldUpdateEvent(
                    (None, None),
                    {'world': game, 'player': self}
                )
            )

    def __str__(self):
        return ','.join((
                    str(self.num),
                    self.upgraded and '1' or '0',
                    self.lighten and '1' or '0',
                    str(self.place),
                    str(self.vector),
                    str(self.walking_vector),
                    self.reversed and '1' or '0',
                    str(self.lives),
                    self.invincible and '1' or '0',
                    self.entity_skin.animation.image
                    ))

    def hit(self, point, reverse):
        """ enforce the effect of a collision with an aggressive point, the
        point is a list of x,y,dx,dy coords, and reverse is a flag indicating
        if the attacking entity is reversed (to apply projection vectors)
        """
        if self.shield['on'] :
            self.shield['power'] -= math.sqrt(
                                point[1][0]**2 + point[1][1]**2
                                )/config.general['SHIELD_SOLIDITY']
            self.shield['power'] = max(0, self.shield['power'])
            if (
            self.shield['date'] < time.time() - config.general['POWER_SHIELD_TIME']
            ):
                self.percents += math.sqrt( point[1][0]**2\
                                     +point[1][1]**2)/(30 * (100 -
                                     self.armor )) / 2

        else:
            if reverse != self.reversed:
                self.vector = [-point[1][0]*(1+self.percents),
                              point[1][1]*(1+self.percents)]
            else:
                self.vector = [ point[1][0]*(1+self.percents),
                              point[1][1]*(1+self.percents) ]
            self.percents += math.sqrt( point[1][0]**2\
                                     +point[1][1]**2)/(30 * (100 -
                                     self.armor ))*10

            self.entity_skin.change_animation(
                    "take",
                    self,
                    params={
                    'entity': self
                    }
                    )

    def dist(self, entity):
        """
        Return the distance to a Rect or to another entity.

        """
        if isinstance(entity, pygame.Rect):
            return (
                (self.place[0] - entity.centerx) ** 2 +
                (self.place[1] - entity.centery) ** 2
                ) ** .5

        elif isinstance(entity, Entity):
            return (
                (self.place[0] - entity.place[0]) ** 2 +
                (self.place[1] - entity.place[1]) ** 2
                ) ** .5
        else:
            raise ValueError("param 1 is neither a Rect or an Entity")

    def serialize(self):
        """
        Return an ascii representation of the object current state.

        """
        return (
                str(self.number),
                self.name,
                self in game.players and 'C' or 'I',
                str(self.place),
                self.entity_skin.animation.image.split(os.sep)[1:]
               )


# should Not be useful
#    def unserialize(self, string):
#        """
#        Set the entity to the state described by the string.
#
#        """
#        number, entity_type, name, place, animation, starttime = string.split(',')
#
#        if self.number != int(number):
#            raise WrongEntityException
#
#        self.entity_skinname = name
#        self.entity_type = entity_type
#        self.place = place[1:-1].split('*')
#        self.place = [int(self.place[0]), self.place[1]]
#        self.entity_skin.current_animation = animation
#        self.entity_skin.animation.__start__time = starttime

    def update_rect(self):
        """
        update entity rect using position and harshape place/size, necessary
        when entity moved or animation frame changed.

        """
        hardshape = self.entity_skin.hardshape
        self.rect[2:] = hardshape[2:]
        self.rect[:2] = [
            self.place[0] - hardshape[2]/2 - hardshape[0],
            self.place[1] - hardshape[1]
            ]

    def move(self,(x,y), _from=''):
        """
        move the entity relatively to his referencial (if he look left, moving
        positively on x mean going left).

        """
        if self.reversed:
            x = -x
        self.place = self.place[0] + x, int (self.place[1] + y)

        self.update_rect()

    def collide_point(self, (x,y)):
        """
        Test the collision of the entity with the 1 pixel wide point at (x,y).

        """
        return self.rect.collidelist([pygame.Rect(x,y,1,1), ])

    def foot_collision_rect(self):
        return pygame.Rect(
                self.rect[0]+self.entity_skin.animation.hardshape[0],
                self.rect[1]+
                    #self.entity_skin.animation.hardshape[1]+
                    self.entity_skin.animation.hardshape[3],
                self.entity_skin.animation.hardshape[2],
                15
                )

    def get_block_vector(self, level_vector_blocs):
        """
        If the entity is in a block associated with a vector, return this
        vector.

        """
        entity_rect = self.foot_collision_rect()
        vector = [0,0]

        for part in level_vector_blocs:
            if entity_rect.collidelist(part.collide_rects) != -1:
                if part.relative and not self.reversed:
                    vector = [
                    vector[0]+part.vector[0],
                    vector[1]+part.vector[1]
                    ]
                else:
                    vector = [
                    vector[0]-part.vector[0],
                    vector[1]+part.vector[1]
                    ]
        return vector

    def get_env_collision(self, blocks):
        rect = self.foot_collision_rect()

        for block in blocks:
            if rect.colliderect(block) == 1:
                if not self.in_water:
                    loaders.track(os.path.join(config.sys_data_dir, "sounds", "splash1.wav")).play()
                self.in_water = True
                return 5
        self.in_water = False
        return 1

    def update_floor_vector(self, level_moving_parts):
        """
        When the entity is on one (or more) moving (horizontaly) floors, the
        entity should move accordingly to the sum of this movements, This
        method return the sum of the horizontal movement of these floors for
        this frame, to add to the position of the character.  This is done by
        testing collision of a small rect under the feet of the entity and each
        of the moving parts of the level, passed in parameters, and asking the
        ones that collides, their horizontal movement.

        """
        rect = self.foot_collision_rect()
        vector = [0,0]
        for part in level_moving_parts:
            if rect.collidelist(part.collide_rects)!= -1:
                vector = [
                vector[0]+part.get_movement()[0],
                vector[1]+part.get_movement()[1]
                ]

        return vector

    def update_points(self, x = 0, y = 0):
        """
        creation of points, there are 8 points placed like this:
         7. .0   counted clockwise and starting from the upper right one
        6.   .1  (in fact it's the opposite but the screen is (0,0) at the
        5.   .2  top left, what actualy means right or left is not important
         4. .3   as long as you stay consistent, I hope I do :P).

         """

        points = []
        for i in range(Entity.nb_points):
            points.append((
                Entity.list_sin_cos[i][0] * self.entity_skin.hardshape[2] / 2 +
                self.entity_skin.hardshape[2]/2 +
                self.entity_skin.hardshape[0] +
                self.rect[0] + x,

                Entity.list_sin_cos[i][1] * self.rect[3] / 2 +
                self.rect[3]/2 +
                self.rect[1] + y
                ))

        return points

    def collide_top(self, game):
        """
        if one of the two lowers points collide, the entity bounce up and it's
        horizontal speed is lowered
        """
        points = self.update_points()
        return (game.level.collide_rect(points[self.TOP_LEFT])
        or game.level.collide_rect(points[self.TOP_RIGHT]))

    def collide_bottom(self, game):
        """
        test of points and consequences on vectors if one of the two uppers
        points collide, the entity bounce down.
        """
        points = self.update_points()
        return (game.level.collide_rect(points[self.BOTTOM_RIGHT])
        or game.level.collide_rect(points[self.BOTTOM_LEFT]))

    def collide_front(self, game):
        """
        if one of the two left points collide and the entity is not
        reversed or one of the two right points collide and the entity is
        reversed and the player is pushed forward.
        """

        points = self.update_points()
        return ( game.level.collide_rect(points[self.UPPER_RIGHT])
            or game.level.collide_rect(points[self.LOWER_RIGHT]) )\
            and self.reversed\
        or ( game.level.collide_rect(points[self.LOWER_LEFT])\
            or game.level.collide_rect(points[self.UPPER_LEFT]) )\
            and not self.reversed

    def collide_back(self, game):
        """
        if one of the two left points collide and the entity is reversed or one
        of the two right points collide and the entity is not reversed and the
        player bounce back.
        """

        points = self.update_points()
        return ((( game.level.collide_rect(points[self.UPPER_RIGHT])
            or game.level.collide_rect(points[self.LOWER_RIGHT]) )
            and not self.reversed)
        or (( game.level.collide_rect(points[self.UPPER_LEFT])
            or game.level.collide_rect(points[self.LOWER_LEFT]) )
            and self.reversed))

    def worldCollide(self, game):
        """
        This test collision of the entity with the map (game.level.map).

        Method:
        Generation of a contact test circle (only 8 points actualy).
        Then we test points of this circle and modify entity vector based on
        points that gets collided, moving the entity in the right direction to
        get out of each collision.

        """

        self.points = self.update_points()
        points = self.points
        if not self.physic:
            if game.level.collide_rect(points[self.TOP_LEFT]):
                self.place = [-10, -10]

        # this test should optimise most of situations.
        elif (game.level.collide_rect(self.rect[:2], self.rect[2:]) != -1 and
            self.physic):
            self.onGround = False

            if self.collide_top(game):
                self.vector[1] = -math.fabs(
                    self.vector[1] * config.general['BOUNCE']
                )
                self.onGround = True
                self.vector[0] /= 2
                while self.collide_top(game):
                    self.move(( 0, -1))

            if self.collide_bottom(game):
                if self.vector[1] < 0:
                    self.vector[1] = int(
                            -self.vector[1] * config.general['BOUNCE']
                            )
                self.vector[0] /= 2
                while self.collide_bottom(game):
                    self.move(( 0, 1))

            if self.collide_front(game):
                self.vector[0] = math.fabs(self.vector[0])/2
                while self.collide_front(game):
                    self.move(( 1, 0))

            if self.collide_back(game):
                self.vector[0] = -math.fabs(self.vector[0])/2
                while self.collide_back(game):
                    self.move(( -1, 0), "wall, pushed back")

        self.place = [
                int(self.place[0]),
                int(self.place[1])
                ]

    def draw_debug(self, coords, zoom, surface, debug_params):
        self.draw_debug_levelmap(coords, zoom, surface, debug_params)
        self.draw_debug_hardshape(coords, zoom, surface, debug_params)
        self.draw_debug_footrect(coords, zoom, surface, debug_params)
        self.draw_debug_current_animation(coords, zoom, surface, debug_params)

    def draw_debug_levelmap(self, coords, zoom, surface, debug_params):
        if debug_params["levelmap"] or loaders.get_gconfig().get("game", "minimap") == "y":
            draw_rect(
                    surface,
                    pygame.Rect(
                        self.place[0]/8,
                        self.place[1]/8,
                        2,
                        2
                        ),
                    pygame.Color('red')
                    )

    def draw_debug_hardshape(self, coords, zoom, surface, debug_params):
        if self.visible:
            if debug_params.get('hardshape', False):
                draw_rect(
                    surface,
                    pygame.Rect(
                    real_coords[0]+self.entity_skin.hardshape[0]*zoom,
                    real_coords[1]+self.entity_skin.hardshape[1]*zoom,
                    self.entity_skin.hardshape[2]*zoom,
                    self.entity_skin.hardshape[3]*zoom
                    )
                    ,
                pygame.Color(255, 0, 0, 127)
                )

                for i in self.update_points():
                    draw_rect(
                        surface,
                        pygame.Rect((
                            int(i[0])+coords[0]*zoom,
                            int(i[1])+coords[1]*zoom,
                            2,
                            2
                            )),
                        pygame.Color('blue')
                        )

    def draw_debug_footrect(self, coords, zoom, surface, debug_params):
        if self.visible:
            if debug_params.get('footrect', False):
                r = self.foot_collision_rect()
                draw_rect(
                    surface,
                    pygame.Rect(
                    coords[0]+r[0]*zoom,
                    coords[1]+r[1]*zoom,
                    r[2]*zoom,
                    r[3]*zoom
                    )
                    ,
                pygame.Color(255, 255, 0, 127)
                )

    def draw_debug_current_animation(self, coords, zoom, surface, debug_params):
        if self.visible:
            if debug_params.get('current_animation', False):
                surface.blit(
                    loaders.text(self.entity_skin.current_animation,
                    fonts['mono']['25']),
                    (
                     real_coords[0],
                     real_coords[1]+self.entity_skin.animation.rect[3]/2
                    ),
                    )

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

        self.draw_debug(coords, zoom, surface, debug_params)

        if self.visible:
            if not self.reversed:
                place = (
                    self.rect[0] - self.entity_skin.hardshape[0],
                    self.rect[1] - self.entity_skin.hardshape[1]
                    )
            else:
                place = (
                    self.rect[0],
                    self.rect[1] - self.entity_skin.hardshape[1]
                    )
            real_coords = (
                    int(place[0]*zoom)+coords[0] ,
                    int(place[1]*zoom)+coords[1]
                    )


            skin_image = loaders.image(
                          self.entity_skin.animation.image,
                          reversed=self.reversed,
                          lighten=self.lighten,
                          zoom=zoom
                          )
            surface.blit(
                  skin_image[0],
                  real_coords
                  )

            if self.shield['on']:
                image = loaders.image(
                            os.path.sep.join(
                                (config.sys_data_dir,'misc','shield.png')
                                ),
                                zoom=zoom*self.shield['power']*3
                            )

                shield_coords = (
                     coords[0] + int (
                     self.rect[0]
                     + self.entity_skin.shield_center[0]
                     - .5 * image[1][2]
                    ) * zoom
                    , coords[1] + int (
                     self.rect[1]
                     + self.entity_skin.shield_center[1]
                     - .5 * image[1][3]
                    ) * zoom
                    )
                surface.blit(image[0], shield_coords)



    def update_physics(self, dt, game):
        """
        This function apply current movemements and various environemental
        vectors to the entity, and calculate collisions.

        """
        # Move in walking direction.
        self.move(
                (
                 self.walking_vector[0] * dt,
                 self.walking_vector[1] * dt
                ),
                'walk'
                )

        # follow the floor if it's moving
        floor_vector = self.update_floor_vector(game.level.moving_blocs)

        # get environemental vector if we collide some vector-block
        environnement_vector = self.get_block_vector(
                game.level.vector_blocs
                )

        environnement_friction = self.get_env_collision(
                game.level.water_blocs
                )

        self.vector = [
        self.vector[0] + environnement_vector[0],
        self.vector[1] + environnement_vector[1]
        ]

        self.place = [
        self.place[0] + floor_vector[0],
        self.place[1] + floor_vector[1]
        ]

        # Gravity
        if self.gravity and self.physic and not self.onGround:
            self.vector[1] += float(config.general['GRAVITY']) * dt
        elif not self.physic:
            #FIXME : it is a bit hackish
            self.vector[1] += -0.00001

        # Application of air friction.
        F = config.general['AIR_FRICTION'] * environnement_friction

        if self.physic: #FIXME: and not a bullet
            self.vector[0] -= (F * self.vector[0] * dt)
            self.vector[1] -= (F * self.vector[1] * dt)

        # apply the vector to entity.
        self.move((self.vector[0] * dt, self.vector[1] * dt), 'vector')

        # Avoid collisions with the map
        self.worldCollide (game)

    def update(self, dt, t, game, coords=(0,0), zoom=1):
        """
        Global function to update everything about entity, dt is the time
        ellapsed since the precedent frame, t is the current time.
        """
        self.update_floor_vector( game.level.moving_blocs)
        # all of this is nonsense if the entity is not present.
        if not self.present:
            return

        # Update animation of entity
        if self.entity_skin.update( t, self.reversed, self.upgraded ) == 0:
            del(self)

        self.update_rect()
        self.update_physics(dt, game)

