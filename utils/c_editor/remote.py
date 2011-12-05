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
    frames = []
    img = None
    path = ''

    def run(self):
        """Run method, this is the code that runs while thread is alive."""

        # While the stopthread event isn't setted, the thread keeps going on
        while not self.stopthread.isSet():
            # Acquiring the gtk global mutex
            gtk.gdk.threads_enter()
            n_frame = self.frames.next()
            print 'frame...', self.path  + n_frame[1]
            self.img.set_from_file(self.path  + n_frame[1])
            # Releasing the gtk global mutex
            gtk.gdk.threads_leave()
            sleep(n_frame[0])

    def stop(self):
        """Stop method, sets the event to terminate the thread's main loop"""
        self.stopthread.set()

    def restart(self):
        print 'restart'
        if self.stopthread.isSet():
            print 're'
            self.stopthread.clear()
        print 'start'
        # Re-Initializing the gtk's thread engine
        gtk.gdk.threads_init()
        self.start()

class RemoteControl():
    def __init__(self, img, project_path, cp):
        self.img = img
        self.project_path = project_path
        self.cp = cp
        self.frame = Frame()
        self.frame.img = self.img
        self.frame.path = self.project_path
        self.frames = self.cp.get_frames()
        print self.cp.get_frames()

    def __del__(self):
        print self.frame
        if self.frame.isAlive():
            print 'quit...'
            self.frame.stop()
        print 'huuu'

    def stop(self):
        if self.frame.isAlive():
            self.frame.stop()
            self.frame = Frame()
            self.frame.img = self.img
            self.frame.path = self.project_path
            self.action.set_stock_id(gtk.STOCK_MEDIA_PLAY)
            self.action.set_tooltip(_('Play animation'))

    def begin(self, action):
        print self.frames.next()

    def previous(self, action):
        pass

    def play(self, action):
        print self.frame
        self.action.set_stock_id(gtk.STOCK_MEDIA_STOP)
        self.action.set_tooltip(_('Stop animation'))
        if self.frame.isAlive():
            self.stop()
            print 'stop'
            return
        self.frame.frames = itertools.cycle(self.frames)
        self.frame.path = self.project_path
        self.frame.restart()
    def next(self, action):
        pass

    def end(self, action):
        pass