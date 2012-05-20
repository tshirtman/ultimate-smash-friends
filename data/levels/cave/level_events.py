#!/usr/bin/env python

from usf.timed_event import TimedEvent, EVENT_NAMES


class test(TimedEvent):
    def __init__(self, *args, **kwargs):
        super(test, self).__init__(*args, **kwargs)

    def condition(self, *args, **kwargs):
        return True

    def execute(self, deltatime):
        pass


def install():
    EVENT_NAMES['CaveTestEvent'] = test
