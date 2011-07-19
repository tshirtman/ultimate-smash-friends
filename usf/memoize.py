#!/usr/bin/env python
################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
#                                                                              #
# This file is part of UltimateSmashFriends                                    #
#                                                                              #
# UltimateSmashFriends is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation, either version 3 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# UltimateSmashFriends is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.#
################################################################################
'''
This module provide simple implementation of the memoize pattern, implemented
as a decorator.

usage:

@memoize
def my_determinist_pure_function(*args, **kwargs):
    do stuff

my_determinist_pure_function(some_params) # first call with those params, slow
...

my_determinist_pure_function(some_params) # return result imediatly

...

my_determinist_pure_function(other_params) # slow again, because new params

...

my_determinist_pure_function(other_params) # return result immediatly


of course, if params/results are memory huger, or the function is called with
lot of different params, that will eat some memory, but if you often need the
same result, that can bring you a lot of speed.

'''
from functools import wraps

def memoize(function):
    """
    Any function decorated with memoize will cache it's results and send them
    directly when called with same parameters as before, without calling the
    actual code, please only use with functions which result depend only of
    parameters (not time, state of the game or such).
    """
    cache = {}

    @wraps(function)
    def decorated_function(*args, **kwargs):
        """ this docstring will be replaced by function's one when decorator is
        used
        """
        params = (args)+tuple(zip(kwargs.keys(), kwargs.values()))
        try:
            return cache[params]
        except KeyError:
            val = function(*args, **kwargs)
            try:
                cache[params] = val
            except TypeError, e:
                print e, params
            return val

    decorated_function.__name__ = function.__name__
    decorated_function.__doc__ = function.__doc__

    return decorated_function

