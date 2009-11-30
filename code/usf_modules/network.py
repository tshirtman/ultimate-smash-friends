################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
#                                                                              #
# This file is part of ultimate-smash-friends                                  #
#                                                                              #
# ultimate-smash-friends is free software: you can redistribute it and/or      #
# modify it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or (at your   #
# option) any later version.                                                   #
#                                                                              #
# ultimate-smash-friends is distributed in the hope that it will be useful, but#
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or#
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# You should have received a copy of the GNU General Public License along with #
# ultimate-smash-friends.  If not, see <http://www.gnu.org/licenses/>.         #
################################################################################

# standart imports
import socket
from threading import Thread, Semaphore
from time import sleep, time

# my imports
from config import config
from debug_utils import LOG

def test_client():
    a=Client()
    b=Client()
    a.connect(nick='1', character='stick-tiny', votemap='baselevel')
    b.connect(nick='2', character='stick-red', votemap='maryoland')

class NetworkError (RuntimeError):
    pass

key_dict = {
                'U': 'UP',
                'D': 'DOWN',
                'L': 'LEFT',
                'R': 'RIGHT',
                'A': 'A',
                'B': 'B'
           }

MSGLEN = 2

def server_thread(client_socket, server, num, game_instance):
    """
    This fonction is called by the serverside to deal with a connected client,
    it will translate recieved messages to the game object.

    """
    prec_time = time()
    while not server.quit:
        # 10 network updates per seconds is already a lot.
        while time() < prec_time + 0.10:
            sleep(.02)
        prec_time = time()
        # we use Fixed Lenght (2 chars) messages, as we know this is always a
        # player number on the client + a key (A, B, U=UP, D=Down, L=Left,
        # R=Right)
        msg = ''
        while len(msg) < MSGLEN:
            chunk = client_socket.recv(MSGLEN - len(msg))
            if chunk == '':
                LOG().log('error client, link broken')
                LOG().log(msg)
                server.quit = True
                raise NetworkError
            else:
                msg += chunk
        if msg == 'AU' and game_instance.accepting:
            auth_msg = ''
            while True:
                chunk = client_socket.recv(5)
                if chunk == '':
                    LOG().log('error client, link broken')
                    LOG().log(msg)
                    raise NetworkError
                else:
                    msg += chunk

                if msg[-1] == '':
                    player = server.new_player_from_string(msg[2:])
                    server.players[num] = (
                                            player['nick']+
                                            ','+
                                            os.sep.join((
                                                           'characters',
                                                           player['character']
                                                        ))
                                          )

                    server.votemap[num]=player['votemap']

                    break;

        else:
            key = 'PL' + str(num * 10 + int(msg[0])) + '_'
            # FIXME: maybe save this dict somewhere as a class property.
            key += key_dict[msg[1]]

            # As messages is a shared resource we need to lock it.
            server.lock.acquire()
            server.messages.append(key)
            server.lock.release()

