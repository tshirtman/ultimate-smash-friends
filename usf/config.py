################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
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

import os
from sys import platform
import logging

import pygame.locals

# xdg
if platform in ('linux2', 'bsd'):
    try:
        xdg_config_home = os.environ['XDG_CONFIG_HOME'] 
    except:
        logging.debug('error, XDG_CONFIG_HOME is not declared.')
        xdg_config_home = os.environ['HOME'] + '/.config'
else:
    xdg_config_home = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))


def open_conf(confname):
    if 'usf' not in os.listdir(os.path.join(xdg_config_home)):
        logging.debug('creating new config directory')
        os.mkdir(os.path.join(xdg_config_home,'usf'))

    if confname+'.cfg' not in os.listdir(os.path.join(xdg_config_home,'usf')):
        logging.debug('creating '+confname+' config')
        conf = open('.' + os.sep + 'default_'+confname+'.cfg')
        config_file = open(os.path.join(xdg_config_home,'usf',confname+'.cfg'),'w')
        config_file.write(conf.read())
        config_file.close()
        conf.close()

    return open(os.path.join(xdg_config_home,'usf',confname+'.cfg'))
        # looks like it's the first launch of the game, we need to create the
        # config file

def load_config():
    #TODO: add options from DEFAULT_CONFIG to config if missing
    config = {}
    config_file = open_conf('config')
    for line in config_file.readlines():
        if '=' in line:
            # allow various comment syntaxes
            line = line.split('#')[0].split(';')[0].split('//')[0]
            # yeah eval is evil, but I guess it exists for such situations
            config[line.split('=')[0].replace(' ','')] = eval(line.split('=')[1])
    return config

def load_sound_config():
    config = {}
    config_file = open_conf('sound')
    for line in config_file.readlines():
        if '=' in line:
            # allow various comment syntaxes
            line = line.split('#')[0].split(';')[0].split('//')[0]
            # yeah eval is evil, but I guess it exists for such situations
            config[line.split('=')[0].replace(' ','')] = eval(line.split('=')[1])
    return config

def load_key_config():
    keyboard_config = {}
    keys_file = open_conf('keys')
    for line in keys_file.readlines():
        #allow various comment syntaxes
        line = line.split('#')[0].split(';')[0].split('//')[0].split('\n')[0]
        if ':' in line:
            a,b=line.replace(' ','').split(":")
            keyboard_config[pygame.locals.__dict__[b]] = a
    return keyboard_config

#logging.debug("keyboard_config ",keyboard_config)

def save_conf():
    """
    save the general configuration options.
    """
    file=open(os.path.join(xdg_config_home,'usf','config.cfg'),'wb')
    for key in config.keys():
        conf= key +" = "
        #if value is a string, adding "
        if(type(config[key]) == type("")):
            conf += "\"" + str(config[key]) + "\""
        else:
            conf +=str(config[key])
        conf+="\n"
        file.write(conf)
    file.close()
    pass

str_conf = """
# this file contain keybindings of players and of the general game
# everything on a line after a # is a comment and is ignored
# you can start a comment with a ; too.

# The syntax of a binding is simple. the first part is the player concerned.
# to bind for the player one, start with "PL1" then a '_' and the action concerned.
# a complete list of actions will be inserted here later (#TODO).

# The second part of the line is the code of the key associated with the action.
# Theses are pygame names, and you can find a list at pygame website:
# http://www.pygame.org/docs/ref/key.html

# please also see online documentation of keybindings here:
# http://code.google.com/p/ultimate-smash-friends/wiki/KeysConfiguration
"""
# conf = ""
# config = {}
# for key in ('SIZE', 'FULLSCREEN', 'ZOOM_SHARPNESS', 'MAX_FPS', 'GRAVITY', 'JUMPHEIGHT', 'WLAKSPEED', 'AIR_FRICTION', 'INVICIBLE_TIME'):
#     conf += str(key)+" = "+str(config[key])+"\n"
#     file=open_conf('config')#(os.path.join(xdg_config_home,'usf','.cfg'),'w')
#     file.write(conf)
#     file.close()

