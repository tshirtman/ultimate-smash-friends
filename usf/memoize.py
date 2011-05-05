#!/usr/bin/env python

def memoize(function):
    """
    Any function decorated with memoize will cache it's results and send them
    directly when called with same parameters as before, without calling the
    actual code, please only use with functions which result depend only of
    parameters (not time, state of the game or such).
    """
    cache = {}

    def decorated_function(*args, **kwargs):
        params = (args)+tuple(zip(kwargs.keys(),kwargs.values()))
        try:
            return cache[params]
        except:
            val = function(*args, **kwargs)
            try:
                cache[params] = val
            except TypeError, e:
                print e, params
            return val
    return decorated_function

