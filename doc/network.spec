this document try to describe the way network game should work.

Server part:
the server part consist of a minimal socket server, waiting for client
connection, and allowing those clients to send command, commands are:

-creation of a game: this cause the creation of a game room. This is not yet a
game, but it has a name and an (initialy empty) list of player. The player who
create a game room manage it.
-join of a game: a player can set itself connected to a game room (only one at
a time), but more than one player on each client should be able to connect to
the same game. 
-chat: server wide or to the game in the room the player is connected.
-vote for the map used in the game to be attached to the gameroom.
-set the game character of the player.
-set the name of the player.

server configuration is done by a config file, that define max number of
gameroom, admin password (allowing restart of server, closing of gameroom, kick
of any player...), and if the server declare itself to an internet main index.

Client part:
the client part of the game is a graphical application: allowing to discover
server in the lan, or using an internet index, and to connect with one of them,
declare any player wanting to play on the connected server, and start a display
game when the server start it.

When a client is connected to a running game, the client send a message
containing a timestamp (for ping data) and every keystrock done during the frame,
to the server, eanch keystrock being converted to a simple format indicating
the player and the mapping of the key.  Every frame the server send a stream to
all the players, containing which entities are to display, and their state,
(position and current animation frame).


data stream specification:
connexion:
    the server listen on port 8421 by default, the client connect and get a
    stream socket, it's in "no room" mode.

in "no room" mode:
    /nick player_num name: change player name of player_num of this connexion
    to "name"
    /join room: the connexion is now bound to room the room is created if it
    did not exist
    /admin password: if the password is the one defined in the configuration,
    connected client is now able to use admin commands (which work in every
    mods)

admin commands:
    /kick player_name: close the player connection

in "room" mode:
    from client to server:
    /leave: leave the room
    /ready number: the player "number" is ready to play
    /nick number nick: the player "numer" change his nick to nick
    /character character: the player choose the named character
    /msg num_player msg: player send the message msg to the room.

    from server to client:
    /time timestamp: the server send a timestamp too client for synchronisation
    purpose
    /msg nick msg: the message msg was sent by player nick.
    /start timestamp level [list]: game start at timestamp with level and
    players [list]
    /level l: level l is currently selected

in game mode:
    from client to server:
    /key p k: player p pushed his key k ('UP', 'DOWN', 'LEFT', 'RIGHT', 'A',
    'B')
    /msg p m: player p sent message

    from server to client:
    /world [list]: a list of entities positions 
    /end p: the game is finished with p being the winner, or None if it's a
    draw.
    /msg nick msg: the player nick sent message msg
