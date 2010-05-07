################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>
#
# This file is part of UltimateSmashFriends
#
# UltimateSmashFriends is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UltimateSmashFriends is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.
# ##############################################################################

from pygame import mixer
import os
import time
import random
import logging

from config import Config
import loaders

config = Config()

class Music (object):
    """
    This class take care of the background music in menus and games, it load the
    "playlist" and change the music in random order.

    """
    def __init__(self):
        """
        We load the playlist.

        """
        self.previous_state = None
        self.playlists = {}
        self.music_volume = config.audio['MUSIC_VOLUME']

        for plist in ['menu','game','credits','victory']:
            self.playlists[plist] = [
                                    os.path.join(
                                    config.sys_data_dir,
                                    'music',
                                    'ogg',file)
                                for file
                                in os.listdir(os.path.join(
                                    config.sys_data_dir,
                                    'music',
                                    'ogg'))\
                                if plist in file
                            ]
        self.current_track = None
        self.time_begin = 0

    def update(self, state, params={}):
        """
        This check various parameters (state of game, time since last music
        change), and may choose to change music (with a fading) if it seems
        necessary.

        """
        if self.current_track is not None:
            if config.audio['MUSIC_VOLUME'] != self.music_volume:
                self.current_track.set_volume(config.audio['MUSIC_VOLUME']/100.0)
        else:
            if state != self.previous_state:
                self.change_music(self.playlists[state])
            elif self.current_track and time.time() - self.time_begin + 4 > self.current_track.get_length():
                self.change_music(self.playlists[state])

        self.music_volume = config.audio['MUSIC_VOLUME']
        self.previous_state = state

    def change_music(self, music, fading=True):
        """
        This change the currently played music. With an optional fading.

        """
        #logging.debug('launching music: '+str(music.get_length()))
        self.time_begin = time.time()
        if fading == True:
            if self.current_track != None:
                self.current_track.fadeout(3000)
            self.current_track = loaders.track(random.choice(music))
            if self.current_track:
                self.current_track.set_volume(config.audio['MUSIC_VOLUME']/100.0)
                self.current_track.play(fade_ms=3000)
        else:
            self.current_track = music
            self.current_track.play()

