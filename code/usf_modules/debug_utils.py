import pygame

def draw_rect(surface, rect, color=pygame.Color('white')):
    surface.fill(color, pygame.Rect(rect))


class LOG (object):
    """
    Provide a simple log system, with optional alternative destination (default to stdout),
    and optional filter to messages by level.
    """
    def __init__(self, out = 'stdout', min_level = 1):
        """
        if out is defined and different of 'stdout' then it is considered as a
        wirtable file object.
        if min_level is defined, messages of an strictly inferior level won't be
        displayed. Please try to use only level 1, 2 and 3.
        """
        self.out = out
        self.min_level = min_level
        self.severities = ['info: ','warning: ', 'BAD: ']

    def log(self, message, level = 1):
        """
        Message must be a printable object.
        Set the level according to severity (1=info, 2=possible issue, 3=BAD).
        """
        if level >= self.min_level:
            if self.out == 'stdout':
                print self.severities[level-1] + str(message)
            else:
                self.out.write(self.severity[level-1] + str(message))

