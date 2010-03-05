""" Enumerators for use throughout ulitmate-smash-friends.

    This module is provided simply for convenience. It allows named constants
    to be used in place of numbers when referencing items in a list.
"""

""" collision points
     7. .0   counted clockwise and starting from the upper right one
    6.   .1  (in fact it's the opposite but the screen is (0,0) at the
    5.   .2  top left, what actualy means right or left is not important
     4. .3   as long as you stay consistent, I hope I do :P).
 """
(TOP_RIGHT, UPPER_RIGHT, LOWER_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT, LOWER_LEFT,
 UPPER_LEFT, TOP_LEFT) = range(8)

