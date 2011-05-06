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

from screen import Screen
from usf.config import Config
config = Config()

from usf import widgets, entity_skin
import os
from usf.game import Game
from os.path import join


class characters(Screen):
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
        files = os.listdir(join(config.sys_data_dir, 'characters'))
        files.sort()

        for file in files:
            try:
                if file != "none":
                    self.game_data['character_file'].append(join(
                        "characters",
                        file))

                    self.character.append(entity_skin.Entity_skin(
                                    join('characters', file)).name)
            except OSError, e:
                if e.errno is 20:
                    pass
                else:
                    raise
            except IOError, e:
                pass

        self.add(widgets.VBox())

        self.checkboxes_ai = []
        self.portraits = []
        self.player_spinner = []
        self.player_vbox = [widgets.VBox(), widgets.VBox(), widgets.VBox(), widgets.VBox()]

        for i in range(0,4):
            #I18N: Artificial Intelligence
            self.checkboxes_ai.append(widgets.TextCheckBox(_("AI:")))
            self.portraits.append(widgets.Image(
                    join(self.game_data['character_file'][0], "portrait.png")))

            self.player_spinner.append(widgets.Spinner(self.character))
            #I18N: %s is the player number, it can be Player 1, Player2...
            self.player_vbox[i].add(widgets.Label(_("Player %s").replace("%s", str(i+1))))
            self.player_vbox[i].add(self.player_spinner[-1])
            self.player_vbox[i].add(self.portraits[-1],
                margin_left=65,
                margin=5,
                size=(50,50))
            self.player_vbox[i].add(self.checkboxes_ai[-1], margin_left=(180-self.checkboxes_ai[-1].width)/2)


        hbox = widgets.HBox()
        #adding the two box which contains the spinner and the name of the characters
        for vbox in self.player_vbox:
            hbox.add(vbox, margin=20)
        self.widget.add(hbox, margin=50)

        #next button to go to the level screen
        self.widget.add(widgets.Button(_("Next")),
            margin=83,
            align="center")

        #back button to come back to main screen
        self.widget.add(widgets.Button(_('Back')),
            margin=20,
            align="center")

    def callback(self,action):
        if action in self.player_spinner :
            #get the index of the player
            player_number = self.player_spinner.index(action)

            self.players[player_number] = action.get_index()
            #change the portrait
            self.portraits[player_number].setImage(
                        join(
                        self.game_data['character_file'][action.get_index()],
                        "portrait.png"))

        if action.text == _("Next"):
            i  = 0
            for player in self.players:
                if player !=0:
                    i += 1
            if i > 1:
                return 'goto:level'

        if action.text == _('Back'):
            return "goto:back"

