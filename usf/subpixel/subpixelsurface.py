import pygame
from pygame.locals import *
from math import floor

# Try to import Numpy, or Numeric
try:    
    import numpy as Numeric    
    BYTE = "u1"
    DWORD = "u4"
    
except ImportError:    
    try:
        import Numeric
    except ImportError, e:
        print "Requires NumPy or Numeric!"
        raise e
    BYTE = Numeric.UnsignedInt8
    DWORD = Numeric.Int32
    

class SubPixelSurface(object):
    
    
    def __init__(self, surface, x_level=3, y_level=None):
        
        """Creates a sub pixel surface object.
        
        surface -- A PyGame surface
        x_level -- Number of sub-pixel levels in x
        y_level -- Number of sub-pixel levels in y (same as x if omited)        
        
        """
                
        self.x_level = x_level
        self.y_level = y_level or x_level
        
        w, h = surface.get_size()
        ow, oh = w, h        
        w += 2
        h += 2        
                
        surf_array_rgb = Numeric.zeros((w, h, 3), BYTE)
        surf_array_rgb[1:ow+1:, 1:oh+1:, ::] = pygame.surfarray.array3d(surface)
        surf_array_a = Numeric.zeros((w, h), BYTE)
        surf_array_a[1:ow+1:, 1:oh+1:] = pygame.surfarray.array_alpha(surface)
                
        surf_array_rgb[0,::] = surf_array_rgb[1,::]                
        surf_array_rgb[::,0] = surf_array_rgb[::,1]        
        surf_array_rgb[w-1,::] = surf_array_rgb[w-2,::]                
        surf_array_rgb[::,h-1] = surf_array_rgb[::,h-2]
        
        s = Numeric.zeros(surf_array_rgb.shape[:2]+(4,), DWORD)
        s[::-1, ::, :3] = surf_array_rgb
        s[::-1, ::, 3] = surf_array_a
        
        x_steps = [float(n) / self.x_level for n in xrange(self.x_level)]
        y_steps = [float(n) / self.y_level for n in xrange(self.y_level)]
        
        self.surfaces = []
        for frac_y in y_steps:
            row = []
            self.surfaces.append(row)
            for frac_x in x_steps:
                row.append( SubPixelSurface._generate(s, frac_x, frac_y) )
                
        
    @staticmethod
    def _generate(s, frac_x, frac_y):        
        
        frac_x, frac_y = frac_y, frac_x
        frac_x = 1. - frac_x        
        
        sa = int( (1.-frac_x) * (1.-frac_y) * 255. ) 
        sb = int( (1.-frac_x) * frac_y * 255. )
        sc = int( frac_x * (1.-frac_y) * 255. )
        sd = int( (frac_x * frac_y) * 255. )
        
        a = s[ :-1:, :-1:] * sa
        b = s[ 1::,  :-1:] * sb
        c = s[ :-1:, 1:: ] * sc
        d = s[ 1::,  1:: ] * sd
        
        a += b
        a += c
        a += d
        a >>= 8
        
        rgba_data = a.astype(BYTE).tostring()
        pygame_surface = pygame.image.fromstring(rgba_data, a.shape[:2][::-1], "RGBA")
        pygame_surface = pygame.transform.rotate(pygame_surface, 270)
        
        return pygame_surface
        
        
    def at(self, x, y):
        
        """Gets a sub-pixel surface for a given coordinate.
        
        x -- X coordinate
        y -- Y coordinate
        
        """
        
        surf_x = int( (x - floor(x)) * self.x_level )
        surf_y = int( (y - floor(y)) * self.y_level )
        
        return self.surfaces[surf_y][surf_x]
