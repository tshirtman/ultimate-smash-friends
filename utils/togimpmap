#!/usr/bin/env python
# -*- coding : utf-8 -*-
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
        content += i
    xml_file = xml.dom.minidom.parseString(content).getElementsByTagName("map")[0]
    filout = open(sys.argv[2],'w')
    filout.write('<img src="Sans titre" width="1000" height="600" border="0" usemap="#map" />'
                 '<map name="map">\n'
                 '<!-- #$-:Image map file created by GIMP Image Map plug-in -->\n'
                 '<!-- #$-:GIMP Image Map plug-in by Maurits Rijk -->\n'
                 '<!-- #$-:Please do not edit lines starting with "#$" -->\n'
                 '<!-- #$VERSION:2.3 -->\n'
                 '<!-- #$AUTHOR:xapantu -->\n')
    for node in xml_file.childNodes :
        try:
            if node.tagName == "block" :
                coords = str(node.getAttribute("coords")).split(' ')
                coords = str(coords[0]) + "," + coords[1] + "," + str(int(coords[2])+int(coords[0])) + "," + str(int(coords[3])+int(coords[1]))
                filout.write('\t<area shape="rect" coords="' + coords + '" nohref="nohref" />\n')
        except:
            pass
    filout.write('</map>')

