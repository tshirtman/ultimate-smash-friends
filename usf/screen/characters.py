################################################################################
# copyright 2009 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
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
import copy, os
from usf.game import Game
from os.path import join


class characters(Screen):
    name_pl1 = 0
    name_pl2 = 0
    name_pl3 = 0
    name_pl4 = 0
    players = [0,0,0,0]

    def init(self):
        self.game_data = {}
        self.game_data['character_file'] = []
        
        #create a character file to have the [?] image
        self.game_data['character_file'].append("characters" + os.sep + 'none')
        self.character = []
        self.character.append("None")
        #create a character for every directory in the characters directory.
        files = os.listdir(
                os.path.join(
                    config.sys_data_dir,
                    'characters'
                    )
                )
        files.sort()
        for file in files:
            try:
                if file != "none":
                    self.game_data['character_file'].append(join("characters", file))
                    self.character.append(entity_skin.Entity_skin(
                                    join(
                                    'characters',
                                    file
                                    )
                                ).name)
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
            self.checkboxes_ai.append(widgets.CheckBox())
            self.portraits.append(widgets.Image(self.game_data['character_file'][0]
                                 + os.sep
                                 + self.game_data['character_file'][0].replace('characters' + os.sep, "")
                                 + "-portrait.png", size=(50,50)))
            self.player_spinner.append(widgets.Spinner(self.character))
            self.player_vbox[i].add(widgets.Label("Player " + str(i+1)))
            self.player_vbox[i].add(self.player_spinner[-1])
            self.player_vbox[i].add(self.portraits[-1], margin_left=50, margin=5)
            hbox = widgets.HBox()
            #this is very bad for performance
            hbox.add(widgets.Label("AI :"))
            hbox.add(self.checkboxes_ai[-1], margin=10)
            self.player_vbox[i].add(hbox)

        
        hbox = widgets.HBox()
        #adding the two box which contains the spinner and the name of the characters
        for vbox in self.player_vbox:
            hbox.add(vbox, margin=40)
        self.widget.add(hbox, margin=50)
        self.widget.add(widgets.Button(_("Next")), margin_left=290, margin=83)
        self.widget.add(widgets.Button(_('Back')), size=(150, 40), margin_left=20, margin=20)

    def callback(self,action):
        if action in self.player_spinner :
            player_number = self.player_spinner.index(action)
            self.players[player_number] = action.getIndex()
            self.portraits[player_number].setImage(self.game_data['character_file'][action.getIndex()] + os.sep +
                self.game_data['character_file'][action.getIndex()].replace('characters' + os.sep, "") + "-portrait.png")

        if action.text == _("Next"):
            return 'goto:level'

        if action.text == _('Back'):
            return "goto:back"

