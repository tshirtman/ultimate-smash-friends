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
#from config import config

from config import Config

config = Config.getInstance()

SIZE = (config.general['WIDTH'], 
        config.general['HEIGHT'])

from debug_utils import draw_rect
from enums import (TOP_RIGHT, UPPER_RIGHT, LOWER_RIGHT, BOTTOM_RIGHT,
                   BOTTOM_LEFT, LOWER_LEFT, UPPER_LEFT, TOP_LEFT)

class WrongEntityException(Exception):
    def __init__(self):
        logging.debug("The entity you wanted to unserialize is not this entity:\
Check number.")

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
    list_sin_cos = [
                    [
                     math.sin(i * math.pi / (nb_points/2) + math.pi / nb_points)
                     ,
                     math.cos(i * math.pi / (nb_points/2) + math.pi / nb_points)
                    ]
                    for
                    i in range(nb_points)
                   ]
    # this counter will allow us to correctly update entities.
    counter = 0

    def __init__( self, num, game,
            entity_skinname='characters'+os.sep+'stick-tiny', place=(550,1),
            lives=3, carried_by=None, vector=[0,0], reversed=False,
            server=False, number=None, visible=False, present=False
            ):
        if number is None:
            self.number = Entity.counter
            Entity.counter += 1
        else:
            self.number = number

        self.num = num
        self.upgraded = False
        self.lighten = False
        self.shield = { 'on': False, 'power': 1.0 }
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
            self.entity_skin = entity_skin.Entity_skin(entity_skinname,
            game == None or game.screen == None)
            try:
                self.entity_skin.change_animation(
                        'static',
                        game,
                        params={
                        'entity': self,
                        'world': game
                        }
                        )
            except:
                #logging.debug((self.name, game))
                raise
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


    def dist(self, entity):
        """
        Return the distance to another entity. None if the entity is None.

        """
        if entity is not None:
            return (
                (self.place[0] - entity.place[0]) ** 2 +
                (self.place[1] - entity.place[1]) ** 2
                ) ** .5
        else:
            return None

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

    def move(self,(x,y), _from=''):
        """
        move the entity relatively to his referencial (if he look left, moving
        positively on x mean going left).

        """
        if self.reversed: x = -x
        self.place = self.place[0] + x, int (self.place[1] + y)

    def collide_point(self, (x,y)):
        """
        Test the collision of the entity with the 1 pixel wide point at (x,y).

        """
        #FIXME test on hardshape at place would be better than size at place
        return self.rect.collidelist( [pygame.Rect(x,y,1,1), ] )

    def foot_collision_rect(self):
        return pygame.Rect(
                self.place[0]+self.entity_skin.animation.hardshape[0],
                self.place[1]+
                    self.entity_skin.animation.hardshape[1]+
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
            pass
        return vector

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
        entity_rect = self.foot_collision_rect()
        vector = [0,0]
        for part in level_moving_parts:
            if entity_rect.collidelist(part.collide_rects)!= -1:
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
        shape = self.entity_skin.animation.hardshape

        points = []
        #center = pygame.Rect(x+shape.)
        for i in range(Entity.nb_points):
            points.append((
                    Entity.list_sin_cos[i][0] * shape[2]
                    + shape[2]/2 + self.place[0] + x,
                            #don't divide width by 2
                    Entity.list_sin_cos[i][1] * shape[3] / 2
                    + shape[3]/2 + self.place[1] + y
                    ))

        return points

    def worldCollide(self, game):
        """
        This test collision of the entity with the map (game.level.map),
        the character.

        Method:
        Generation of a contact test circle (only 8 points actualy).
        Then we test points of this circle and modify entity vector based on
        points that gets collided, moving the entity in the right direction to
        get out of each collision.

        """

        # this test should optimise most of situations.
        if game.level.collide_rect(self.entity_skin.hardshape[:2],
                                   self.entity_skin.hardshape[2:]) != -1:
            points = self.update_points()
            self.onGround = False

            #first test if the entity hit fast enought that the middle points
            #touched
            if (game.level.collide_point(points[UPPER_LEFT])
                and game.level.collide_point(points[UPPER_RIGHT]))\
            or (game.level.collide_point(points[LOWER_LEFT])
                and game.level.collide_point(points[LOWER_RIGHT])):
                #self.vector[1] = math.fabs(self.vector[1])
                while game.level.collide_point(points[UPPER_LEFT])\
                or game.level.collide_point(points[UPPER_RIGHT]):
                    self.move(( 0, -(abs(self.vector[1])/self.vector[1])))
                    points = self.update_points()


            # if one of the two lowers points collide, the entity bounce up and
            # it's horizontal speed is lowered
            if (game.level.collide_point(points[TOP_LEFT])
            or game.level.collide_point(points[TOP_RIGHT])):
                self.vector[1] = -math.fabs(self.vector[1]/2)
                self.onGround = True
                self.vector[0] /= 2
                while (game.level.collide_point(points[TOP_LEFT])
                or game.level.collide_point(points[TOP_RIGHT])):
                    self.move(( 0, -1))
                    points = self.update_points()

            # test of points and consequences on vectors if one of the two
            # uppers points collide, the entity bounce down.
            if (game.level.collide_point(points[BOTTOM_RIGHT])
            or game.level.collide_point(points[BOTTOM_LEFT])):
                self.vector[1] = int(-self.vector[1] / 2)
                self.vector[0] /= 2
                while (game.level.collide_point(points[BOTTOM_RIGHT])
                or game.level.collide_point(points[BOTTOM_LEFT])):
                    self.move(( 0, 1))
                    points = self.update_points()

            # if one of the two left points collide and the entity is not
            # reversed or one of the two right points collide and the entity is
            # reversed and the player is pushed forward.
            if ( game.level.collide_point(points[UPPER_RIGHT])
                or game.level.collide_point(points[LOWER_RIGHT]) )\
                and self.reversed\
            or ( game.level.collide_point(points[LOWER_LEFT])\
                or game.level.collide_point(points[UPPER_LEFT]) )\
                and not self.reversed:
                self.vector[0] = math.fabs(self.vector[0])/2
                while ( game.level.collide_point(points[UPPER_RIGHT])\
                    or game.level.collide_point(points[LOWER_RIGHT]) )\
                    and self.reversed\
                or ( game.level.collide_point(points[LOWER_LEFT])\
                    or game.level.collide_point(points[UPPER_RIGHT]) )\
                    and not self.reversed:
                    self.move(( 1, 0))
                    points = self.update_points()

            # if one of the two left points collide and the entity is reversed or
            # one of the two right points collide and the entity is not reversed and
            # the player bounce back.

            if ((( game.level.collide_point(points[UPPER_RIGHT])
                or game.level.collide_point(points[LOWER_RIGHT]) )
                and not self.reversed)
            or (( game.level.collide_point(points[UPPER_LEFT])
                or game.level.collide_point(points[LOWER_LEFT]) )
                and self.reversed)):
                self.vector[0] = -math.fabs(self.vector[0])/2
                while ((( game.level.collide_point(points[UPPER_RIGHT])
                    or game.level.collide_point(points[LOWER_RIGHT]) )
                    and not self.reversed)
                or ( game.level.collide_point(points[UPPER_LEFT])
                    or game.level.collide_point(points[LOWER_LEFT]) )
                    and self.reversed):
                    self.move(( -1, 0), "wall, pushed back")
                    points = self.update_points()
        self.place = [int(self.place[0]), int(self.place[1])]

    def draw(self, coords, zoom, surface):
        """
        Draw the entity on the surface(i.e: the screen), applying coordinates
        offsets and zoom scaling as necessary, implementation depends on the
        definition of the global "SIZE", as a 2 elements list of in integers,
        containing respective height and width of the screen.

        coords is a tuple containing the current position of the camera, zoom is
        the current zoom of the camera.

        """
        if self.visible == True:
            real_coords = (
                    int(self.place[0]*zoom)*(SIZE[0]/800.0)+coords[0]
                    ,
                    int(self.place[1]*zoom)*(SIZE[1]/480.0)+coords[1]
                    )
            surface.blit(
                      loaders.image(
                          self.entity_skin.animation.image,
                          reversed=self.reversed,
                          lighten=self.lighten,
                          zoom=zoom
                          )[0],
                  real_coords
                  )

            if self.shield['on']:
                image = loaders.image(
                            os.path.sep.join(
                                (config.data_dir,'misc','shield.png')
                                ),
                                zoom=zoom*self.shield['power']*3
                            )

                shield_coords = (
                    int(self.place[0]*zoom)*(SIZE[0]/800.0)+coords[0]+\
                    .5*(self.rect[2]-image[1][2])
                    ,
                    int(self.place[1]*zoom)*(SIZE[1]/480.0)+coords[1]+\
                    .5*(self.rect[3]-image[1][3]) - .25*self.rect[3]
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

        self.vector = [
        self.vector[0] + environnement_vector[0],
        self.vector[1] + environnement_vector[1]
        ]

        self.place = [
        self.place[0] + floor_vector[0],
        self.place[1] + floor_vector[1]
        ]

        # Gravity
        if self.gravity :#and not self.onGround:
            self.vector[1] += float(config.general['GRAVITY']) * dt

        # Application of air friction.
        self.vector[0] -= config.general['AIR_FRICTION'] * self.vector[0] * dt
        self.vector[1] -= config.general['AIR_FRICTION'] * self.vector[1] * dt

        # apply the vector to entity.
        self.move ((self.vector[0] * dt, self.vector[1] * dt), 'vector')

        # Avoid collisions with the map
        self.worldCollide (game)

    def update(self, dt, t, surface, game, coords=(0,0), zoom=1):
        """
        Global function to update everything about entity, dt is the time
        ellapsed since the precedent frame, t is the current time, surface is
        the surface where the updated entity will be blitted, game is the
        reference of the current game. If the surface is None (for example in
        game server mode), then no drawing is performed.

        """
        self.update_floor_vector( game.level.moving_blocs)
        #TODO: fix vector movement to take account of framechange between two
        # displays

        # This function is dirty and slow. must be cleaned and optimized

        # all of this is nonsense if the entity is not present.
        if not self.present:
            return

        self.rect[2:] = self.entity_skin.animation.rect[2:]
        self.rect[:2] = self.place[0] - self.rect[2]/2, self.place[1]

        # Draw a point on the map at the entity position.
        if surface is not None:
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

        # Update animation of entity
        if self.entity_skin.update( t, self.reversed ) == 0:
            del(self)

        self.update_physics(dt, game)

