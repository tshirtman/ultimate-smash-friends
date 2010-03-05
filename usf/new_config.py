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
        
    def __init__(self):
        self.__parser = SafeConfigParser()
        self.__parser.optionxform=str

        (self.config_dir, self.sys_config_file, 
         self.user_config_file, self.data_dir) = self.__get_locations()

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
            sys_config_file = path.join(config_dir, 'rc.config')
            user_config_file = sys_config_file
            data_dir = path.join(config_dir, 'data')
        else:
            try: 
                # determine if usf has been installed. If not, use config_dir as the data
                # dir, similar to windows
                data_dir = path.join(prefix, 'share', 
                                     'ultimate-smash-friends', 'data')
                stat(data_dir)
                sys_config_file = path.join(prefix, 'etc', 
                                            'ultimate-smash-frields', 
                                            'rc.config')

                if 'XDG_CONFIG_HOME' in environ.keys():
                    config_dir = path.join(environ['XDG_CONFIG_HOME'], 'usf')
                    user_config_file = path.join(config_dir, 'rc.config')
                else:
                    config_dir = path.join(environ['HOME'], '.config', 'usf')
                    user_config_file = path.join(config_dir, 'rc.config')
            except OSError:
                config_dir = path.dirname(path.abspath(path.join(__file__, '..')))
                sys_config_file = path.join(config_dir, 'rc.config')
                user_config_file = sys_config_file
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
