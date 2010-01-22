import pygame

def draw_rect(surface, rect, color=pygame.Color('white')):
    surface.fill(color, pygame.Rect(rect))

