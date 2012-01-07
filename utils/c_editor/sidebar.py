import os
import gtk

from gettext import gettext as _


class Picture(gtk.DrawingArea):

    margin_x = 0
    margin_y = 0

    def __init__(self, path, hardshape):
        gtk.DrawingArea.__init__(self)
        self.path = path
        self.hardshape = hardshape

        self.set_events(gtk.gdk.EXPOSURE_MASK\
            | gtk.gdk.LEAVE_NOTIFY_MASK\
            | gtk.gdk.BUTTON_PRESS_MASK\
            | gtk.gdk.POINTER_MOTION_MASK\
            | gtk.gdk.POINTER_MOTION_HINT_MASK)

        self.g_hardshape = gtk.CheckButton(_('get hardshape'))
        self.g_hardshape.connect('clicked', self.get_hardshape)

        self.connect("expose-event", self.draw)
        self.get_hardshape()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        self.picture = gtk.gdk.pixbuf_new_from_file(self._path)
        self.p_width = self.picture.get_width()
        self.p_height = self.picture.get_height()
        self.set_size_request(self.p_width, self.p_height)

    @property
    def hardshape(self):
        return self._hardshape

    @hardshape.setter
    def hardshape(self, value):
        self.x = int(value[0])
        self.y = int(value[1])
        self.width = int(value[2])
        self.height = int(value[3])
        self._hardshape = value

    def draw(self, d_area=None, event=None):
        x, y, width, height = self.get_allocation()
        self.margin_x = width / 2 - self.p_width / 2
        self.margin_y = height / 2 - self.p_height / 2
        style = self.get_style()
        self.context_graph = style.fg_gc[gtk.STATE_NORMAL]
        try:
            self.window.draw_pixbuf(
                self.context_graph, self.picture,
                0, 0, self.margin_x, self.margin_y,
                )
        except KeyboardInterrupt:
            exit(0)

        if self.g_hardshape.get_active():
            self.get_hardshape()

    def get_hardshape(self, button=None):
        if self.g_hardshape.get_active():
            self.window.draw_rectangle(
                self.context_graph, False,
                self.margin_x + self.x,
                self.margin_y + self.y,
                self.width, self.height
                )
        else:
            self.modify_bg(
                gtk.STATE_NORMAL,
                gtk.gdk.color_parse("white"))


