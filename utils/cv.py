#!/usr/bin/env python
# coding:utf-8
import pygame
from pygame import locals
from pygame.locals import (
    KEYDOWN,
    KEYUP,
    K_DOWN,
    K_ESCAPE,
    K_F5,
    K_KP_MINUS,
    K_KP_PLUS,
    K_LEFT,
    K_MINUS,
    K_PLUS,
    K_RIGHT,
    K_SPACE,
    K_UP,
    K_p,
    K_s,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    USEREVENT,
    )

import sys, os
import time
import logging
import re

usf_root='../'

try:
    import inotifyx
    fd = inotifyx.init()
except:
    logging.warning(
        "inotifyx module not present on your system, install it or use F5 "+
        "to update display manualy"
        )
    inotifyx = False

sys.path.append(os.path.join(usf_root,'usf'))

from entity_skin import Entity_skin
from loaders import image
from config import Config
config = Config()

def create_character_xml(path):
    """ create a stub xml character """
    #TODO!
    movements={}
    f = open(os.path.join(path, path.split(os.path.sep)[-1])+".xml",'w')
    f.write('''<?xml version="1.0" encoding="UTF-8"?>
<character
name="'''+path.split(os.path.sep)[-1]+'''"
image="portrait.png"
hardshape="10 10 10 10"
creator=""
weight="1"
auto-reverse="True"
age=""
Description=""
shield_center="20 40"
>''')
    regex = re.compile('(.*?)-?([0-9]+).png')
    regex2 = re.compile('(.*?)-?([0-9]+)-upgraded.png')
    for file in os.listdir(path):
        res = regex.findall(file)
        if res:
            basename, number = res[0]
            if basename not in movements:
                movements[basename] = []
            movements[basename].append((int(number or 0), file))
        res = regex2.findall(file)
        if res:
            basename, number = res[0]
            basename += "-upgraded"
            if basename not in movements:
                movements[basename] = []
            movements[basename].append((int(number or 0), file))

    for movement in movements:
        m = movements[movement]
        m.sort(cmp=lambda x,y : cmp(x[0],y[0]))
        f.write('''
    <movement name="'''+movement+'''"
    duration="'''+str(len(m)*150+('jump' in movement and 30000))+'''"
    repeat="'''+(movement in ("walk", "static") and "-1" or "0")+'''"
    >''')
        if "jump" in movement:
            f.write('''
        <event
        period="350,0"
        action="PlayerStaticOnGround"
        ></event>''')

        t = 0
        for frame in m:
            i = image(os.path.join(path, frame[1]))
            f.write('''
        <frame
        time="'''+str(t)+'''"
        image="'''+str(frame[1])+'''"
        hardshape="'''+' '.join(map(str, i[1]))+'''"
        />''')
            t += 150

        f.write('''
    </movement>''')
    f.write('''
</character>
''')
    f.close()

