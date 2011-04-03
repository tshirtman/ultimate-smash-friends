#!/usr/bin/env python
from timed_event import event_names
import itertools

class EventManager(object):
    """
    This simple module takes care of the state of events in the game

    """
    def __init__(self):
        self.events = list()

    def backup(self):
        return tuple((self.events[:], (e.backup() for e in self.events)))

    def restore(self, backup):
        self.events = backup[0]
        for e,b in zip(self.events, backup[1]):
            e.restore(b)

    def update(self, deltatime, gametime):
        """
        Called every frame, update every instancied event.

        """
        for e in self.events:
            e.update(deltatime, gametime)
        [e.del_() for e in self.events if e.done]
        self.events = filter(lambda x: not x.done, self.events)

    def add_event(self, name, *args, **kwargs):
        self.events.append(event_names[name](self, *args, **kwargs))

    def get_events(self, cls=None, params=dict()):
        ''' return events filtered by name and target parameters, None mean no
        filter on this parameter
        '''

        return itertools.ifilter(
                lambda event:
                (cls is None or event.__class__==cls) and
                (reduce(
                    lambda x,y: x and y,
                    [(i in event.params and event.params[i] == params[i]) for i in params])
                    ),
                self.events)

