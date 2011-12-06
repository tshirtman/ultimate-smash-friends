from time import sleep
import itertools
import threading
import gtk

from gettext import gettext as _

# Initializing the gtk's thread engine
gtk.gdk.threads_init()


class Frame(threading.Thread):
    #Thread event, stops the thread if it is set.
    stopthread = threading.Event()
    frames = None
    img = None
    path = ''

    def run(self):
        """Run method, this is the code that runs while thread is alive."""

        # While the stopthread event isn't setted, the thread keeps going on
        while not self.stopthread.isSet():
            # Acquiring the gtk global mutex
            gtk.gdk.threads_enter()
            n_frame = self.frames.next()
            print 'frame...', self.path + n_frame[1]
            self.img.set_from_file(self.path + n_frame[1])
            # Releasing the gtk global mutex
            gtk.gdk.threads_leave()
            sleep(n_frame[0])

    def stop(self):
        """Stop method, sets the event to terminate the thread's main loop"""
        self.stopthread.set()

    def restart(self):
        if self.stopthread.isSet():
            self.stopthread.clear()
        # Re-Initializing the gtk's thread engine
        gtk.gdk.threads_init()
        self.start()


class RemoteControl():
    def __init__(self, img, project_path, cp):
        self.img = img
        self.project_path = project_path
        self.cp = cp
        self.frames = self.cp.get_frames()

        self.frame = Frame()
        self.frame.img = self.img
        self.frame.path = self.project_path
        self.frame.frames = itertools.cycle(self.frames)
        self.frame.frames.next()

    def __del__(self):
        if self.frame.isAlive():
            self.frame.stop()

    def stop(self, action):
        if self.frame.isAlive():
            self.frame.stop()
            action.set_stock_id(gtk.STOCK_MEDIA_PLAY)
            action.set_tooltip(_('Play animation'))
        self.frame = Frame()
        self.frame.img = self.img
        self.frame.path = self.project_path
        self.frame.frames = itertools.cycle(self.frames)

    def begin(self, action):
        frames = itertools.cycle(self.frames)
        self.img.set_from_file(self.project_path + frames.next()[1])
        self.frame.frames = frames

    def previous(self, action):
        iteration = len(self.frames)
        frames = self.frame.frames
        while iteration > 0:
            frames.next()
            iteration -= 1
        self.img.set_from_file(
            self.project_path + frames.next()[1]
            )

    def play(self, action):
        action.set_stock_id(gtk.STOCK_MEDIA_STOP)
        action.set_tooltip(_('Stop animation'))
        iter_frames = self.frame.frames
        if self.frame.isAlive():
            self.stop(action)
            self.frame.frames = iter_frames
            return
        self.frame.frames = itertools.cycle(self.frames)
        self.frame.path = self.project_path
        self.frame.restart()

    def next(self, action):
        self.img.set_from_file(
            self.project_path + self.frame.frames.next()[1]
            )

    def end(self, action):
        iteration = len(self.frames) - 1
        frames = itertools.cycle(self.frames)
        while iteration > 0:
            frames.next()
            iteration -= 1
        self.img.set_from_file(self.project_path + frames.next()[1])
        self.frame.frames = frames