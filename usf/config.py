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

from os import environ, makedirs, stat, sep
from os.path import join, dirname, abspath
from sys import prefix
from ConfigParser import SafeConfigParser
import platform
import logging
import pygame

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
        # automatically save recently changed value to file
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

        (self.config_dir, self.sys_config_file, self.user_config_file, 
         self.sys_data_dir, self.user_data_dir) = self.__get_locations()

        # load sys config options and replace with defined user config options
        self.read([self.sys_config_file, self.user_config_file])
        self.save()

    def __get_locations(self):
        """ returns the appropriate locations of the config directory, config
            files, and data directories according to the user's platform
        """

        # may need to expand once other platforms are tested
        if OS == 'windows':
            """ from what I can understand, windows saves user data/config info
                inside of an APPDATA environment variable. I am hold off on
                writing this portion until we get a working setup.py, py2exe or
                similar so that proper testing can be done. From there, filling
                in the blanks should be trivial
            """
			#TODO : a proper system to localize .cfg
            sys_data_dir = join(__file__, '..', '..', '..', 'data')
            sys_config_file = join(__file__, '..', '..', '..', 'system.cfg')
            # see if files are installed on the system
            stat(sys_data_dir)

            # set the variables according to HOME variable
            config_dir = join(environ['APPDATA'], 'usf')

            user_config_file = join(config_dir, 'user.cfg')
            user_data_dir = join(config_dir, 'user_data')
        elif OS == 'linux':
            try:
                sys_data_dir = join(prefix, 'share', 'ultimate-smash-friends',
                                    'data')
                sys_config_file = join(sep, 'etc', 'ultimate-smash-friends',
                                       'system.cfg')

                # see if files are installed on the system
                stat(sys_data_dir)

                # set the variables according to HOME variable
                if 'XDG_CONFIG_HOME' in environ.keys():
                    config_dir = join(environ['XDG_CONFIG_HOME'],
                                      'ultimate-smash-friends')
                else:
                    config_dir = join(environ['HOME'], '.config',
                                      'ultimate-smash-friends')

            except OSError:
                # files aren't installed on the system so set config_dir to the
                # parent directory of this module
                config_dir = dirname(abspath(join(__file__, '..')))
                sys_data_dir = join(config_dir, 'data')
                sys_config_file = join(config_dir, 'system.cfg')

            user_config_file = join(config_dir, 'user.cfg')
            user_data_dir = join(config_dir, 'user_data')

        try:
            # create user config and user data directories
            makedirs(config_dir)
            makedirs(user_data_dir)
        except OSError:
            # paths already exist or user doesn't have permissions
            pass
        
        return (config_dir, sys_config_file, user_config_file, 
                sys_data_dir, user_data_dir)

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

