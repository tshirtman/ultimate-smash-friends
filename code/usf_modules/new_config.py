"""  copyright 2010 Edwin Marshall (aspidites) <aspidties@gmx.com>

 This file is not part of UltimateSmashFriends, yet, but is still
 distributable under the same license terms as UltimateSmashFriends.

 Goals
   - Remove external dependencies
   - DRY (remove tasks that are performed better by core libraries
   - Cross-platform
   - Keep syntax familiar. Where possible, I kept function names the same and
     tried to adhere to already present coding standards.

Notes
  - This is incomplete. To make it functional, I would have to modify 3 or four
    other files. I wanted to see if the  core developers of USF liked my
    modifications of the config file first (hince the name new_config.py
    instead of a simple overwrite).

  - SafeConfigParser allows you to easily read from and write to standard
    config files with simple commands:
        config.set('Audio', 'SOUND_VOLUME', 500) # set the sound volume to 50
        config.get('Audio', 'SOUND_VOLUME') # retrieve the sound volume
        config.write(open(config_file, 'wb')) # write all settings to file

"""

from os import environ, makedirs, path
import platform
import logging

from ConfigParser import SafeConfigParser

import pygame.locals

OS = platform.system().lower()
config = SafeConfigParser()

# may need to expand once other platforms are tested
if OS == 'windows':
    # set the config directory to the parent directory of this script
    config_dir = path.dirname(path.abspath(__file__ + '/..'))
else:
    if 'XDG_CONFIG_HOME' in environ.keys():
        config_dir = environ['XDG_CONFIG_HOME'] + '/usf'
        config_file = config_dir + '/config.ini'
    else:
        config_dir = environ['HOME'] + '/.config/usf'
        config_file = config_dir + '/config'

def open_config(section):
    # create the config directory if it doesn't already exist
    try:
        logging.debug('creating new config directory')
        makedirs(config_dir)
    except OSError as (code, message):
       pass

    # create the config file if it doesn't already exist 
    try:
        open(config_file)
        config.read(config_file)
    except IOError:
        logging.debug('creating '+section+' section')
        config.add_section(section)
        config.write(open(config_file, 'wb'))

def load_conf(section):
    return dict(config.get(section))

def save_conf(section, **kwargs):
    if section == 'General':
        pass
    elif section == 'Audio':
        pass
    elif section == 'Keys':
        pass


if __name__ == '__main__':
    save_conf('general', keys=5)
