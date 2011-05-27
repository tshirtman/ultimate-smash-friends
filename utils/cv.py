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

import sys
import os
import time
import logging
import re

usf_root = '../'

animations = (
'static',          'static_upgraded',
'walk',            'walk_upgraded',
'jump',            'jump_upgraded',
'scnd-jump',       'scnd-jump_upgraded',
'pick',            'pick_upgraded',
'roll',            'roll_upgraded',
'take',            'take_upgraded',
'hit',             'hit_upgraded',
'kick',            'kick_upgraded',
'kick-jumping',    'kick-jumping_upgraded',
'smash-straight',  'smash-straight_upgraded',
'smash-up',        'smash-up-jumping_upgraded',
'smash-up-jumping','smash-up_upgraded',
'smash-down',      'smash-down_upgraded',
'special',         'special_upgraded',
'special2',        'special2_upgraded',
'specialhit',      'specialhit_upgraded',
)

try:
    import inotifyx
    fd = inotifyx.init()
except:
    logging.warning(
        "inotifyx module not present on your system, install it or use F5 "+
        "to update display manualy"
        )
    inotifyx = False

sys.path.append(usf_root)

from usf.entity_skin import Entity_skin
from usf.loaders import image
from usf.config import Config
config = Config()

class Placeholder(object):
    def __init__(self):
        self.hardshape=(0,0,40,60)
        self.image = 'no_animation.png'
        self.time = 0
        self.agressivpoints = []
        self.vectors = []

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

def load_entities(charnames):
    wds = list()
    skins = list()

    for charname in charnames:
        path = os.path.join(usf_root, 'data', 'characters', charname)
        path2 = os.path.join(usf_root, 'data', 'characters_unfinished', charname)

        if os.path.exists(path):
            if not os.path.exists(
                os.path.join(path,path.split(os.path.sep)[-1])+".xml"
                ):
                create_character_xml(path)
            skins.append(Entity_skin(path))

            if inotifyx:
                wds.append(inotifyx.add_watch(fd, path, inotifyx.IN_MODIFY))

        elif os.path.exists(path2):
            if not os.path.exists(
                os.path.join(path2,path2.split(os.path.sep)[-1])+".xml"
                ):
                create_character_xml(path2)
            skins.append(Entity_skin(path2))

            if inotifyx:
                wds.append(inotifyx.add_watch(fd, path2, inotifyx.IN_MODIFY))

        else:
            logging.error("no directory of this name in characters.")

    return skins, wds


def main(charnames):
    pygame.init()
    window_size = (200*len(charnames), 400)
    screen = pygame.display.set_mode(window_size)
    skins, wds = load_entities(charnames)

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
    last_time = time.time()
    while True:
        # frame limiter
        while time.time() < last_time + 0.05:
            time.sleep(0.05)

        last_time = time.time()

        # get key events
        pygame.event.pump()
        if inotifyx:
            for i, w in enumerate(wds):
                if inotifyx.get_events(fd, 0):
                    print "events"
                    for i in range(3):
                        try:
                            skins = load_entities(charnames)[0]
                            break
                        except:
                            time.sleep(0.5)
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
                (mouse_xy[0] - image_position[0]) % 200,
                mouse_xy[1] - image_position[1],
                2 * (pygame.mouse.get_pos()[0] - mouse_xy[0]),
                2 * (pygame.mouse.get_pos()[1] - mouse_xy[1])
                )

            print """
            <vector
            time="%s"
            vector="%s,%s"
            ></agressiv-point>
            """ % (
                img.time,
                2 * (pygame.mouse.get_pos()[0] - mouse_xy[0]),
                2 * (pygame.mouse.get_pos()[1] - mouse_xy[1])
                )
            mouse_click = False

        if not mouse_click and pygame.mouse.get_pressed()[0]:
            print "click pressed"
            mouse_xy = pygame.mouse.get_pos()
            mouse_click = True

        for event in pygame.event.get(
            [KEYDOWN, KEYUP]
            ):
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_F5:
                    entity_skins = load_entities(charnames)[0]
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

        pygame.event.clear( [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN] )
        screen.fill(pygame.Color('green'))
        for i, skin in enumerate(skins):
            animation = animations[anim % len(animations)]
            # update screen
            if animation in skin.animations:
                if not pause:
                    try:
                        img = filter(
                                    lambda f : f.time <= (
                                        (time.time()*1000.0*speed) %
                                        skin.animations[animation].duration
                                        ),
                                    skin.animations[animation].frames
                                    )[-1]
                    except ZeroDivisionError:
                        print "error: duration of 0 in", charnames[i], "in animation", animation
                        continue

                    bottom_center_hardshape[0] = (window_size[0]/(len(charnames)
                            * 2)) + (int(time.time() * config.general['WALKSPEED']) % 200 if
                                    "walk" in animation else 0)

                    #if "walk" in animation:
                        #bottom_center_hardshape[0] = int(
                            #time.time() * config.general['WALKSPEED']
                            #) % window_size[0]
                    #else:
                        #bottom_center_hardshape[0] = window_size[0]/(len(charnames) * 2)
                else:
                    img = skin.animations[animation].frames[frame % len(skin.animations[animation].frames)]
            else:
                img = Placeholder()

            # update the image_position of the up-left corner of image, so that the
            # bottom-middle of the hardhape never moves (as in the game)
            image_position = (
                (bottom_center_hardshape[0] - img.hardshape[0] -
                img.hardshape[2]/2 + 200 * i) % window_size[0],
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
                        image_position[0] + img.hardshape[0],
                        image_position[1] + img.hardshape[1],
                        img.hardshape[2],
                        img.hardshape[3]
                    ))
                    )

            screen.blit(image(img.image)[0], image_position)
            screen.blit(
                font.render( charnames[i], True, pygame.Color('red')),
                (10 + 200 * i,10))

            screen.blit(
                font.render(str(anim)+': '+animation, True, pygame.Color('red')),
                (10 + 200 * i,20))

            screen.blit(
                font.render(str(img.time), True, pygame.Color('red')),
                (10 + 200 * i,30))

            if shield:
                pygame.draw.circle(
                    screen,
                    pygame.Color('red'),
                    (
                        image_position[0] + img.hardshape[0] +
                        skin.shield_center[0] - 100 + 200 * i,
                        image_position[1] + img.hardshape[1] + skin.shield_center[1]
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
                        + skin.shield_center[0]
                        - .5 * image_shield[1][2]
                        ,
                        image_position[1]
                        + skin.shield_center[1]
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
    for wd in wds:
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
    if len(sys.argv) < 2 or sys.argv[1] == "help":
        usage()
        l = (
                os.listdir(os.path.join(usf_root, 'data', 'characters'))+
                os.listdir(os.path.join(usf_root, 'data',
                'characters_unfinished')))

        main(filter(lambda x: x != 'none', l))
    else:
        main(sys.argv[1:])
