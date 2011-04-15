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

from __future__ import with_statement

from os import environ, makedirs, stat, sep
import os
from os.path import join, dirname, abspath
from sys import prefix
from memoize import memoize

from ConfigParser import SafeConfigParser
import platform
import logging

import pygame

OS = platform.system().lower()


@memoize
def _splitconf(c):
    return [value.strip().strip('\'\"') for value in c.split(',')]


@memoize
def _get_value_from_config(c):
    values = _splitconf(c)
    for item in values:
        try:
            # try to convert it into an integer instead
            values[values.index(item)] = int(item)
        except ValueError:
            try:
                # try to convert the item into a float
                values[values.index(item)] = float(item)
            except ValueError:
                # try to convert it into a boolean otherwise it's a string
                if item.lower() in ['true', 't', 'yes', 'y']:
                    values[values.index(item)] = True
                elif item.lower() in ['false', 'f', 'no', 'n']:
                    values[values.index(item)] = False

    if len(values) == 1:
        return values[0]
    else:
        return values


class Option(dict):
    """#FIXME: doc!
    """

    def __init__(self, args, **kwargs):
        self.name = kwargs['name']
        del kwargs['name']

        self.__parser = kwargs['parser']
        del kwargs['parser']

        self.__config = kwargs['config']
        del kwargs['config']

        dict.__init__(self, args, **kwargs)

    def __setitem__(self, option, value):
        try:
            #invalidate cache of __getitem__
            _get_value_from_config.cache = {}
        except AttributeError:
            logging.warning("__getitem__ not memoized? oO")

        self.__parser.set(self.name, option, str(value))
        dict.__setitem__(self, option, str(value))
        # automatically save recently changed value to file
        with open(self.__config, 'wb') as config_file:
            self.__parser.write(config_file)

    def __getitem__(self, key):
        # create a list of strings for the stored value
        return _get_value_from_config(dict.__getitem__(self, key))


class Config(object):
    """ Object that implements automatic saving.

        Config first loads default settings from the system config file, then
        overwrites those with the ones found in the user config file.

        Different config sections can be accessed as
        attributes (eg. Config().section), which would then return an Option
        object, which acts virtually identical to the builtin dict type. As
        such, specific options can be accesed as keys
        (Config().section[option]).
    """

    # inspired by http://code.activestate.com/recipes/66531/
    __shared_state = {}

    def __init__(self, config_files=None):
        self.__dict__ = self.__shared_state
        self.__parser = SafeConfigParser()
        self.__parser.optionxform = str

        (self.user_config_dir, self.sys_config_file, self.user_config_file,
         self.sys_data_dir, self.user_data_dir) = self.__get_locations()

        if config_files is None:
            self.read([self.sys_config_file, self.user_config_file])
        else:
            self.read(config_files)

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

            try:
                sys_data_dir = join(environ['PROGRAMFILES'],
                                    'Ultimate Smash Friends', 'data')
                sys_config_file = join(environ['PROGRAMFILES'],
                                       'Ultimate Smash Friends', 'system.cfg')

                # see if files are installed on the system
                stat(sys_data_dir)

            except OSError:
                # files aren't installed on the system so set user_config_dir
                # to the parent directory of this module
                user_config_dir = dirname(abspath(join(__file__, '..\..')))
                sys_data_dir = join(user_config_dir, 'data')
                sys_config_file = join(user_config_dir, 'system.cfg')

            user_config_dir = join(environ['APPDATA'],
                                'Ultimate Smash Friends')
            user_config_file = join(user_config_dir, 'user.cfg')
            user_data_dir = join(user_config_dir, 'user_data')

        else:
            sys_data_dir = ""
            #for the devlopment version
            #"./data/", "./system.cfg"

            #if someone launch launch main.py directly
            #"../data/", "../system.cfg"

            #an easier way to create a mod
            #"../usf-data/", "./system.cfg"

            #standard use
            #"/usr/share/ultimate-smash-friends/data/",
            #"/etc/ultimate-smash-friends/system.cfg"

            for datadir in [
                ("../usf-data/", "./system.cfg"),
                ("./data/", "./system.cfg"),
                ("../data/", "../system.cfg"),
                ("/usr/share/ultimate-smash-friends/data/",
                    "/etc/ultimate-smash-friends/system.cfg")]:
                try:
                    stat(datadir[0])
                    sys_data_dir = datadir[0]

                    if 'XDG_CONFIG_HOME' in environ.keys():
                        user_config_dir = join(environ['XDG_CONFIG_HOME'],
                                          'ultimate-smash-friends')
                    else:
                        user_config_dir = join(environ['HOME'], '.config',
                                          'ultimate-smash-friends')
                    sys_config_file = datadir[1]
                    break
                except OSError:
                    pass
            if sys_data_dir == "":
                logging.error("Error: no valid data directory - aborting")
                logging.error("Current dir: " + os.getcwd())
                exit(-1)

            user_config_file = join(user_config_dir, 'user.cfg')
            user_data_dir = join(user_config_dir, 'user_data')

        try:
            # create user config and user data directories
            makedirs(user_config_dir)
            makedirs(user_data_dir)
        except OSError:
            # paths already exist or user doesn't have permission to create them
            pass

        return (user_config_dir, sys_config_file, user_config_file,
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

    def reverse_keymap(self, keycode=None):
        keymap = dict((value, key)
                      for key, value in pygame.__dict__.iteritems()
                      if key[:2] in ('K_', 'KM'))

        if keycode is not None:
            return keymap[keycode]

