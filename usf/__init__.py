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
