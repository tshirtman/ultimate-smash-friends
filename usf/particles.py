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
This module provide a particle class and a ParticlesGenerator class, you
probably only need to manipulate the later. This allow you to generate textured
particles with variable initial coordinate, variable direction, and custome
initial speed and friction.
'''
from math import pi, sin, cos
from random import random
from usf.loaders import image

class Particle(object):
    '''
    A particle object is used as a part of a flow of particles to render
    effects as watter, smoke, fire or other dynamic elements.
    This Particle object is not very useful in itself, as it only store
    position, speed, direction and age of the particle, most of the management
    being done by the ParticlesGenerator parent object.
    '''
    def __init__(self, position, speed, direction):
        self.position = list(position)
        self.speed = speed
        self.direction = direction
        self.age = 0

    def update(self, deltatime, friction):
        self.age += deltatime
        self.position[0] += cos(self.direction) * self.speed
        self.position[1] += sin(self.direction) * self.speed
        self.speed = max(0, self.speed - friction * deltatime)

    def draw(self, surface, texture, pos, zoom, lifetime):
        real_coords = (int(self.position[0] * zoom) + pos[0],
                int(self.position[1] * zoom) + pos[1])

        surface.blit(
                image(
                    'data/'+texture,
                    zoom=zoom,
                    alpha=1-int(10*self.age/lifetime)/10.0)[0],
                    real_coords)


class ParticlesGenerator(object):
    ''' A simple particle generator implementation for levels, Particle
    generators are used to represent dynamic things like water, fire, rain,
    smoke, and so on.

    To use a ParticlesGenerator you should override the parametters in
    self.params with your own (in attribs), note that attribs is managed to
    extract information from xml files into it, so all data are represented in
    strings.

    position: the initial (center) position of the particles (in pixels)
    position_delta: allows to add a range of possible values around the center
    speed: initial speed of particles (in pixels/seconds)
    rate: rate of production of particles (in particles/seconds)
    direction: the main direction of particle emission, the value is in
    radian/pi (so 1 mean 1pi, which is 180 degrees, or half a circle, 0 mean
    left to right.)
    direction_delta: as for position_delta, allow to provide a range of
    randomness, same unit as direction
    lifetime: the lifetime of particles, note that the alpha of particles will
    decrease linearly to completly diseapear at end of life.
    friction: speed will decrease of this value each second, up to 0.
    '''

    def __init__(self, attribs):
        self.params = {
                'image': 'misc/hit.png',
                'position': (0, 0),
                'position_delta': (0, 0),
                'speed': 10,
                'rate': 30,
                'direction': 0,
                'direction_delta': 2 * pi,
                'lifetime': 2,
                'friction': 0.01,
                }

        if 'position' in attribs:
            attribs['position'] = [int(x) for x in
                    attribs['position'].split(',')]

        if 'position_delta' in attribs:
            attribs['position_delta'] = [int(x) for x in
                    attribs['position_delta'].split(',')]

        if 'speed' in attribs:
            attribs['speed'] = float(attribs['speed'])

        if 'rate' in attribs:
            attribs['rate'] = float(attribs['rate'])

        if 'direction_delta' in attribs:
            attribs['direction_delta'] = (
                    pi * float(attribs['direction_delta']))

        if 'direction' in attribs:
            attribs['direction'] = (
                    pi * float(attribs['direction']))

        if 'lifetime' in attribs:
            attribs['lifetime'] = float(attribs['lifetime'])

        if 'friction' in attribs:
            attribs['friction'] = float(attribs['friction'])

        self.params.update(attribs)
        self.time_accumulator = 0
        self.particles = set()
        self.frac = 1.0/self.params['rate']


    def update(self, deltatime):
        ''' update particles, delete too old ones, create new ones if
        time_accumulator allows it
        '''

        self.time_accumulator += deltatime
        to_remove = set()
        for p in self.particles:
            p.update(deltatime, self.params['friction'])
            if p.age > self.params['lifetime']:
                to_remove.add(p)

        self.particles.difference_update(to_remove)

        p = self.params
        while self.time_accumulator > self.frac:
            self.time_accumulator -= self.frac
            self.particles.add(Particle(
                [
                    p['position'][0] + p['position_delta'][0] * (random() - .5),
                    p['position'][1] + p['position_delta'][1] * (random() - .5)],
                p['speed'],
                p['direction'] + p['direction_delta'] * (random() - .5)))

    def draw(self, surface, pos, zoom):
        """ draw existing particles on surface, needs position and zoom of the
        camera.
        """
        for p in self.particles:
            p.draw(
                    surface,
                    self.params['image'],
                    pos,
                    zoom,
                    self.params['lifetime'])
