################################################################################
# copyright 2010 Lucas Baudin <xapantu@gmail.com>                              #
#                                                                              #
# This file is part of Ultimate Smash Friends.                                 #
#                                                                              #
# Ultimate Smash Friends is free software: you can redistribute it and/or      #
# modify it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or (at your   #
# option) any later version.                                                   #
#                                                                              #
# Ultimate Smash Friends is distributed in the hope that it will be useful, but#
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or#
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# You should have received a copy of the GNU General Public License along with #
# Ultimate Smash Friends.  If not, see <http://www.gnu.org/licenses/>.         #
################################################################################

'''
This module provides a widget for UI, allowing to display and edit a line of
text, it can be used to edit settings like an IP address for a network game, or
a player name.

'''
from math import sin

from pygame import color, draw
from pygame.locals import (
    K_DOWN, K_UP, K_RETURN, K_LEFT, K_RIGHT, K_BACKSPACE, MOUSEBUTTONUP, 
    K_DELETE
)

from usf import font, loaders
from usf.widgets.button import Button
from usf.widgets.label import Label

class TextEntry(Button):
    """
    A widget allowing to enter some text
    """

    animation_speed = 1/10.0
    def __init__(self, text, *args, **kwargs):
        super(TextEntry, self).__init__(text, *args, **kwargs)
        self.properties["size_request"] = (220, 20)
        self.dynamic_size[1] = True

        self.cursor = len(self.text)
        self.posx = 0
        self.posy = 0
        self.cursor_red = 0.0
        self.cursor_green = 0.0
        self.cursor_blue = 0.0
        self.cursor_state = 0.0

    def get_text(self):
        """
        Get the current text of the widget.
        """
        return self.text

    def move_cursor(self, x):
        """ place the cursor at the position nearest of x in the widget
        """
        x -= self.indent
        text = self.get_text()
        diff = self.width
        self.cursor = 1
        text_font = font.fonts["sans"]["normal"]
        for i in range(0, len(text) + 1):
            diff_temp = min(diff,
                    abs(x - loaders.text(text[0:i], text_font).get_width()))
            if diff is not diff_temp:
                self.cursor = i
            diff = diff_temp

    def handle_mouse(self, event):
        """ set focus if the click was on the text entry, so we can type in it
        """
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        if event.type == MOUSEBUTTONUP:
            if self.state:
                x -= self.parentpos[0] + self.x
                y -= self.parentpos[1] + self.y
            if 0 < x < self.width and 0 < y < self.height:
                self.move_cursor(x)
                self.state = True
                return False, self

            self.state = False
            return False, False
        return False, (self if self.state else False)

    def handle_keys(self, event):
        """ manage keyboard input events
        """
        if not self.state:
            return False, False

        if event.dict["key"] == K_RETURN:
            return self, self

        elif event.dict['key'] == K_DELETE:
            if self.cursor <= len(self.text):
                self.set_text(''.join((
                        self.text[:self.cursor],
                        self.text[self.cursor + 1:])))

        elif event.dict['key'] == K_BACKSPACE:
            if self.cursor > 0:
                self.set_text(''.join((
                        self.text[:self.cursor-1],
                        self.text[self.cursor:])))
                self.cursor -= 1

        elif event.dict["key"] == K_LEFT:
            self.cursor = max(0, self.cursor - 1)

        elif event.dict["key"] == K_RIGHT:
            self.cursor = min(len(self.text) + 1, self.cursor + 1)

        else:
            if event.dict['unicode']:
                try:
                    self.set_text(''.join((
                            self.text[:self.cursor],
                            event.dict["unicode"],
                            self.text[self.cursor:])))
                    self.cursor += 1
                except UnicodeEncodeError:
                    pass

        return False, False

    def draw(self):
        super(TextEntry, self).draw()

        # Display the cursor
        if self.state:
            # Get text width
            offset = loaders.text(
                    self.get_text()[0:self.cursor],
                    font.fonts["sans"]['normal']).get_width() + self.indent

            # Draw cursor
            color_value = int(abs(sin(self.cursor_state))*255)/2
            #print color_value
            color_cursor = color.Color(color_value, color_value, color_value)
            draw.line(self.screen, color_cursor,
                      (self.parentpos[0] + self.x + offset,
                       self.parentpos[1] + self.y),
                      (self.parentpos[0] + self.x + offset,
                       self.parentpos[1] + self.y + self.height),
                     2)
        self.start_anim()

    def animation(self):
        self.cursor_state += 0.1


