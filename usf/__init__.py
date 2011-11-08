'''
Ultimate Smash friends is a game designed to provide tons of fun :D

It also focus on being easy to mod and to be easilily extensible both in code
and in gameplay.

'''
import os

import memoize
from config import Config

# find the appropriate data and config paths
PATHS = {}
for dirs in [('../usf-data', '.'),
             ('./data', '.'),
             ('../data', '../'),
             ('/usr/share/ultimate-smash-friends/data', 
                 '/etc/ultimate-smash-friends')]:
    if os.path.isdir(dirs[0]) and os.path.isdir(dirs[1]):
        PATHS['system_path'] = dirs[0]
        PATHS['config_path'] = dirs[1]
        break

if 'XDG_CONFIG_HOME' in os.environ.keys():
    PATHS['user_path'] = os.path.join(os.environ['XDG_CONFIG_HOME'],
                         'ultimate-smash-friends')
else:
    PATHS['user_path'] = os.path.join(os.environ['HOME'], '.config',
                         'ultimate-smash-friends')

# create a config object using above paths
CONFIG = Config(**PATHS)
