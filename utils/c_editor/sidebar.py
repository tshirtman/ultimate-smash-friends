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
        #self.connect("motion_notify_event", self.overview)
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
        self.x1 = self.margin_x + int(value[2]) + int(value[0])
        self.y1 = self.margin_y + int(value[3]) + int(value[1])
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
        self.chooser.show()

        #Select good picture
        self.d_area = Picture(
            cp.get_picture(picture_path), self.properties[2].split())
        self.d_area.show()

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
            #spin.value = l
            adj.connect("value-changed", self.change_hardshape)
            spins_hbox.pack_start(spin)

        spins_hbox.show_all()

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
        duration_hbox.show_all()

        #Sidebar options
        self.pack1(self.d_area, True, False)
        vbox = gtk.VBox()
        vbox.pack_start(self.d_area.g_hardshape, False)
        vbox.pack_start(self.chooser, False)
        vbox.pack_start(spins_hbox, False)
        vbox.pack_start(duration_hbox, False)
        self.pack2(vbox, False, False)

    def draw(self, path, frame):
        #print frame
        if not path:
            return
        self.picture_path = path
        if frame:
            self.picture_path += frame[1]
            #print 'draw============>', frame
            self.d_area.hardshape = frame[2].split()

        self.d_area.path = self.picture_path

        if os.path.exists(self.picture_path):
            self.chooser.set_filename(self.picture_path)

        self.adj_x.set_value(self.d_area.x)
        self.adj_y.set_value(self.d_area.y)
        self.adj_w.set_value(self.d_area.width)
        self.adj_h.set_value(self.d_area.height)

    def overview(self, d_area, event):
        coord = event.get_coords()
        mouse_x = int(coord[0])
        mouse_y = int(coord[1])

        self.d_area.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
        if self.__compare(self.x, mouse_x):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.LEFT_SIDE)
                )
        if self.__compare(self.y, mouse_y):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.TOP_SIDE)
                )
        if self.__compare(self.x1, mouse_x):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.RIGHT_SIDE)
                )
        if self.__compare(self.y1, mouse_y):
            self.d_area.window.set_cursor(gtk.gdk.Cursor(
                gtk.gdk.BOTTOM_SIDE)
                )
        if self.__compare(self.x, mouse_x)\
        and self.__compare(self.y, mouse_y):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_CORNER)
                )
        if self.__compare(self.x1, mouse_x)\
        and self.__compare(self.y, mouse_y):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.TOP_RIGHT_CORNER)
                )
        if self.__compare(self.x, mouse_x)\
        and self.__compare(self.y1, mouse_y):
            self.d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.BOTTOM_LEFT_CORNER)
                )
        if self.__compare(self.x1, mouse_x)\
        and self.__compare(self.y1, mouse_y):
            self.d_area.window.set_cursor(gtk.gdk.Cursor(
                gtk.gdk.BOTTOM_RIGHT_CORNER)
                )

    def change_hardshape(self, widget):
        #print 'change : ', int(widget.get_value()), widget.value
        value = int(widget.get_value())
        #x, y, width, height = self.d_area.get_allocation()
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
        #pixmap = gtk.gdk.Pixmap(self.d_area.window, width, height)
        #pixmap.draw_rectangle(self.d_area.get_style().white_gc,
        #                  True, 0, 0, width, height)

        #if widget.value == 'x':
            #style = self.d_area.get_style()
            #context_graph = style.fg_gc[gtk.STATE_NORMAL]

            #self.d_area.window.draw_drawable(
            #    self.d_area.get_style().fg_gc[gtk.STATE_NORMAL],
            #    pixmap, x, y, x, y, width, height)
            #print 'ok'

    def cancel(self, widget):
        pass

    def validate(self, widget):
        pass

    def __compare(self, h_value, m_value):
        '''Compare hardshape value to mouse value :
        the acrochage is set to a value of plus or minus 5 pixels'''
        if h_value <= m_value + 5 and h_value >= m_value - 5:
            return True
