#!/usr/bin/env python
from timed_event import event_names
import itertools

class EventManager(object):
    """
    This simple module takes care of the state of events in the game

    """
    def __init__(self):
        self.events = set()
        self.to_add = set()
        self.to_remove = set()

    def update(self, deltatime, gametime):
        """
        Called every frame, update every instancied event.

        """
        self.events.update(self.to_add)
        self.to_add.clear()

        for e in self.events:
            if not e.update(deltatime, gametime):
                self.to_remove.add(e)

        self.events.difference_update(self.to_remove)
        self.to_remove.clear()

    def add_event(self, name, *args, **kwargs):
        self.to_add.add(event_names[name](self, *args, **kwargs))

    def get_events(self, cls=None, params=dict()):
        ''' return events filtered by name and target parameters, None mean no
        filter on this parameter
        '''

        return itertools.ifilter(
                lambda event:
                (cls is None or event.__class__==cls) and
                (reduce(
                    lambda x,y: x and y,
                    [event.params[i] == params[i] for i in event.params])
                    ),
                self.events)

