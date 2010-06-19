#!/usr/bin/env python
from usf import loaders
import pygame
pygame.display.set_mode((800, 600))
a = loaders.image('data/gui/icon.png')[1]
import test_load2 as b
print a == b.b
