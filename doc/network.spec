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

    from server to client:

in game mode:
    from client to server:

    from server to client:

