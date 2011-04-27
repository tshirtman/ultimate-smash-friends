UltimateSmashFriends
====================

UltimateSmashFriends is a game which aim at creating quick and fun multiplayer
entertainment. With nice 2d bitmap graphics and arcade gameplay we hope to
deliver hours of fun.

How to install
==============

see INSTALL file if you have not already installed the game.


Launching the game
==================

Just launch ultimate-smash-friends.py, by double clicking it or from a shell
with ./ultimate-smash-friends.py in the ultimate smash friends path. Then use
the menu to lauch a game.

You can directly launch a game by passing level and player parameters, separate
players name by a comma, like this:

./ultimate-smash-friends --level rizland --players xeon,blob

(--level can be abreviated as -l and --players as -p)
you can add an artificial intelligence player by adding "AI" before the name of
the character, e.g:

./ultimate-smash-friends --level rizland --players blob,AIxeon

like this the second player will be an AI player.


Controls
========

Keys configuration are stored in the user.cfg file and can be changed from the
options menu of the game

Each player has 4 direction keys and two action keys referred here as A and B
plus a SHIELD key.

Basic actions:

  * The LEFT and RIGHT keys allow to walk
  * The UP key allow to jump
  * The DOWN key allow to pick an item
  * The A key trigger a kick
  * The B key trigger a simple hit
  * The SHIELD key set the shield on until the key is released of the shield is
  exhausted

Combined actions:
  * During a jump, the UP key will trigger a second jump
  * When DOWN has been pushed, a LEFT or RIGHT push will trigger a roll
  * When B is pushed just after a move in any direction, that will trigger a
  smash in that direction
  * When A is pushed after DOWN, a special attack is triggered, if available
  * When DOWN is pushed two times, and then A is pushed, another special attack
  is triggered, if available


Menu
====

The escape key can be used to toggle the menu. Launching a new game will cancel
any current game.


Game
====

Each character has 7 keys: 4 directional and 2 action keys plus the SHIELD key,
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


Contribute
==========

The addition of characters and levels is designed to be easy, only bitmaps and
an xml file! Characters support vectors in any animations, collision points
in any animations, adding event to game in any animations, the
characters behaviour is very flexible, It's also easy to code a particular
event if you are a developper. We hope this will encourage collaborative
creation of original characters and levels.  Please see the wiki for help on
characters/maps creation.

http://usf.tuxfamily.org/wiki/Documentation


Bugs
====

Please send reports, suggests or patchs to:
https://bugs.launchpad.net/ultimate-smash-friends

last update: Wed, 27 Apr 2011 18:45:51 +0200
