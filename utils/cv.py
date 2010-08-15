#!/usr/bin/env python
import pygame
from pygame import locals
from pygame.locals import (
    KEYDOWN,
    KEYUP,
    MOUSEMOTION,
    MOUSEBUTTONUP,
    MOUSEBUTTONDOWN,
    USEREVENT,
    K_ESCAPE,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_F5,
    )

import sys, os
import time

usf_root='../'

sys.path.append(os.path.join(usf_root,'usf'))

from entity_skin import Entity_skin
from loaders import image

def load(charname):
    return Entity_skin(os.path.join(
        usf_root, 'data', 'characters', charname
        ))

def main(charname):

    pygame.init()
    screen = pygame.display.set_mode((200,200))
    entity_skin = load(charname)
    anim = 1

    bottom_center_hardshape = (100, 150)
    while True:
        # get key events
        pygame.event.pump()
        for event in pygame.event.get(
            [ KEYDOWN, KEYUP ]
            ):
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_F5:
                    character = load(charname)
                elif event.key == K_UP:
                    anim +=1
                elif event.key == K_DOWN:
                    anim -=1

        animation = entity_skin.animations.keys()[
            anim % len(entity_skin.animations.keys())
        ]
        pygame.event.clear( [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN] )
        # update screen
        screen.fill(pygame.Color('green'))
        img = filter(
                    lambda f : f.time < (
                        (time.time()*1000.0) %
                        entity_skin.animations[animation].duration
                        ),
                    entity_skin.animations[animation].frames
                    )[-1]
        position = (
            bottom_center_hardshape[0] - img.hardshape[0] - img.hardshape[2]/2,
            bottom_center_hardshape[1] - img.hardshape[1] - img.hardshape[3]/2
        )
        screen.blit(image(img.image)[0], position)
        pygame.display.flip()

if __name__ == '__main__':
    main(sys.argv[1])