reverse_keymap = {
        # FIXME: Maybe this is the source of bugs other plateforms! try to do this
        # dynamicaly!
        # reversed map of keys, based on pygame/sdl documentation
        1 : "KMOD_LSHIFT",
        2 : "KMOD_RSHIFT",
        3 : "KMOD_SHIFT",
        8 : "K_BACKSPACE",
        9 : "K_TAB",
        12 : "K_CLEAR",
        13 : "K_RETURN",
        19 : "K_PAUSE",
        27 : "K_ESCAPE",
        32 : "K_SPACE",
        33 : "K_EXCLAIM",
        34 : "K_QUOTEDBL",
        35 : "K_HASH",
        36 : "K_DOLLAR",
        38 : "K_AMPERSAND",
        39 : "K_QUOTE",
        40 : "K_LEFTPAREN",
        41 : "K_RIGHTPAREN",
        42 : "K_ASTERISK",
        43 : "K_PLUS",
        44 : "K_COMMA",
        45 : "K_MINUS",
        46 : "K_PERIOD",
        47 : "K_SLASH",
        48 : "K_0",
        49 : "K_1",
        50 : "K_2",
        51 : "K_3",
        52 : "K_4",
        53 : "K_5",
        54 : "K_6",
        55 : "K_7",
        56 : "K_8",
        57 : "K_9",
        58 : "K_COLON",
        59 : "K_SEMICOLON",
        60 : "K_LESS",
        61 : "K_EQUALS",
        62 : "K_GREATER",
        63 : "K_QUESTION",
        64 : "KMOD_LCTRL",
        64 : "K_AT",
        91 : "K_LEFTBRACKET",
        92 : "K_BACKSLASH",
        93 : "K_RIGHTBRACKET",
        94 : "K_CARET",
        95 : "K_UNDERSCORE",
        96 : "K_BACKQUOTE",
        97 : "K_a",
        98 : "K_b",
        99 : "K_c",
        100 : "K_d",
        101 : "K_e",
        102 : "K_f",
        103 : "K_g",
        104 : "K_h",
        105 : "K_i",
        106 : "K_j",
        107 : "K_k",
        108 : "K_l",
        109 : "K_m",
        110 : "K_n",
        111 : "K_o",
        112 : "K_p",
        113 : "K_q",
        114 : "K_r",
        115 : "K_s",
        116 : "K_t",
        117 : "K_u",
        118 : "K_v",
        119 : "K_w",
        120 : "K_x",
        121 : "K_y",
        122 : "K_z",
        127 : "K_DELETE",
        128 : "KMOD_RCTRL",
        192 : "KMOD_CTRL",
        256 : "KMOD_LALT",
        256 : "K_KP0",
        257 : "K_KP1",
        258 : "K_KP2",
        259 : "K_KP3",
        260 : "K_KP4",
        261 : "K_KP5",
        262 : "K_KP6",
        263 : "K_KP7",
        264 : "K_KP8",
        265 : "K_KP9",
        266 : "K_KP_PERIOD",
        267 : "K_KP_DIVIDE",
        268 : "K_KP_MULTIPLY",
        269 : "K_KP_MINUS",
        270 : "K_KP_PLUS",
        271 : "K_KP_ENTER",
        272 : "K_KP_EQUALS",
        273 : "K_UP",
        274 : "K_DOWN",
        275 : "K_RIGHT",
        276 : "K_LEFT",
        277 : "K_INSERT",
        278 : "K_HOME",
        279 : "K_END",
        280 : "K_PAGEUP",
        281 : "K_PAGEDOWN",
        282 : "K_F1",
        283 : "K_F2",
        284 : "K_F3",
        285 : "K_F4",
        286 : "K_F5",
        287 : "K_F6",
        288 : "K_F7",
        289 : "K_F8",
        290 : "K_F9",
        291 : "K_F10",
        292 : "K_F11",
        293 : "K_F12",
        294 : "K_F13",
        295 : "K_F14",
        296 : "K_F15",
        300 : "K_NUMLOCK",
        301 : "K_CAPSLOCK",
        302 : "K_SCROLLOCK",
        303 : "K_RSHIFT",
        304 : "K_LSHIFT",
        305 : "K_RCTRL",
        306 : "K_LCTRL",
        307 : "K_RALT",
        308 : "K_LALT",
        309 : "K_RMETA",
        310 : "K_LMETA",
        311 : "K_LSUPER",
        312 : "K_RSUPER",
        313 : "K_MODE",
        315 : "K_HELP",
        316 : "K_PRINT",
        317 : "K_SYSREQ",
        318 : "K_BREAK",
        319 : "K_MENU",
        320 : "K_POWER",
        321 : "K_EURO",
        323 : "K_LAST",
        512 : "KMOD_RALT",
        768 : "KMOD_ALT",
        1024 : "KMOD_LMETA",
        2048 : "KMOD_RMETA",
        3072 : "KMOD_META",
        4096 : "KMOD_NUM",
        8192 : "KMOD_CAPS",
        16384 : "KMOD_MODE",
        }

def save_sound_conf():
    """
    save the sound configuration.
    """
    conf = ""
    for key in ('SOUND_VOLUME', 'MUSIC_VOLUME', 'SOUND', 'MUSIC'):
        conf += str(key)+" = "+str(sound_config[key])+"\n"

    file=open(os.path.join(xdg_config_home,'usf','sound.cfg'),'w')
    file.write(conf)
    file.close()

def save_keys_conf(controls):
    """
    save the configuration of controls.
    """
    conf = ""
    for key in sorted(controls.keys()):
        #conf += "%s : %s\n" % ( self.keys[key], self.reverse_keymap[key])
        conf += str(controls[key])+" : "+str(reverse_keymap[key])+"\n"

    # we sort the keys configuration by player so the file is easier to read.
    file=open(os.path.join(xdg_config_home,'usf','keys.cfg'),'w')
    file.write(conf)
    file.close()

config = load_config()
keyboard_config = load_key_config()
sound_config= load_sound_config()

