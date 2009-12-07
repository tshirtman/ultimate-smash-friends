################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
#                                                                              #
# This file is part of Ultimate Smash Friends                                  #
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

# FIXME this menu system is either completly borken or really badly coded. way
# too many levels of conditions in both rendering and key management...
# consider starting all over.

from pygame.locals import USEREVENT, QUIT
from math import sin, cos
from time import time
import os
import pygame

from loaders import image
from config import (
        config,
        sound_config,
        save_sound_conf,
        save_keys_conf
        )
import controls
import entity_skin
from debug_utils import LOG
from game import Game
from config import xdg_config_home

class Menu:
    def __init__(self, surface):
        self.characters = []
        self.players = [None, None, None, None]
        self.state = 'main'
        self.levels = []
        self.level = 0
        self.R, self.V, self.B = '00','22','55'
        self.key_list={}
        for (k,m) in [
        l.split(':') for l in open(os.path.join(xdg_config_home,'usf','keys.cfg')).readlines()
        if len(l.split(':')) == 2
        ]:
            try:
                self.key_list[
                k.split(';')[0].split('#')[0].replace(' ','')
                ] = m.split(';')[0].split('\n')[0].split('#')[0]\
                                    .replace(' ','').split('_')[1]
            except:
                pass

        #create a character for every directory in the characters directory.
        files = os.listdir(
                os.path.join(
                    config['MEDIA_DIRECTORY'],
                    'characters'
                    )
                )
        files.sort()
        for file in files:
            try:
                self.characters.append(
                        entity_skin.Entity_skin(
                            os.path.join(
                                'characters',
                                file
                                )
                            )
                        )
                #LOG().log( "character "+file+" created.")
            except OSError, e:
                if e.errno is 20:
                    pass
                else:
                    raise
            except IOError, e:
                LOG().log(file+" is not a valid character directory.", 3)
                #raise
                #LOG().log(e)
                pass

        #create a level image for every directory in the level directory.
        files = os.listdir(
                os.path.join(
                    config['MEDIA_DIRECTORY'],
                    'levels'
                    )
                )
        files.sort()
        for file in files:
            if 'middle' not in file :
                #LOG().log('NOT '+file)
                continue
            try:
                img = os.path.join(
                            config['MEDIA_DIRECTORY'],
                            'levels',
                            file
                            )

                #img = pygame.transform.scale(img, config['SIZE'])
                self.levels.append((''.join(file.split('-middle')[0]),img))
                #LOG()("level "+file+" miniature created.")
            except :
                #LOG()(file+" is not a valid level.")
                raise
                pass

        self.menu_elements = {}
        for file in os.listdir(
                os.path.join(
                    config['MEDIA_DIRECTORY'],
                    'misc',
                    'menu'
                    )
                ):
            try:
                self.menu_elements[
                                    ''.join(file.split(os.extsep)[:-1])
                                  ] = os.path.join(
                                              config['MEDIA_DIRECTORY'],
                                              'misc',
                                              'menu',
                                              file
                                              )
            except:
                #LOG().log(file+" is not a valid image file.")
                pass

        self.entries={
            'main': (
                    'Local game',
                    'Configure',
                    'Credits',
                    'Quit'
                    ),
            'main_pause': (
                    'Resume game',
                    'Local game',
                    'Configure',
                    'Credits',
                    'Quit'
                    ),
            'quit':('yes', 'no'),
            'configure': ('Keyboard','Sound',),
            'sound': ('music','sounds','save','reset'),
            'keyboard': ['QUIT','TOGGLE_FULLSCREEN','VALIDATE']+
            [
            'PL'+str(p+1)+'_'+k for p in range(4)
            for k in ('UP','DOWN','LEFT','RIGHT','A','B')
                ]+['save','reset']
        }
        self.cursor = 0
        self.cursors = [ 0, 1, 2, 3]
        self.surface = surface
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 20)

    def draw_player_rect( self, place, player ):
        if player == None or player['validated'] == 0:
            self.surface.blit(
                    image(self.menu_elements['player-rect'])[0],
                    (0, place * config['SIZE'][1]/4)
                    )
        else:
            self.surface.blit(
                    image(self.menu_elements[ 'player-rect-selected'
                    ])[0],
                    (0, place * config['SIZE'][1]/4)
                    )

        self.surface.blit(
            self.small_font.render(
                "Select your player with "
                +self.key_list.get('PL' +str(place+1) +'_RIGHT','') +' or '
                +self.key_list.get( 'PL' +str(place+1) +'_LEFT', '')
                +' accept = ' +self.key_list.get( 'PL' +str(place+1) +'_A', '')
                +' back = ' +self.key_list.get( 'PL' +str(place+1) +'_B', ''),
                True,
                pygame.color.Color('#'+self.R +self.V +self.B)
                ),
            (40, place*config['SIZE'][1]/4+config['SIZE'][1]/16)
        )

        if player is not None:
            self.surface.blit(
                    self.characters[player['character']].image,
                    (400, place * config['SIZE'][1]/4+config['SIZE'][1]/8)
                    )

            self.surface.blit(
                    self.font.render(
                        self.characters[
                        player['character']].name,
                        True,
                        pygame.color.Color(
                            '#'\
                            +self.R\
                            +self.V\
                            +self.B
                            )
                        ),
                    (40, place*config['SIZE'][1]/4+config['SIZE'][1]/8)
                    )

    def draw_player_selection(self):
        for index,player in enumerate( self.players ):
            self.draw_player_rect( index, player)

    def draw_menu(self, game):
        self.surface.blit(
                image(self.menu_elements['main_background'])[0],
                (0, 0)
                )
        for index,entry in enumerate(self.entries[self.state]):
            if self.cursor == index:
                self.surface.blit(
                    self.font.render(
                        entry,
                        True,
                        pygame.color.Color('#' +self.R +self.V +self.B)
                        )
                    ,
                    (2*config['SIZE'][0]/5, (index +1 ) *
                    config['SIZE'][1]/(len(self.entries[self.state])+1))
                )

            else:
                self.surface.blit(
                    self.font.render(
                        entry,
                        True,
                        pygame.color.Color("white")
                        )
                    ,(2*config['SIZE'][0]/5, (index +1) *
                    config['SIZE'][1]/(len(self.entries[self.state])+1))
                )

    def draw_level_selection(self):
        level = self.levels[self.level][1]
        zoom=min(
            config['SIZE'][0]/(image(level)[1][2]*1.0),
            config['SIZE'][1]/(image(level)[1][3]*1.0),
            )
        #LOG().log(zoom)
        self.surface.blit(
                image(level,
                    zoom=zoom,
                    )[0],
                (0,0)
                )

        self.surface.blit(
                self.font.render(
                    self.levels[self.level][0],
                    True,
                    pygame.color.Color("white")
                    )
                ,(40, 40)
                )

    def draw_credits(self):
        credits = open('CREDITS').readlines()
        for index,line in enumerate(credits):
            if line[:4] == ' '*4:
                # name of a contributor
                self.surface.blit(
                        self.font.render(
                            line.split('\n')[0],
                            True,
                            pygame.color.Color("white")
                            )
                        ,(config['SIZE'][0]/10, 25*index)
                        )

            else:
                # name of a section
                self.surface.blit(
                        self.font.render(
                            line.split('\n')[0],
                            True,
                            pygame.color.Color("red")
                            )
                        ,(config['SIZE'][0]/10, 25*index)
                        )

    def draw_conf_sound(self):
        self.surface.blit(
                image(self.menu_elements['main_background'])[0],
                (0, 0)
                )
        for index,key in enumerate(self.entries['sound']):
            if key == "save":
                if self.cursor == index:
                    self.surface.blit(
                        self.font.render(
                            key,
                            True,
                            pygame.color.Color('#'+self.R+self.V+self.B)
                            )
                        ,
                        (300, 300)
                    )
                else:
                    self.surface.blit(
                        self.font.render(
                            key,
                            True,
                            pygame.color.Color('white')
                            )
                        ,(300, 300)
                    )
            elif key == "reset":
                if self.cursor == index:
                    self.surface.blit(
                        self.font.render(
                            key,
                            True,
                            pygame.color.Color('#'+self.R+self.V+self.B)
                            )
                            ,(300, 400)
                    )
                else:
                    self.surface.blit(
                        self.font.render(
                            key,
                            True,
                            pygame.color.Color('white')
                            )
                        ,(300, 400)
                    )
            elif key == 'sounds':
                if self.cursor == index:
                    self.surface.blit(
                        self.font.render(
                            ' '.join((key,str(sound_config['SOUND_VOLUME']),'%')),
                            True,
                            pygame.color.Color('#'+self.R+self.V+self.B)
                            )
                        ,(300, 200)
                    )
                else:
                    self.surface.blit(
                        self.font.render(
                            ' '.join((key,str(sound_config['SOUND_VOLUME']),'%')),
                            True,
                            pygame.color.Color('white')
                            )
                        ,(300, 200)
                    )
            elif key == 'music':
                if self.cursor == index:
                    self.surface.blit(
                        self.font.render(
                            ' '.join((key,str(sound_config['MUSIC_VOLUME']),'%')),
                            True,
                            pygame.color.Color('#'+self.R+self.V+self.B)
                            )
                        ,(300, 100)
                    )
                else:
                    self.surface.blit(
                        self.font.render(
                            ' '.join((key,str(sound_config['MUSIC_VOLUME']),'%')),
                            True,
                            pygame.color.Color('white')
                            )
                        ,(300, 100)
                    )
    def draw_conf_keyboard(self, controls):
        self.surface.blit(
                image(self.menu_elements['main_background'])[0],
                (0, 0)
                )
        for index,key in enumerate(self.entries['keyboard']):
            if key == "save":
                if self.cursor == index:
                    self.surface.blit(
                        self.small_font.render(
                            key,
                            True,
                            pygame.color.Color('#'+self.R+self.V+self.B)
                            )
                        ,
                        (300, 400)
                    )
                else:
                    self.surface.blit(
                        self.small_font.render(
                            key,
                            True,
                            pygame.color.Color('white')
                            )
                        ,(300, 400)
                    )
            elif key == "reset":
                if self.cursor == index:
                    self.surface.blit(
                        self.small_font.render(
                            key,
                            True,
                            pygame.color.Color('#'+self.R+self.V+self.B)
                            )
                        ,(400, 400)
                    )
                else:
                    self.surface.blit(
                        self.small_font.render(
                            key,
                            True,
                            pygame.color.Color('white')
                            )
                        ,(400, 400)
                    )
            else:
                if self.cursor == index:
                    if key[0] is not 'P' :
                        drawable_key = key[0] + key[1:].lower ()
                    else :
                        drawable_key = 'Player' + key[2] + '::' + key[4] +\
                                        key[5:].lower ()
                    drawable_hard_key = str(controls.getKeyByAction(key)) [2]

                    if len (str(controls.getKeyByAction(key))) >= 4 :
                        drawable_hard_key += str(controls.getKeyByAction(key))\
                                [3:].lower ()

                    self.surface.blit(
                        self.small_font.render(
                            drawable_key + ' : ' + drawable_hard_key
                            ,
                            True,
                            pygame.color.Color('#'+self.R+self.V+self.B)
                            ),
                        (
                         80 + 200 * int(index / 10),
                         (index % 10) * 20 + 80
                        )
                    )

                else:
                    if key[0] is not 'P' :
                        drawable_key = key[0] + key[1:].lower ()

                    else :
                        drawable_key = 'Player' + key[2] + '::' + key[4]\
                                       + key[5:].lower ()

                    drawable_hard_key = str(controls.getKeyByAction(key)) [2]

                    if len (str(controls.getKeyByAction(key))) >= 4 :
                        drawable_hard_key += str(controls.getKeyByAction(key))\
                                                [3:].lower ()

                    self.surface.blit(
                        self.small_font.render(
                            drawable_key +
                            ' : ' +
                            drawable_hard_key
                            ,
                            True,
                            pygame.color.Color("white")
                            ),
                        (
                         80 + 200 * int(index / 10),
                         (index % 10) * 20 + 80
                        )
                    )

    def launch_game(self, game):
        players = []
        for i in self.players:
            if i is not None:
                players.append(self.characters[i['character']].filename)
            else:
                players.append(None) # there will be no player i :(

        if self.game_type == 'local':
            game = Game(
                self.surface,
                self.levels[self.level][0],
                players
            )

        elif self.game_type == 'network_server':
            game = NetworkServerGame(
                self.surface,
                self.levels[self.level][0],
                players
            )

        elif self.game_type == 'network_client':
            game = NetworkClientGame(
                self.surface,
                self.levels[self.level][0],
                players
            )

        return game

    def update(self, state, game, controls):
        # R, V, B = int(self.R), int(self.V), int(self.B)
        # here we can use any funny method to change the background color.
        R = int(sin(time())*50)+50
        V = int(cos(time())*50)+50
        B = int(sin(time())*50)+50

        self.R, self.V, self.B = (
                str(R).zfill(2),
                str(V).zfill(2),
                str(B).zfill(2)
                )

        self.surface.fill(pygame.Color('#'+self.R+self.V+self.B))

        if self.state == "main" and game != None and game.ended == False:
            self.state = "main_pause"
        if self.state in ('main', 'main_pause', 'configure', 'quit'):
            self.draw_menu(game)
        elif self.state == 'credits':
            self.draw_credits()
        elif self.state  =='players':
            self.draw_player_selection()
        elif self.state == 'levels':
            self.draw_level_selection()
        elif self.state == 'keyboard':
            self.draw_conf_keyboard(controls)
        elif self.state == 'sound':
            self.draw_conf_sound()

        for event in pygame.event.get( USEREVENT ):
            try:
                player = self.players[self.cursors[event.player-1]]
            except AttributeError:
                # dirty FIXME!
                pass

            #normal menus

            if event.key == "QUIT":
                if self.state in ('main', 'main_pause'):
                    self.state = "quit"
                    self.cursor = 0
                else:
                    self.state = "main"
                    self.cursor = 0

            if self.state in (
                                'main',
                                'main_pause',
                                'configure',
                                'keyboard',
                                'sound',
                                'quit'
                             ):
                if event.key == 'DOWN':
                    self.cursor += 1
                elif event.key =='UP':
                    self.cursor -= 1
                elif event.key == "B":
                    if self.state == 'configure':
                        self.state = 'main'
                        self.cursor = 0
                    elif self.state in ('keyboard', 'keyboard'):
                        self.state = 'configure'
                        self.cursor = 0

                elif event.key == 'LEFT':
                    if self.state == 'keyboard':
                        if self.cursor - 10 < 0:
                            self.cursor += (
                                    10 * (len(self.entries['keyboard']) // 10)
                            )
                        else:
                            self.cursor -= 10
                    elif self.state == 'sound':
                        if self.entries['sound'][self.cursor] == "music":
                            sound_config['MUSIC_VOLUME'] = max(
                                    0,
                                    sound_config['MUSIC_VOLUME']-5
                                    )
                        elif self.entries['sound'][self.cursor] == "sounds":
                            sound_config['SOUND_VOLUME'] = max(
                                    0,
                                    sound_config['SOUND_VOLUME']-5
                                    )
                elif event.key == 'RIGHT':
                    if self.state == 'keyboard':
                        if self.cursor + 10 > len(self.entries['keyboard']):
                            self.cursor = self.cursor % 10
                        else:
                            self.cursor += 10
                    elif self.state == 'sound':
                        if self.entries['sound'][self.cursor] == "music":
                            sound_config['MUSIC_VOLUME'] = min(
                                    100,
                                    sound_config['MUSIC_VOLUME']+5
                                    )
                        elif self.entries['sound'][self.cursor] == "sounds":
                            sound_config['SOUND_VOLUME'] = min(
                                    100,
                                    sound_config['SOUND_VOLUME']+5
                                    )
 
                elif event.key in ('VALIDATE','A') and self.state == 'sound':
                    if self.entries['sound'][self.cursor] == 'save':
                        save_sound_conf()
                        self.state = 'configure'
                        self.cursor = 0

                    elif self.entries['sound'][self.cursor] == 'reset':
                        load_sound_config()

                    else:
                        controls.assignKey(
                                self.entries['keyboard'][self.cursor]
                                          )
                elif event.key in ('VALIDATE','A') and self.state == 'keyboard':
                    if self.entries['keyboard'][self.cursor] == 'save':
                        save_keys_conf()
                        self.state = 'configure'
                        self.cursor = 0

                    elif self.entries['keyboard'][self.cursor] == 'reset':
                        load_key_config()

                    else:
                        controls.assignKey(
                                self.entries['keyboard'][self.cursor]
                                          )

                elif event.key in ("A", "VALIDATE"):
                    if self.entries[self.state][self.cursor] == 'Local game':
                        self.game_type = 'local'
                        self.state = 'players'
                        self.cursor = 0

                    elif self.entries[self.state][self.cursor] == 'Resume game':
                        return True, game

                    elif self.entries[self.state][self.cursor] == 'Configure':
                        self.state='configure'
                        self.cursor = 0

                    elif self.entries[self.state][self.cursor] == 'Credits':
                        self.state='credits'
                        self.cursor = 0

                    elif self.entries[self.state][self.cursor] == 'Quit':
                        if config['CONFIRM_EXIT']:
                            self.state = "quit"
                            self.cursor = 0
                        else:
                            pygame.event.post( pygame.event.Event(QUIT) )

                    elif self.entries[self.state][self.cursor] == 'Keyboard':
                        self.state='keyboard'
                        self.cursor = 0

                    elif self.entries[self.state][self.cursor] == 'Sound':
                        self.state='sound'
                        self.cursor = 0

                    elif self.state == "quit":
                        if self.entries[self.state][self.cursor] == "yes":
                            pygame.event.post( pygame.event.Event(QUIT) )
                        elif self.entries[self.state][self.cursor] == "no":
                            self.state = "main"
                            self.cursor = 0

                if self.state in self.entries:
                    self.cursor %= len(self.entries[self.state])

            #PLAYERS menu
            elif self.state == 'players':
                if event.key == "RIGHT":
                    if player == None:
                      player = {'character':1, 'validated':0}
                    elif player['validated'] == 0:
                      player['character'] += 1
                      player['character'] %= len(self.characters)

                if event.key == "LEFT":
                    if player == None:
                      player = {'character':1, 'validated':0}
                    elif player['validated'] == 0:
                      player['character'] -= 1
                      player['character'] %= len(self.characters)

                if event.key == "B":
                    if player is not None and player['validated'] == 1:
                        player['validated'] = 0
                    elif player is not None:
                        player = None
                    else:
                        self.state = "main"
                        self.cursor = 0
                if event.key == "A":
                    if player is not None:
                        player['validated'] = 1
                        #LOG().log(self.players)
                        if len([pls for pls in self.players\
                                    if pls is not None and pls['validated']])>1\
                        and len([pls for pls in self.players\
                                    if pls is not None\
                                    and not pls['validated']]) == 0:
                            self.state = 'levels'
                            self.cursor = 0

                try:
                    self.players[self.cursors[event.player-1]] = player
                except UnboundLocalError:
                    pass

            #LEVELS menu

            elif self.state == 'levels':
                if event.key == "RIGHT":
                    self.level += 1
                    self.level %= len(self.levels)

                elif event.key == "LEFT":
                    self.level -= 1
                    self.level %= len(self.levels)

                elif event.key == "B":
                    self.state = "players"
                    self.cursor = 0

                elif event.key in ("A", "VALIDATE"):
                    self.state = "main"
                    self.cursor = 0
                    game = self.launch_game(game)
                    self.players = [None, None, None, None]
                    return True, game

        return False, None
 
