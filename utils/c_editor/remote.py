import threading
import gtk

from time import sleep
import itertools
import copy

from gettext import gettext as _

# Initializing the gtk's thread engine
gtk.gdk.threads_init()


class Frame(threading.Thread):
    '''Process thread to return the proper frame of the character'''
    #Thread event, stops the thread if it is set.
    frames = None
    img = None
    timeline = None
    path = ''

    def __init__(self):
        threading.Thread.__init__(self)
        self.stopthread = threading.Event()

    def run(self):
        """Run method, this is the code that runs while thread is alive."""

        # While the stopthread event isn't setted, the thread keeps going on
        while not self.stopthread.isSet():
            # Acquiring the gtk global mutex
            gtk.gdk.threads_enter()
            n_frame = self.frames.next()
            self.img.draw(self.path, n_frame)
            self.timeline.frame = n_frame[3]
            # Releasing the gtk global mutex
            gtk.gdk.threads_leave()
            sleep(n_frame[0])

    def stop(self):
        """Stop method, sets the event to terminate the thread's main loop"""
        self.stopthread.set()


class TimeLine(gtk.ScrolledWindow):
    def __init__(self, frames, size=1000):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_NEVER)

        self.frames = copy.deepcopy(frames)
        self._frame = None

        self.size = size
        self.hbox = gtk.HBox()
        for frame in self.frames:
            button = gtk.Button()
            button.set_label(frame[1])
            button.set_size_request(int(frame[0] * self.size), 100)
            frame.append(button)
            self.hbox.pack_start(button, False)
        self.n_style = self.frames[0][3].get_modifier_style().copy()
        self.add_with_viewport(self.hbox)
        self.show_all()

    @property
    def frame(self):
        '''frame property'''
        return self._frame

    @frame.setter
    def frame(self, value):
        for frame in self.frames:
            if frame[3] == value:
                value.modify_bg(gtk.STATE_NORMAL,
                    gtk.gdk.color_parse("green"))
                value.modify_bg(gtk.STATE_PRELIGHT,
                    gtk.gdk.color_parse("green"))
                value.modify_bg(gtk.STATE_SELECTED,
                    gtk.gdk.color_parse("green"))
                value.grab_focus()
            else:
                frame[3].modify_style(self.n_style)
                frame[3].modify_bg(gtk.STATE_NORMAL,
                    gtk.gdk.color_parse("grey"))
                frame[3].modify_bg(gtk.STATE_PRELIGHT,
                    gtk.gdk.color_parse("grey"))

        x = value.get_allocation().x
        hadjust = self.get_hadjustment()
        # TODO : complicate gitter to eliminate
        hadjust.set_value(x)

        self._frame = value


class RemoteControl():
    '''Class that orchestrates all animate frame interaction'''
    def __init__(self, img, project_path, timeline):
        self.img = img
        self.project_path = project_path

        self.timeline = timeline
        self.frames = self.timeline.frames

        self.handlers_id = []
        self.create_frame(self.timeline.frames)

    def __del__(self):
        if self.frame.isAlive():
            self.frame.stop()

    def _is_handler(self, button):
        for handler_id in self.handlers_id:
            if button.handler_is_connected(handler_id):
                return True
        return False

    def create_frame(self, iter_frames):
        # Get clicked Buttons on timeline
        for frame in self.timeline.frames:
            if not self._is_handler(frame[3]):
                h_id = frame[3].connect("clicked", self._select_frame)
                self.handlers_id.append(h_id)

        self.frame = Frame()
        self.frame.img = self.img
        self.frame.path = self.project_path
        self.frame.frames = itertools.cycle(iter_frames)

        self.frame.timeline = self.timeline

        n_frame = self.frame.frames.next()
        self.frame.timeline.frame = n_frame[3]

    def stop(self, action=None):
        if self.frame.isAlive():
            self.frame.stop()
            action.set_stock_id(gtk.STOCK_MEDIA_PLAY)
            action.set_tooltip(_('Play animation'))

    def restart(self, iter_frames):
        if self.frame.isAlive():
            self.frame.stop()
            self.create_frame(iter_frames)
            self.frame.start()

    def travel(self, frames, subtract=0):
        iteration = len(self.timeline.frames) - subtract
        while iteration > 0:
            n_frame = frames.next()
            iteration -= 1
        self.frame.timeline.frame = n_frame[3]
        self.img.draw(self.project_path, n_frame)

    def _select_frame(self, button):
        frames = itertools.cycle(self.timeline.frames)
        self.frame.timeline.frame = button
        while True:
            n_frame = frames.next()
            if n_frame[3] == button:
                break
        if self.frame.isAlive():
            self.frame.stop()
            self.travel(frames, 1)
            self.img.draw(self.project_path, n_frame)
            self.create_frame(frames)
            self.frame.start()
        else:
            self.img.draw(self.project_path, n_frame)
        self.frame.frames = frames

    def zoom(self, size=1000):
        pass

    def begin(self, action):
        frames = itertools.cycle(self.timeline.frames)
        if self.frame.isAlive():
            self.frame.stop()
            self.create_frame(frames)
            self.frame.start()
        else:
            self.travel(frames, len(self.timeline.frames) - 1)
        self.frame.frames = frames

    def previous(self, action):
        iter_frames = self.frame.frames
        if self.frame.isAlive():
            self.travel(iter_frames, 3)
            self.frame.stop()
            self.create_frame(iter_frames)
            self.frame.start()
        else:
            self.travel(iter_frames, 1)

    def play(self, action):
        action.set_stock_id(gtk.STOCK_MEDIA_STOP)
        action.set_tooltip(_('Stop animation'))
        # supress zoom possibility when play timeline
        # no good solutions to correct this...
        if self.frame.isAlive():
            action.set_stock_id(gtk.STOCK_MEDIA_PLAY)
            action.set_tooltip(_('Play animation'))
            self.zoom.set_sensitive(True)
            iter_frames = self.frame.frames
            self.travel(iter_frames, 1)
            self.frame.stop()
            self.create_frame(iter_frames)
        else:
            self.zoom.set_sensitive(False)
            self.frame.start()

    def next(self, action):
        iter_frames = self.frame.frames
        if self.frame.isAlive():
            self.travel(iter_frames, 1)
            self.frame.stop()
            self.create_frame(iter_frames)
            self.frame.start()
        else:
            self.travel(iter_frames, len(self.timeline.frames) - 1)

    def end(self, action):
        frames = itertools.cycle(self.timeline.frames)
        if self.frame.isAlive():
            self.travel(frames, 2)
            self.frame.stop()
            self.create_frame(frames)
            self.frame.start()
        else:
            self.travel(frames, 0)
        self.frame.frames = frames
