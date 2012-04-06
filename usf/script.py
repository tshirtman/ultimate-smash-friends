################################################################################
# copyright 2012 Thomas Glamsch <thomas-glamsch@gmx.de>                        #
#                                                                              #
# This file is part of Ultimate Smash Friends                                  #
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
This module provides utilities for securely evaluating python scripts from
user-generated content.
'''

import __builtin__
import itertools
import logging
import math
import random



class _Sandbox(object):
    """
    A container class which holds a dictionary with secure global names for
    script evaluation. This should not be accessed from outside this module.
    """
    pass

# Extend this list to blacklist more builtins.
_Sandbox._builtins_blacklist = [
    'compile',
    'eval',
    'execfile',
    'file',
    'help',
    'id',
    'input',
    'memoryview',
    'open',
    'print',
    'raw_input',
    'reload',
    '__import__']

# That's pretty ugly. If you know a better way to generate a dict containing
# all non-blacklisted builtins, go ahead and change it.
_Sandbox._builtins = dict(
    itertools.izip(
        itertools.ifilter(
            lambda x: hasattr(vars(__builtin__)[x], '__name__') and x not in _Sandbox._builtins_blacklist,
            vars(__builtin__).iterkeys()),
        itertools.ifilter(
            lambda x: hasattr(x, '__name__') and x.__name__ not in _Sandbox._builtins_blacklist,
            vars(__builtin__).itervalues())))

# These are the modules which may be used in user-generated scripts.
# Extend this dict to allow more modules to be used.
_Sandbox.globals = {
    '__builtins__': _Sandbox._builtins,
    'math'        : math,
    'random'      : random}

def secure_eval(expression):
    """
    Securely evaluate a user-generated script.
    To achieve a certain level of security, all builtin functions which
    allow access to arbitrary locations or which can cause problems in any
    other way have been blacklisted. Furthermore, the access to modules from
    the Python standard library has been restricted to math and random.
    """
    try:
        return eval(expression, _Sandbox.globals)
    except Exception:
        logging.error('Could not evaluate expression \'%s\'.' % expression)
