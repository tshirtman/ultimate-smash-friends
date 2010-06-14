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
from config import Config
config = Config()

import widgets, entity_skin
import copy, os
from game import Game
class local_game(Screen):
    name_pl1 = 0
    name_pl2 = 0
    name_pl3 = 0
    name_pl4 = 0
    players = [0,0,0,0]
    def init(self):
        self.game_data = {}
        self.game_data['character_file'] = []
        self.game_data['character_file'].append("characters" + os.sep + 'none')
        self.character = []
        self.character.append("None")
        self.game_data['level_name'] = []
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
                self.game_data['character_file'].append("characters" + os.sep + file)
                self.character.append(entity_skin.Entity_skin(
                            os.path.join(
                                'characters',
                                file
                                )
                            ).name)
                #logging.debug( "character "+file+" created.")
            except OSError, e:
                if e.errno is 20:
                    pass
                else:
                    raise
            except IOError, e:
                #logging.debug(file+" is not a valid character directory.", 3)
                #raise
                #logging.debug(e)
                pass
        #create a level image for every directory in the level directory.
        files = os.listdir(
                os.path.join(
                    config.sys_data_dir,
                    'levels'
                    )
                )
        files.sort()
        for file in files:
            try:
                if '.xml' in file :
                    self.game_data['level_name'].append(file.replace(".xml",""))
            except :
                #logging.debug(file+" is not a valid level.")
                raise
                pass
        self.add(widgets.HBox())
        """
        pl12 = widgets.VBox()
        pl23 = widgets.VBox()
        """
        """
        self.widget.add(pl12, margin=100)
        
        
        self.widget.add(pl23, margin=20)
        """
        """
        self.pl1 = widgets.Spinner(self.character)
        self.pl2 = widgets.Spinner(self.character)
        self.pl3 = widgets.Spinner(self.character)
        self.pl4 = widgets.Spinner(self.character)
        """
        """
        self.img1 = widgets.Image(self.game_data['character_file'][0] + os.sep +
            self.game_data['character_file'][0].replace('characters' + os.sep, "") + "-portrait.png", size=(50,50))
        self.img2 = widgets.Image(self.game_data['character_file'][0] + os.sep +
            self.game_data['character_file'][0].replace('characters' + os.sep, "") + "-portrait.png", size=(50,50))
        self.img3 = widgets.Image(self.game_data['character_file'][0] + os.sep +
            self.game_data['character_file'][0].replace('characters' + os.sep, "") + "-portrait.png", size=(50,50))
        self.img4 = widgets.Image(self.game_data['character_file'][0] + os.sep +
            self.game_data['character_file'][0].replace('characters' + os.sep, "") + "-portrait.png", size=(50,50))
        """
            
        self.w_launch = widgets.Button("Launch the game")
        """
        pl12.add(widgets.Label("Player 1"), margin=150)
        pl12.add(self.pl1)
        pl12.add(self.img1, margin_left=50, margin=5)
        pl12.add(widgets.Label("Player 2"), margin=20)
        pl12.add(self.pl2)
        pl12.add(self.img2, margin_left=50, margin=5)
        pl23.add(widgets.Label("Player 2"), margin=150)
        pl23.add(self.pl3)
        pl23.add(self.img3, margin_left=50, margin=5)
        pl23.add(widgets.Label("Player 3"), margin=20)
        pl23.add(self.pl4)
        pl23.add(self.img4, margin_left=50, margin=5)
        pl23.add(self.w_launch, size=(200,50), margin=20)
        """
        self.checkboxes_ai = []
        self.portraits = []
        self.player_spinner = []
        self.player_vbox = [widgets.VBox(), widgets.VBox()]
        for i in range(0,4):
            self.checkboxes_ai.append(widgets.CheckBox())
            self.portraits.append(widgets.Image(self.game_data['character_file'][0] + os.sep + self.game_data['character_file'][0].replace('characters' + os.sep, "") + "-portrait.png", size=(50,50)))
            self.player_spinner.append(widgets.Spinner(self.character))
            
            self.player_vbox[i/2].add(widgets.Label("Player " + str(i+1)), margin=20)
            self.player_vbox[i/2].add(self.player_spinner[-1])
            self.player_vbox[i/2].add(self.portraits[-1], margin_left=50, margin=5)
            self.player_vbox[i/2].add(widgets.Label("AI :"), margin=20)
            self.player_vbox[i/2].add(self.checkboxes_ai[-1])
        for vbox in self.player_vbox:
            self.widget.add(vbox, size=(200,50), margin=20)
        self.player_vbox[1].add(self.w_launch, margin=20)
        #level elements
        self.level_name = widgets.Spinner(self.game_data['level_name'])
        self.level_image = widgets.Image('gui'+ os.sep + 'image' + os.sep + 'BiX_level.png')
        level_box = widgets.VBox()
        level_box.add(widgets.Label("Level"), margin=150)
        self.widget.add(level_box, margin=40)
        level_box.add(self.level_name)
        level_box.add(self.level_image, size=(200,120), margin=5)
        
    def callback(self,action):
        if action in self.player_spinner :
            player_number = self.player_spinner.index(action)
            self.players[player_number] = action.getIndex()
            self.portraits[player_number].setImage(self.game_data['character_file'][action.getIndex()] + os.sep +
                self.game_data['character_file'][action.getIndex()].replace('characters' + os.sep, "") + "-portrait.png")
        if action == self.level_name :
            self.level_image.setImage("gui" + os.sep + "image" + os.sep + self.game_data['level_name'][action.getIndex()] + ".png")
        if action == self.w_launch:
            return self.launch_game()

    def launch_game(self):
        """
        Function to launch the game, use precedant user choices to initiate the
        game with level and characters selected.

        """

        players = [
        self.game_data['character_file'][p]
        for p in self.players if p != 0
        ]
        for i in range(0,len(players)):
            if self.checkboxes_ai[i].get_value():
                players[i] = players[i].replace("characters/", "characters/AI")
        if len(players) > 1:
            game = Game(
                self.screen,
                self.game_data['level_name'][self.level_name.getIndex()],
                players
            )

            #thread.start_new_thread(self.loading, ())
            #self.goto_screen("ingame.usfgui", False)
            #self.state="game"
            return game
