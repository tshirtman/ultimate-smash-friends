#!/usr/bin/env python
import sys
import os
import time

sys.path.append('usf/')
from game import Game
from level import Level
from entity import Entity
from entity_skin import Entity_skin
from game import Game

USE_SCREEN = True
PRECISION = 50

def usage():
    print sys.argv[0], ': ', sys.argv[0], 'character level'
    print """launch a game with character in level, and place it at lots of
    positions, making it perform every movments to observe where it gets it,
    then s"""

def starting_positions():
    for movement in ('walk', 'jump', 'scnd_jumping', 'smash-up-jumping'):
        for reversed in (False, True):
            for pos_x in range(level.border[0], level.border[2], PRECISION):
                for pos_y in range(level.border[1], level.border[3], PRECISION):
                    yield (movement, reversed, pos_x, pos_y)

def main(player, level):
    screen = None
    if USE_SCREEN:
        import pygame
        pygame.display.init()
        screen = pygame.display.set_mode((800, 480))

    game = Game(screen)
    level = Level(level)
    player = Entity(0, game, entity_skinname='characters'+os.sep+player)
    quit = False

    for starting in starting_positions():
        player.reversed = starting[1]
        player.walking_vector = starting[0] = 'walk' and (WALKING_SPEED, 0) or (0,0)
        player.vector = (0,0)
        player.change_animation(starting[0])
        player.pos = starting[2]
        t = time.time()
        while time.time() < t+2:
            game.update()
            if USE_SCREEN:
                game.draw()
                pygame.display.update()

        pos = player.pos[0]/PRECISION,
              player.pos[1]/PRECISION

        print starting[2][0]/PRECISION,
              starting[2][1]/PRECISION,


if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()
    else:
        main(*sys.argv[1:3])

