#!/usr/bin/env python2

from usf.timed_event import EVENT_NAMES, TimedEvent

class test(TimedEvent):
    def __init__(self, *args, **kwargs):
        super(test, self).__init__(*args, **kwargs)

    def condition(self, *args, **kwargs):
        return True

    def execute(self, deltatime):
        pass

EVENT_NAMES['CaveTestEvent'] = test
