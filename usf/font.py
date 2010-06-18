################################################################################
# copyright 2010 Lucas Baudin <xapantu@gmail.com>                              #
#                                                                              #
# This file is part of UltimateSmashFriends                                    #
#                                                                              #
# UltimateSmashFriends is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by the Free#
# Software Foundation, either version 3 of the License, or (at your option) any#
# later version.                                                               #
#                                                                              #
# UltimateSmashFriends is distributed in the hope that it will be useful, but  #
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or#
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# You should have received a copy of the GNU General Public License along with #
# UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.           #
################################################################################

#our modules
from config import Config
config = Config()

#standart imports
import xml.etree.ElementTree as xml
from os.path import join


class FontList(object):

    def __init__(self):
        self.list = {}
        font_file = xml.parse(join(config.sys_data_dir, "fonts", "fonts.xml"))

    def __getitem__(self, item):
        if self.list[item]:
            return self.list[item]
        else:
            print "No font named" + str(item)
            return self.list['sans']


font = FontList()

