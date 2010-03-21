###############################################################################
# copyright 2010 Edwin Marshall (aspidites) <aspidties@gmx.com>               #
#                                                                             #
# This file is part of UltimateSmashFriends                                   #
#                                                                             #
# UltimateSmashFriends is free software: you can redistribute it and/or       #
# modify it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# UltimateSmashFriends is distributed in the hope that it will be useful,     #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with UltimateSmashFriends.                                            # 
# If not, see <http://www.gnu.org/licenses/>.                                 #
###############################################################################

""" It should be noted that unlike the old config, key/value pairs are loaded
    exactly as they are represented in the config file. This is important
    particularly for keyboard configuration, because the old  config converted
    key names to key codes, and used them as the dicitonary's keys, using the
    keys pressed as the values. Conversely, in new_config.py, no conversion is
    done, so the key names are used as values where the action to perform is
    used as the keys in the dictionary.

"""
from __future__ import with_statement

from os import environ, makedirs, path, stat
from sys import prefix
from ConfigParser import SafeConfigParser
import platform
import logging

from singletonmixin import Singleton

OS = platform.system().lower()

class Option(dict):
    def __init__(self, args, **kwargs):
        self.name = kwargs['name']
        del kwargs['name']

        self.__parser = kwargs['parser']
        del kwargs['parser']

        self.__config = kwargs['config']
        del kwargs['config']

        dict.__init__(self, args, **kwargs)

    def __setitem__(self, option, value):
        self.__parser.set(self.name, option, str(value))
        dict.__setitem__(self, option, value)
        with open(self.__config, 'wb') as config_file:
            self.__parser.write(config_file)

    def __getitem__(self, key):
        item = dict.__getitem__(self, key)
        # detect whether the item is a bool, int, float, or string
        try:
            return int(item)
        except ValueError:
            try:
                return float(item)
            except ValueError:
                if item.upper() == "True":
                    return True
                elif item.upper() == "False":
                    return False
                else:
                    return item
class Config(Singleton):
    """ Object that implements automatic saving.

        Config first loads default settings from the system config file, then
        overwrites those with the ones found in the user config file. 

        Different config sections can be accessed as
        attributes (eg. Config().section), which would then return an Option 
        object, which acts virtually identical to the builtin dict type. As
        such, specific options can be accesed as keys
        (Config().section[option]).
    """

    def __init__(self):
        self.__parser = SafeConfigParser()
        self.__parser.optionxform=str

        (self.config_dir, self.sys_config_file,
         self.user_config_file, self.data_dir) = self.__get_locations()
        print dir(self)
        print self.sys_config_file, self.user_config_file

        # load sys config options and replace with defined user config options
        self.read([self.sys_config_file, self.user_config_file])
        self.save()

    def __get_locations(self):
        """ returns the appropriate locations of the config directory, system
            config file, user config file, and datadirectories according to the
            user's platform
        """

        # may need to expand once other platforms are tested
        if OS == 'windows':
            # set the config directory to the parent directory of this script
            config_dir = path.dirname(path.abspath(path.join(__file__, '..')))
            sys_config_file = path.join(config_dir, 'system.cfg')
            user_config_file = path.join(config_dir, 'user.cfg')
            data_dir = path.join(config_dir, 'data')
        else:
            try:
                # determine if usf has been installed. If not, use config_dir as the data
                # dir, similar to windows
                data_dir = path.join(prefix, 'share', 
                                     'ultimate-smash-friends', 'data')
                stat(data_dir)
                sys_config_file = path.join('/etc', 'ultimate-smash-friends', 
                                            'system.cfg')

                if 'XDG_CONFIG_HOME' in environ.keys():
                    config_dir = path.join(environ['XDG_CONFIG_HOME'], 'usf')
                else:
                    config_dir = path.join(environ['HOME'], '.config', 'usf')

                user_config_file = path.join(config_dir, 'user.cfg')
            except OSError:
                config_dir = path.dirname(path.abspath(path.join(__file__, '..')))
                sys_config_file = path.join(config_dir, 'system.cfg')
                user_config_file = path.join(config_dir, 'user.cfg')
                data_dir = path.join(config_dir, 'data')

        # create config directory and user config file
        try:
            logging.debug('creating new config directory')
            makedirs(config_dir)
        except OSError:
           pass

        return config_dir, sys_config_file, user_config_file, data_dir

    def save(self):
        with open(self.user_config_file, 'wb') as config_file:
            self.__parser.write(config_file)

    def read(self, files):
        self.__parser.read(files)

        # dynamically create attributes based on sections in the config file,
        # then assign a dictionary of the form "option: value" to each
        # attribute.

        for section in self.__parser.sections():
            setattr(self, section, Option(([item for item in
                    self.__parser.items(section)]),
                    parser=self.__parser,
                    config=self.user_config_file,
                    name=section))
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
