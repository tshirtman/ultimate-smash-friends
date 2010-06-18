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
from os import stat

#library import
import pygame

pygame.font.init()
class FontList(object):

    def __init__(self):
        self.list = {}
        font_xml = xml.parse(join(config.sys_data_dir, "fonts", "fonts.xml"))
        for font in font_xml.findall("font"):
            print font.get("file")

            #use theme fonts
            try:
                font_file = join(config.sys_data_dir, "gui",
                    config.general['THEME'], font.get('file'))
                stat(font_file)
            #use default usf fonts
            except:
                font_file = join(config.sys_data_dir, "fonts", font.get('file'))

            self.list[font.get('name')] = Font(font.get('name'), int(font.get('size')), font_file)

    def __getitem__(self, item):
        if self.list[item]:
            return self.list[item]
        else:
            print "No font named" + str(item)
            return self.list['sans']


class Font(object):

    def __init__(self, name, size, font_file, bold="", italic="", bolditalic=""):
        self.font = pygame.font.Font(font_file, config.general["HEIGHT"]/size)
        if bold != "":
            self.bold = pygame.font.Font(bold,
                config.general["HEIGHT"]/size)
        if italic != "":
            self.italic = pygame.font.Font(italic,
                config.general["HEIGHT"]/size)
        if bolditalic != "":
            self.bolditalic = pygame.font.Font(bolditalic,
                config.general["HEIGHT"]/size)

    def __getitem__(self, item):
        if item == "normal":
            return self.font
        if item == "bold" and self.bold:
            return self.bold
        if item == "italic" and self.italic:
            return self.italic
        if item == "bolditalic" and self.bolditalic:
            return self.bolditalic
        
        print "No font named : " + str(item)
        
        return self.font
            
fonts = FontList()

