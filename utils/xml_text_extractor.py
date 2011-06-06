#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

# extract label strings from xml files to a dummy .py file
# to be able to use them with gettext

import os
import re
from usf_modules.config import config

PATH = os.sep.join((config['MEDIA_DIRECTORY'], 'gui'))

regex_str = re.compile('value *= *".*?"')

strings = []

for file in os.listdir(PATH):
    if ".usfgui" in file:
        f = open(os.sep.join((PATH, file)))
        s = f.read()
        f.close()
        strings.extend(re.findall(regex_str, s))

f = open('strings.py', 'w')
for s in strings:
    if ".png" not in s:
        f.write(s.replace('value','print ').replace('=','_(')+')\n')
f.close()