def main(charname):
    pygame.init()
    window_size = (400, 400)
    screen = pygame.display.set_mode(window_size)
    path = os.path.join(
        usf_root, 'data', 'characters', charname
        )
    if os.path.exists(path):
        if not os.path.exists(
            os.path.join(path,path.split(os.path.sep)[-1])+".xml"
            ):
            create_character_xml(path)
    else:
        logging.error("no directory of this name in characters.")

    entity_skin = Entity_skin(path)
    if inotifyx:
        wd = inotifyx.add_watch(fd, path, inotifyx.IN_MODIFY)
    anim = 0
    display_hardshape = True
    speed = 1.0
    font = pygame.font.Font(pygame.font.get_default_font(), 12)
    pause = False
    shield = False
    frame = 0
    mouse_click = False
    mouse_xy = [0, 0]

    bottom_center_hardshape = [window_size[0]/2, window_size[1]*2/3]
    while True:
        # get key events
        pygame.event.pump()
        if inotifyx and inotifyx.get_events(fd, 0):
            time.sleep(0.5)
            for i in range(3):
                try:
                    entity_skin = Entity_skin(path)
                    break
                except:
                    pass
            else:
                print "doh!"

        if mouse_click and not pygame.mouse.get_pressed()[0]:
            print "click released"
            print """
            <agressiv-point
            coords="%s,%s"
            vector="%s,%s"
            ></agressiv-point>
            """ % (
                mouse_xy[0] - image_position[0],
                mouse_xy[1] - image_position[1],
                2 * (pygame.mouse.get_pos()[0] - mouse_xy[0],
                2 * (pygame.mouse.get_pos()[1] - mouse_xy[1])
                )
            mouse_click = False

        if not mouse_click and pygame.mouse.get_pressed()[0]:
            print "click pressed"
            mouse_xy = pygame.mouse.get_pos()
            mouse_click = True

        for event in pygame.event.get(
            [ KEYDOWN, KEYUP ]
            ):
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_F5:
                    entity_skin = Entity_skin(path)
                    print "reloaded"
                elif event.key == K_s:
                    shield = not shield
                elif event.key == K_p:
                    if pause:
                        print "normal mode"
                    else:
                        print "pause: frame mode, chose frame with ← and →"
                    pause = not pause
                elif event.key == K_RIGHT:
                    frame +=1
                elif event.key == K_LEFT:
                    frame -=1
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
        try:
            if not pause:
                img = filter(
                            lambda f : f.time <= (
                                (time.time()*1000.0*speed) %
                                entity_skin.animations[animation].duration
                                ),
                            entity_skin.animations[animation].frames
                            )[-1]
                if "walk" in animation:
                    bottom_center_hardshape[0] = int(
                        time.time() * config.general['WALKSPEED']
                        ) % window_size[0]
                else:
                    bottom_center_hardshape[0] = window_size[0]/2
            else:
                frame %= len(entity_skin.animations[animation].frames)
                img = entity_skin.animations[animation].frames[frame]
        except Exception, e:
            print e
        # update the image_position of the up-left corner of image, so that the
        # bottom-middle of the hardhape never moves (as in the game)
        image_position = (
            bottom_center_hardshape[0] - img.hardshape[0] - img.hardshape[2]/2,
            bottom_center_hardshape[1] - img.hardshape[1] - img.hardshape[3]
        )
        if display_hardshape:
            screen.fill(
                pygame.Color('grey'),
                pygame.Rect((
                    image_position[0],
                    image_position[1],
                    image(img.image)[1][2],
                    image(img.image)[1][3]
                ))
                )
            screen.fill(
                pygame.Color('blue'),
                pygame.Rect((
                    image_position[0]+img.hardshape[0],
                    image_position[1]+img.hardshape[1],
                    img.hardshape[2],
                    img.hardshape[3]
                ))
                )
        screen.blit(image(img.image)[0], image_position)
        screen.blit(
            font.render(
                str(anim)+': '+animation +'   '+ str(img.time),
                True,
                pygame.Color('red'),
                ),
            (10,10)
            )

        if shield:
            pygame.draw.circle(
                screen,
                pygame.Color('red'),
                (
                    image_position[0] + img.hardshape[0] + entity_skin.shield_center[0],
                    image_position[1] + img.hardshape[1] + entity_skin.shield_center[1]
                ),
                10
            )

            image_shield = image(
                    os.path.sep.join(('..','data','misc','shield.png')),
                    zoom=3
                    )

            screen.blit(
                image_shield[0],
                (
                        image_position[0]
                        + entity_skin.shield_center[0]
                        - .5 * image_shield[1][2]
                        ,
                        image_position[1]
                        + entity_skin.shield_center[1]
                        - .5 * image_shield[1][3]
                )
                )

        for i in img.agressivpoints:
            pygame.draw.ellipse(
                screen,
                pygame.Color('red'),
                pygame.Rect(
                    image_position[0]+i[0][0]-1, image_position[1]+i[0][1]-1, 2, 2
                    )
                )
            pygame.draw.line(
                screen,
                pygame.Color('red'),
                    (
                    image_position[0]+i[0][0],
                    image_position[1]+i[0][1],
                    ),
                    (
                    image_position[0]+i[0][0]+i[1][0]/2,
                    image_position[1]+i[0][1]+i[1][1]/2,
                    ),
                1
            )
        if mouse_click:
            pygame.draw.line(
                screen,
                pygame.color.Color("red"),
                mouse_xy,
                pygame.mouse.get_pos(),
                1
                )

        pygame.display.flip()
    inotifyx.rm_watch(wd)

def usage():
    print "usage: cv.py character_name"
    print """the character viewer has two mode of displaying: normal, and frame,

    In both modes:
        the ↑ and ↓ keys allow you to chose the played animation.
        the space key allow to switch boxes (image size and hardshape) displays
        the p key allow to switch mode (hint: pause)
        the s key allow to switch shield display (only used with static
        animation)

    In normal mode, the current animation is played over and over,
        You can change speed of the animation with + (faster) and - (slower)

    In frame mode the current frame is always displayed,
        You can use the ← and → keys to chose the current frame.

    I your system support inotify and your python installation contains the
    inotifyx module, the character will be automagicaly reloaded when modified,
    if not you can use ther F5 key to do so.
"""


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] == "help":
        usage()
    else:
        main(sys.argv[1])
