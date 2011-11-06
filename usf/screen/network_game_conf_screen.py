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
Show connected users list, player choices and level choice for a network game,
this screen should be seen identically by the player hosting the game and the
player(s) joining it, only each player can only chose his character. Level can
be chosen by both, the game start when both player have clicked the "start
game" button (maybe with some time delay, and with possibility to cancel?).

'''

from usf.screen.screen import Screen
from usf import loaders
CONFIG = loaders.get_config()

from usf.widgets.box import VBox, HBox
from usf.widgets.button import Button
from usf.widgets.image import Image
from usf.widgets.spinner import Spinner
from usf.widgets.label import Label
from usf.widgets.checkbox_text import TextCheckBox
from usf.widgets.text_entry import TextEntry
from usf.widgets.coverflow import Coverflow

from usf.translation import _

from usf import entity_skin
import os
from os.path import join
import logging


class NetworkGameConfScreen(Screen):
    """ the network game configuration screen
    """
    name_pl1 = 0
    name_pl2 = 0
    name_pl3 = 0
    name_pl4 = 0
    players = [0, 0, 0, 0]

    def init(self):
        self.game_data = {}
        self.game_data['character_file'] = []

        #I18N: The title of the screen where players can choose their character.
        self.set_name(_("characters"))

        #create a character file to have the [?] image
        self.game_data['character_file'].append(join('characters', 'none'))
        self.character = []
        #I18N: in the character screen, to select no character for this player
        #I18N: (with the [?] icon)
        self.character.append(_("None"))
        #create a character for every directory in the characters directory.
        files = os.listdir(join(CONFIG.system_path, 'characters'))
        files.sort()

        self.load_chararacters(files)

        self.add(VBox())

        self.portrait = Image(join(self.game_data['character_file'][0],
            "portrait.png"))

        self.player_spinner = Spinner(self.character)
        player_vbox = VBox()
        player_vbox.add(Label(_('Player name'), align='center'))
        player_vbox.add(TextEntry(_('unnamed player')))
        player_vbox.add(Spinner(self.character))
        player_vbox.add(self.portrait, margin_left=65, margin=5, size=(50, 50))

        hbox = HBox()
        # adding the two box which contains the spinner and the name of the
        # characters
        hbox.add(player_vbox, margin=400)
        self.widget.add(hbox, margin=150)

        #create a level image for every directory in the level directory.
        files = os.listdir(os.path.join( CONFIG.system_path, 'levels'))
        files.sort()

        coverflow_data = self.load_levels(files)

        self.coverflow = Coverflow(coverflow_data)
        self.widget.add(self.coverflow, size=(800, 275))

        #next button to go to the level screen
        self.widget.add(Button(_("Start")),
            margin=83,
            align="center")

        #back button to come back to main screen
        self.widget.add(Button(_('Back')),
            margin=20,
            align="center")

    def load_chararacters(self, files):
        """ append characters to self.character, loaded from files in "files".
        """
        for f in files:
            try:
                if f != "none":
                    self.game_data['character_file'].append(join(
                        "characters",
                        f))

                    self.character.append(entity_skin.EntitySkin(
                                    join('characters', f)).name)
            except OSError, e:
                if e.errno is 20:
                    pass
                else:
                    raise
            except IOError, e:
                pass

    def load_levels(self, files):
        """ append a level in self.levels
        """
        coverflow_data = []
        for f in files:
            try:
                if 'level.xml' in os.listdir(
                        os.path.join(CONFIG.system_path, "levels", f)):
                    coverflow_data.append([])
                    coverflow_data[-1].append(f)
                    coverflow_data[-1].append(
                            join(
                                CONFIG.system_path,
                                "levels", f, "screenshot.png"))
            except:
                #XXX: catch all exceptions: BAD
                logging.debug(str(f) +" is not a valid level.")
        return coverflow_data

    def callback(self, action):
        if action is self.player_spinner :
            #get the index of the player
            player_number = self.player_spinner.index(action)

            self.players[player_number] = action.get_index()
            #change the portrait
            self.portraits[player_number].setImage(
                    join(
                        self.game_data['character_file'][action.get_index()],
                        "portrait.png"))

        if action.text == _("Start"):
            i  = 0
            for player in self.players:
                if player != 0:
                    i += 1
            if i > 1:
                return 'goto:level'

        if action.text == _('Back'):
            return "goto:back"

