===UltimateSmashFriends:===

UltimateSmashFriends is a game which aim at creating quick and fun multiplayer
entertainment. With nice 2d bitmap graphics and arcade gameplay we hope to
deliver hours of fun.

The addition of characters is designed to be easy, only bitmaps of animations and
an xml file!  Levels are even simpler: three bitmap (png): background, level and
forground, and a "map" file (flat file for simple levels, xml for more
possibilities). Characters support vectors in any animations, collision points
in any animations, adding event to game in any animations, the characters
behaviour is very flexible, It's also easy to code a particular event if you
are a developper. We hope this will encourage collaborative creation of
original characters and levels.  Please see the wiki for help on
characters/maps creation.

==How to play:==

To play you need python (>=2.4) and pygame(>=1.7) (older version not tested).
If you use python 2.4 you must install python-elementtree. Python 3 is not
currently supported.

On debian/ubuntu install python-pygame and if you are using python2.4:
python-elementtree.
On windows please install python 2.5 from http://python.org and pygame
1.7 from http://pygame.org.

Just launch ultimate-smash-friends.py, by double clicking it or from a shell
with ./ultimate-smash-friends.py in the ultimate smash friends path. Then use
the menu to lauch a game (see controls section).

You can directly launch a game by passing level and player parameters, separate
players name by a comma, like this:

./ultimate-smash-friends --level maryoland --players stick-tiny,boogy-t

(--level can be abreviated as -l and --players as -p)
you can test the Artificial intelligence (in very first steps of developpement)
by adding "AI" before the name of a player, e.g:

./ultimate-smash-friends --level maryoland --players stick-tiny,AIboogy-t

like this the second player will be an AI player.

==Controls==
Keys configuration are stored in the UltimateSmashFriends.cfg file. See
http://code.google.com/p/ultimate-smash-friends/w/list for reference.

Each player has 4 direction keys and two action keys refered here as A and B.

Menu:
Use the left-right keys of your player to select your character, the 'A' key to
go to level selection (when all player are happy with their selected character).
Use the left-right key to select a level, you can use the 'B' key of your player
to go back to character selection). Then use the 'A' key to launch the game.

the escape key can be used to toggle the menu. Launching a new game will cancel
any current game.

Game:
each character has 6 keys: 4 directional and 2 action keys, the actions keys
are further referenced as A and B. You can use A and B in combination with
directions keys to make more complexe attacks (combos).

Use the escape key to access the menu in game.

==How to win:== 
Rules are simples, when you hit someone, his percents raise, and is projected
every time a little more far, the aim is to beat the enemies out of the map, you
have 3 lives.

Enjoy :)

==Bugs:==
Please send reports, suggests or patchs to:
http://code.google.com/p/ultimate-smash-friends/issues/list

Known bugs are:
 - collisions bugs, you may get through a piece of level or be moved a little
far of your location.
 - animation timing bug, depending on your computer, you might get different
animation timings, this is a high priority bug, any help very welcome.

last update: Sun, 15 Nov 2009 18:25:30 +0100