class FrameEdit(gtk.HPaned):
    def __init__(self, cp, picture_path):
        gtk.HPaned.__init__(self)
        self.properties = cp.get_frames()[0]
        self.h_bar = ''

        #Choose the good picture
        chooser_dialog = gtk.FileChooserDialog(
            title=_("Open the picture file"),
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser_dialog.set_default_response(gtk.RESPONSE_OK)

        filtre = gtk.FileFilter()
        filtre.set_name(_('pictures file'))
        # TODO : find the real(s) mime-type format
        #filtre.add_mime_type('')
        filtre.add_pattern("*.png")
        filtre.add_pattern("*.jpg")
        filtre.add_pattern("*.jpeg")
        chooser_dialog.add_filter(filtre)

        self.chooser = gtk.FileChooserButton(chooser_dialog)
        self.picture_path = cp.directory + self.properties[1]
        if os.path.exists(self.picture_path):
            self.chooser.set_filename(self.picture_path)

        #Select good picture
        self.d_area = Picture(
            cp.get_picture(picture_path), self.properties[2].split())
        self.d_area.connect("motion_notify_event", self.overview)

        # Hardshape spin buttons
        spins_hbox = gtk.HBox()

        self.adj_x = gtk.Adjustment(self.d_area.x, -1, 10000, 1, 1, 0)
        self.adj_y = gtk.Adjustment(self.d_area.y, -1, 10000, 1, 1, 0)
        self.adj_w = gtk.Adjustment(self.d_area.width, 0, 10000, 1, 1, 0)
        self.adj_h = gtk.Adjustment(self.d_area.height, 0, 10000, 1, 1, 0)

        labels = [[self.adj_x, 'x'],
            [self.adj_y, 'y'],
            [self.adj_w, 'width'],
            [self.adj_h, 'height']]

        for adj, l in labels:
            label = gtk.Label(_('%s : ' % l))
            spins_hbox.pack_start(label)
            spin = gtk.SpinButton(adj, 0.0, 0)
            spin.set_wrap(True)
            adj.connect("value-changed", self.change_hardshape)
            spins_hbox.pack_start(spin)

        # Duration
        duration_hbox = gtk.HBox()
        label = gtk.Label(_('Duration : '))
        duration_hbox.pack_start(label)

        duration = int(self.properties[0] * 1000)
        adj = gtk.Adjustment(duration, 1, 100000, 1, 1, 0)
        spin = gtk.SpinButton(adj, 0.0, 0)
        spin.set_wrap(True)
        duration_hbox.pack_start(spin)

        label = gtk.Label(_('ms'))
        duration_hbox.pack_start(label)

        #Sidebar options
        self.pack1(self.d_area, True, False)
        vbox = gtk.VBox()
        vbox.pack_start(self.d_area.g_hardshape, False)
        vbox.pack_start(self.chooser, False)
        vbox.pack_start(spins_hbox, False)
        vbox.pack_start(duration_hbox, False)
        self.pack2(vbox, False, False)
        self.show_all()

    def draw(self, path, frame):
        if not path:
            return
        self.picture_path = path
        if frame:
            self.picture_path += frame[1]
            self.d_area.hardshape = frame[2].split()

        self.d_area.path = self.picture_path

        if os.path.exists(self.picture_path):
            self.chooser.set_filename(self.picture_path)

        self._refresh_spins()

    def _refresh_spins(self):
        self.adj_x.set_value(self.d_area.x)
        self.adj_y.set_value(self.d_area.y)
        self.adj_w.set_value(self.d_area.width)
        self.adj_h.set_value(self.d_area.height)

    def _redraw(self):
        self.d_area.draw()
        self.d_area.modify_bg(gtk.STATE_NORMAL,
               gtk.gdk.color_parse("white"))
        self._refresh_spins()

    def _left(self, mouse_x):
        diff = mouse_x - self.d_area.margin_x - self.d_area.x

        if self.d_area.x + int(diff / 2) < 0:
            self.d_area.width = self.d_area.x + self.d_area.width
            self.d_area.x = 0
        elif self.d_area.width - int(diff / 2) < 1:
            self.d_area.x = self.d_area.x + self.d_area.width - 1
            self.d_area.width = 1
        else:
            self.d_area.x += int(diff / 2)
            self.d_area.width -= int(diff / 2)
        self._redraw()

    def _right(self, mouse_x):
        if mouse_x - self.d_area.margin_x > self.d_area.p_width:
            self.d_area.width = self.d_area.p_width - self.d_area.x
        elif mouse_x - self.d_area.x - self.d_area.margin_x < 1:
            self.d_area.width = 1
        else:
            self.d_area.width = mouse_x - self.d_area.x - self.d_area.margin_x
        self._redraw()

    def _top(self, mouse_y):
        diff = mouse_y - self.d_area.margin_y - self.d_area.y

        if self.d_area.y + int(diff / 2) < 0:
            self.d_area.height = self.d_area.y + self.d_area.height
            self.d_area.y = 0
        elif self.d_area.height - int(diff / 2) < 1:
            self.d_area.y = self.d_area.y + self.d_area.height - 1
            self.d_area.height = 1
        else:
            self.d_area.y += int(diff / 2)
            self.d_area.height -= int(diff / 2)
        self._redraw()

    def _bottom(self, mouse_y):
        #total = mouse_y + self.d_area.y - self.d_area.margin_y
        if mouse_y + self.d_area.y\
        - self.d_area.margin_y > self.d_area.p_height:
            self.d_area.height = self.d_area.p_height - self.d_area.y
        elif mouse_y - self.d_area.y - self.d_area.margin_y < 1:
            self.d_area.height = 1
        else:
            self.d_area.height = mouse_y - self.d_area.y - self.d_area.margin_y
        self._redraw()

    def overview(self, d_area, event):
        if not self.d_area.g_hardshape.get_active():
            return
        coord = event.get_coords()
        mouse_x = int(coord[0])
        mouse_y = int(coord[1])

        x = self.d_area.margin_x + self.d_area.x
        y = self.d_area.margin_y + self.d_area.y
        x1 = x + self.d_area.width
        y1 = y + self.d_area.height

        if event.state & gtk.gdk.BUTTON1_MASK:
            if self.h_bar == 'left':
                self._left(mouse_x)
                return
            elif self.h_bar == 'top':
                self._top(mouse_y)
                return
            elif self.h_bar == 'right':
                self._right(mouse_x)
                return
            elif self.h_bar == 'bottom':
                self._bottom(mouse_y)
                return
            elif self.h_bar == 'left_top':
                self._left(mouse_x)
                self._top(mouse_y)
                return
            elif self.h_bar == 'right_top':
                self._right(mouse_x)
                self._top(mouse_y)
                return
            elif self.h_bar == 'left_bottom':
                self._left(mouse_x)
                self._bottom(mouse_y)
                return
            elif self.h_bar == 'right_bottom':
                self._right(mouse_x)
                self._bottom(mouse_y)
                return
        else:
            self.h_bar = None

        self.d_area.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
        if self.__compare(x, mouse_x):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.LEFT_SIDE)
                )
            if event.state & gtk.gdk.BUTTON1_MASK:
                self.h_bar = 'left'
                self._left(mouse_x)
        if self.__compare(y, mouse_y):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.TOP_SIDE)
                )
            if event.state & gtk.gdk.BUTTON1_MASK:
                self.h_bar = 'top'
                self._top(mouse_y)
        if self.__compare(x1, mouse_x):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.RIGHT_SIDE)
                )
            if event.state & gtk.gdk.BUTTON1_MASK:
                self.h_bar = 'right'
                self._right(mouse_x)
        if self.__compare(y1, mouse_y):
            self.d_area.window.set_cursor(gtk.gdk.Cursor(
                gtk.gdk.BOTTOM_SIDE)
                )
            if event.state & gtk.gdk.BUTTON1_MASK:
                self.h_bar = 'bottom'
                self._bottom(mouse_y)
        if self.__compare(x, mouse_x)\
        and self.__compare(y, mouse_y):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_CORNER)
                )
            if event.state & gtk.gdk.BUTTON1_MASK:
                self.h_bar = 'left_top'
                self._left(mouse_x)
                self._top(mouse_y)
        if self.__compare(x1, mouse_x)\
        and self.__compare(y, mouse_y):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.TOP_RIGHT_CORNER)
                )
            if event.state & gtk.gdk.BUTTON1_MASK:
                self.h_bar = 'right_top'
                self._right(mouse_x)
                self._top(mouse_y)
        if self.__compare(x, mouse_x)\
        and self.__compare(y1, mouse_y):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.BOTTOM_LEFT_CORNER)
                )
            if event.state & gtk.gdk.BUTTON1_MASK:
                self.h_bar = 'left_bottom'
                self._left(mouse_x)
                self._bottom(mouse_y)
        if self.__compare(x1, mouse_x)\
        and self.__compare(y1, mouse_y):
            self.d_area.window.set_cursor(gtk.gdk.Cursor(
                gtk.gdk.BOTTOM_RIGHT_CORNER)
                )
            if event.state & gtk.gdk.BUTTON1_MASK:
                self.h_bar = 'right_bottom'
                self._right(mouse_x)
                self._bottom(mouse_y)

    def change_hardshape(self, widget):
        value = int(widget.get_value())
        if self.adj_x == widget:
            if value + self.d_area.width == self.d_area.p_width:
                return
            if value + self.d_area.width > self.d_area.p_width:
                widget.set_value(value - 1)
                return
            if value == -1:
                widget.set_value(0)
                return
            self.d_area.x = value
        if self.adj_y == widget:
            if value + self.d_area.height == self.d_area.p_height:
                return
            if value + self.d_area.height > self.d_area.p_height:
                widget.set_value(value - 1)
                return
            if value == -1:
                widget.set_value(0)
                return
            self.d_area.y = value
        if self.adj_w == widget:
            if value + self.d_area.x == self.d_area.p_width:
                return
            if value + self.d_area.x > self.d_area.p_width:
                widget.set_value(value - 1)
                return
            if value == 0:
                widget.set_value(1)
                return
            self.d_area.width = value
        if self.adj_h == widget:
            if value + self.d_area.y == self.d_area.p_height:
                return
            if value + self.d_area.y > self.d_area.p_height:
                widget.set_value(value - 1)
                return
            if value == 0:
                widget.set_value(1)
                return
            self.d_area.height = value

        self.d_area.draw()
        self.d_area.modify_bg(gtk.STATE_NORMAL,
               gtk.gdk.color_parse("white"))

    def cancel(self, widget):
        pass

    def validate(self, widget):
        pass

    def __compare(self, h_value, m_value):
        '''Compare hardshape value to mouse value :
        the acrochage is set to a value of plus or minus 5 pixels'''
        if h_value <= m_value + 5 and h_value >= m_value - 5:
            return True
