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
    K_PLUS,
    K_MINUS,
    K_KP_PLUS,
    K_KP_MINUS,
    )

import sys, os
import time

usf_root='../'

try:
    import inotifyx
    fd = inotifyx.init()
except:
    print "no inotify, update manualy"
    inotifyx = False

sys.path.append(os.path.join(usf_root,'usf'))

from entity_skin import Entity_skin
from loaders import image

def main(charname):

    pygame.init()
    screen = pygame.display.set_mode((200,200))
    path = os.path.join(
        usf_root, 'data', 'characters', charname
        )
    entity_skin = Entity_skin(path)
    if inotifyx:
        wd = inotifyx.add_watch(fd, path, inotifyx.IN_MODIFY)
    anim = 0
    display_hardshape = True
    speed = 1.0
    font = pygame.font.Font(pygame.font.get_default_font(), 12)

    bottom_center_hardshape = (100, 150)
    while True:
        # get key events
        pygame.event.pump()
        if inotifyx and inotifyx.get_events(fd, 0):
            print 
            time.sleep(0.5)
            entity_skin = Entity_skin(path)
        for event in pygame.event.get(
            [ KEYDOWN, KEYUP ]
            ):
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_F5:
                    entity_skin = Entity_skin(path)
                    print "reloaded"
                elif event.key == K_UP:
                    anim +=1
                elif event.key == K_DOWN:
                    anim -=1
                elif event.key == K_SPACE:
                    display_hardshape = not display_hardshape
                elif event.key == K_PLUS or event.key == K_KP_PLUS:
                    speed *= 2
                elif event.key == K_MINUS or event.key == K_KP_MINUS:
                    speed /= 2

        animation = (
            sorted(
                filter(
                    lambda x: 'upgraded' not in x,
                    entity_skin.animations.keys()
                    )
                )+sorted(
                filter(
                    lambda x: 'upgraded' in x,
                    entity_skin.animations.keys()
                    )
                )
            )[
            anim % len(entity_skin.animations.keys())
        ]
        pygame.event.clear( [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN] )
        # update screen
        screen.fill(pygame.Color('green'))
        img = filter(
                    lambda f : f.time <= (
                        (time.time()*1000.0*speed) %
                        entity_skin.animations[animation].duration
                        ),
                    entity_skin.animations[animation].frames
                    )[-1]
        position = (
            bottom_center_hardshape[0] - img.hardshape[0] - img.hardshape[2]/2,
            bottom_center_hardshape[1] - img.hardshape[1] - img.hardshape[3]
        )
        if display_hardshape:
            screen.fill(
                pygame.Color('blue'),
                pygame.Rect((
                    position[0],
                    position[1],
                    image(img.image)[1][2],
                    image(img.image)[1][3]
                ))
                )
            screen.fill(
                pygame.Color('red'),
                pygame.Rect((
                    position[0]+img.hardshape[0],
                    position[1]+img.hardshape[1],
                    img.hardshape[2],
                    img.hardshape[3]
                ))
                )
        screen.blit(image(img.image)[0], position)
        screen.blit(
            font.render(
                animation +'   '+ str(img.time),
                True,
                pygame.Color('white')
                ),
            (10,10)
            )
        pygame.display.flip()
    inotifyx.rm_watch(wd)

if __name__ == '__main__':
    main(sys.argv[1])
