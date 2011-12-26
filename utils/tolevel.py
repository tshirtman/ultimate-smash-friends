#!/usr/bin/env python
# -*- coding : utf-8 -*-
################################################################################
# copyright 2008-2011 Gabriel Pettier <gabriel.pettier@gmail.com>              #
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

import xml.dom.minidom
import sys
"""
Syntax : ./tolevel.py .map .xml nameoflevel
"""
if sys.argv[1] == "--help" :
    print "Syntax : ./tolevel.py .map .xml nameoflevel"
else:
    filin = open(sys.argv[1],'r').readlines()
    content = ""
    for i in filin :
        if "<img" not in i:
            content += i
    xml_file = xml.dom.minidom.parseString(content).getElementsByTagName("map")[0]
    filout = open(sys.argv[2],'w')
    filout.write('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<map \n'
        '	name="'+ sys.argv[3]+'"\n'
        '	background="'+ sys.argv[3]+'-background.png"\n'
        '	foreground="'+ sys.argv[3]+'-foreground.png"\n'
        '	middle="'+ sys.argv[3]+'-middle.png"\n'
        '	>\n')
    for node in xml_file.childNodes :
        try:
            if node.tagName == "area" :
                coords = str(node.getAttribute("coords")).split(',')
                coords = str(coords[0]) + " " + coords[1] + " " + str(int(coords[2])-int(coords[0])) + " " + str(int(coords[3])-int(coords[1]))
                filout.write('\t<block coords="' + coords + '" ></block>\n')
        except:
            pass
    filout.write('</map>')

