UltimateSmashFriends
====================

UltimateSmashFriends is a game which aim at creating quick and fun multiplayer
entertainment. With nice 2d bitmap graphics and arcade gameplay we hope to
deliver hours of fun.

The addition of characters and levels is designed to be easy, only bitmaps and
an xml file! Characters support vectors in any animations, collision points
in any animations, adding event to game in any animations, the
characters behaviour is very flexible, It's also easy to code a particular
event if you are a developper. We hope this will encourage collaborative
creation of original characters and levels.  Please see the wiki for help on
characters/maps creation.

http://usf.tuxfamily.org/wiki/Documentation

How to play
===========

To play you need python (>=2.4) and pygame(>=1.7) (older version not tested).
If you use python 2.4 you must install python-elementtree. Python 3 is not
currently supported.

On debian/ubuntu install python-pygame and if you are using python2.4:
python-elementtree.
On windows please install python 2.5 from http://python.org and pygame
1.7 from http://pygame.org.

Just launch ultimate-smash-friends.py, by double clicking it or from a shell
with ./ultimate-smash-friends.py in the ultimate smash friends path. Then use
the menu to lauch a game.

You can directly launch a game by passing level and player parameters, separate
players name by a comma, like this:

./ultimate-smash-friends --level rizland --players xeon,blob

(--level can be abreviated as -l and --players as -p)
you can test the Artificial intelligence (in very first steps of developpement)
by adding "AI" before the name of a player, e.g:

./ultimate-smash-friends --level rizland --players blob,AIxeon

like this the second player will be an AI player.

Controls
========
Keys configuration are stored in the user.cfg file.

Each player has 4 direction keys and two action keys refered here as A and B
plus a SHIELD key.

Menu
====
the escape key can be used to toggle the menu. Launching a new game will cancel
any current game.

Game
====
each character has 7 keys: 4 directional and 2 action keys plus the SHIELD key,
the actions keys are further referenced as A and B. You can use A and B in
combination with directions keys to make more complexe attacks (combos).

the SHIELD key is used to protect the player, but it can't move while protected.

Use the escape key to access the menu in game.

How to win
==========

Rules are simple, when you hit someone, his percents raise, and is projected
every time a little more far, the aim is to beat the enemies out of the map, you
have 3 lives.

Enjoy :)

Bugs
====

Please send reports, suggests or patchs to:
https://bugs.launchpad.net/ultimate-smash-friends

last update: Sun, 10 Apr 2011 10:53:29 +0200