class Client(object):
    """
    Using this class, a client will send any input event from the player on this
    machine, and will recieve an acknowledgment in response.

    """
    def __init__(self, sock=None):
        self.lock = Semaphore()
        self.messages = ''
        if sock is None:
            self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            LOG().log('client socket created')
        else:
            self.socket = sock

    def connect(self, host="127.0.0.1", port=config['NETWORK_PORT'], nick='',
                character='stick-tiny', votemap='', listening=True):
        """
        This attempt to connect our client socket to the server socket and
        send all information to server, about who we are and who we play.
        (there may be more than one player an a client and the server need to
        known what caracters theses players plays.

        this fonction accept a dict of values like.
        {'nick': ..., 'character':..., 'votemap': ...}

        the stream sent is terminated with a ^D character ().


        """
        LOG().log('connecting to game server')
        try:
            self.socket.connect((host,port))
        except:
            raise
        LOG().log('success')
        pass

        msg = ('AU'+'N'+(nick or character)+','+
                    'C'+character+','+
                    'M'+votemap+
                    'L'+listening+
                    '')

        self.socket.sendall(msg)

    def send(self, key, action='down'):
        """
        This add a key event to be sent to the game server. Action can be up or
        down, down if player pushed the key, up if he released it.

        """
        self.lock.acquire()
        LOG().log('sent key '+key+' to game server')
        self.messages += key
        self.lock.release()

    def close(self):
        """
        Close the socket connection.

        """
        self.socket.close()

    def update(self):
        """
        Send all the pending messages to the server.

        """
        self.lock.acquire()
        self.socket.sendall(self.messages)
        self.messages = ''
        self.lock.release()

    def recieve(self):
        """
        Recieve all the data from the server necessary to update our display.

        """
        LOG().log('recieve new data from server')
        while True:
            chunk = self.socket.recv(5)
            if chunk == '':
                LOG().log('error server, link broken')
                raise NetworkError
            else:
                msg += chunk

                if msg[-1] == '':
                    break
        # parse msg to extract infos about level and characters.
        # IN is for INIT: the game is beginning
        if msg[:2] == 'IN':
            infos = msg[2:].split(',')
            for i in infos:
                k,v=i.split(':')
                if k == 'LE': # LEVEL
                    self.level = v
                elif k == 'PL': # PLAYERS
                    self.players.append(v)

        # UP is for UPDATE this is an update of the game
        elif msg[:2] == 'UP':
            self.players = msg[2:].split(';')

        return

class Server(object):
    """
    This class maintain a server socket that will listen for client connections
    and will create client socket to deal with client connections.

    """
    def __init__(self, game_instance=None, sock=None):
        self.quit = False
        self.game_instance = game_instance
        if sock is None:
            self.lock = Semaphore()
            self.serversocket = socket.socket(
                                                socket.AF_INET,
                                                socket.SOCK_STREAM
                                             )
            self.serversocket.bind(
                                    (
                                        self.serversocket.getsockname()[0],
                                        config['NETWORK_PORT']
                                    )
                                  )

            self.serversocket.listen(5)
            self.clients = []
            self.messages = []
        else:
            self.socket = socket

        self.listen()
    def __del__(self):
        """
        We wait for the thread to die.

        """
        self.quit = True
        time.sleep(1000)

    def listen(self, clients=[]):
        """
        Launch the server connection socket listener.

        """
        Thread( target = self.listen_function, args=(self.game_instance,) ).start()

    def close(self):
        self.quit = True

    def new_player_from_string(self, data):
        """
        Data is a stream sent by the client, this function return a dict of
        params to create the client character.

        """
        params = data[:-1].split(',')
        for p in params:
            if p[0] == 'N':
                nick = p[1:]

            if p[0] == 'C':
                character = p[1:]

            if p[0] == 'M':
                votemap = p[1:]

        return {'nick': nick, 'character': character, 'votemap': votemap}

    def listen_function(self, game_instance):
        """
        Listen for new connexion, and fork them to threads with their socket.

        """
        num = 0
        self.players = []
        self.votemap = []
        while num < self.game_instance.num_players:
            (clientsocket, address) = self.serversocket.accept()
            LOG().log('new client accepted :D')
            self.players.append([])
            self.votemap.append([])
            Thread(target=server_thread, args=(clientsocket, self, num, game_instance)).start()
            num += 1
            LOG().log('client threaded away ;)')

        sleep(.5) # FIXME: need to be sure that all informations are recieved
        LOG().log("enougth players, launching game")
        list_level = [(self.votemap.count(a), a) for a in set(self.votemap)]
        list_level.sort(reverse=True)
        LOG().log(self.players)
        self.game_instance.begin(players_=self.players, level=list_level[0][1])

    def fetch(self):
        """
        Get the next key event sent by a player.

        """
        if len(self.messages) == 0:
            yield None
        else:
            self.lock.acquire()
            event = self.messages.pop(0)
            self.lock.release()
            yield event

