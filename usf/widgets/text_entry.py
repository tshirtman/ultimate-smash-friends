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
This moodule provide a widget for UI, allowing to display and edit a line of
text, it can be used to edit settings like an IP address for a network game, or
a player name.

'''

from usf.widgets.label import Label
from pygame.locals import K_DOWN, K_UP, K_RETURN, K_LEFT, K_RIGHT, K_BACKSPACE

class TextEntry(Label):
    """
    A widget allowing to enter some text
    """

    def __init__(self, text, *args, **kwargs):
        super(TextEntry, self).__init__(text, *args, **kwargs)

        self.properties["focusable"] = True
        self.cursor = len(self.text)

    def get_text(self):
        """
        Get the current text of the widget.
        """
        return self.text

    def handle_keys(self, event):
        """ manage keyboard input events
        """
        #if (
                #event.dict["key"] == K_DOWN or
                #event.dict["key"] == K_UP) and not self.state:
            #self.state = True
            #return False, self

        if event.dict["key"] == K_RETURN:
            return self, self

        elif event.dict['key'] == K_BACKSPACE:
            if self.cursor > 0:
                self.set_text(''.join((
                        self.text[:self.cursor-1],
                        self.text[self.cursor:])))
                self.cursor -= 1

        elif event.dict["key"] == K_LEFT:
            self.cursor = max(0, self.cursor - 1)

        elif event.dict["key"] == K_RIGHT:
            self.cursor = min(len(self.text), self.cursor + 1)

        else:
            if event.dict['unicode']:
                self.set_text(''.join((
                        self.text[:self.cursor],
                        event.dict["unicode"],
                        self.text[self.cursor:])))
                self.cursor += 1

        return False, False

