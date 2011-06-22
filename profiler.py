#!/usr/bin/env python
import cProfile
from usf import main
import sys


def main_():
    sys.argv = ['./ultimate-smash-friends', '-p', 'AIblob,AIxeon', '-l',
            'rizland']
    m = main.Main()
    m.init()
    cProfile.runctx("m.run()", globals(), locals(), filename="usf.profile")


if __name__ == '__main__':
    main_()

