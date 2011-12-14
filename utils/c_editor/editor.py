import os
import gtk

from gettext import gettext as _


class FrameEdit:
    def __init__(self, widget, timeline, properties):
        dialog = gtk.Dialog(_('Editing Frame'))
        dialog.set_size_request(600, 400)

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

        chooser = gtk.FileChooserButton(chooser_dialog)
        self.picture_path = timeline.cp.directory + properties[1]
        if os.path.exists(self.picture_path):
            chooser.set_filename(self.picture_path)
        chooser.show()

        # Draw hardshape
        print timeline.frames
        hardshape = properties[2].split()

        self.x = int(hardshape[0])
        self.y = int(hardshape[1])
        self.width = int(hardshape[2])
        self.height = int(hardshape[3])
        self.x1 = int(hardshape[2]) + int(hardshape[0])
        self.y1 = int(hardshape[3]) + int(hardshape[1])

        d_area = gtk.DrawingArea()
        d_area.set_size_request(200, 200)
        d_area.set_events(gtk.gdk.EXPOSURE_MASK
                            | gtk.gdk.LEAVE_NOTIFY_MASK
                            | gtk.gdk.BUTTON_PRESS_MASK
                            | gtk.gdk.POINTER_MOTION_MASK
                            | gtk.gdk.POINTER_MOTION_HINT_MASK)
        #d_area.set_events(gtk.gdk.POINTER_MOTION_MASK |
        #                     gtk.gdk.POINTER_MOTION_HINT_MASK)
        d_area.connect("expose-event", self.enter)
        d_area.connect("motion_notify_event", self.overview)
        d_area.show()

        # Hardshape spin buttons
        spins_hbox = gtk.HBox()
        label = gtk.Label(_('x : '))
        spins_hbox.pack_start(label)

        adj = gtk.Adjustment(self.x, 0, 100000, 1, 1, 0)
        spin = gtk.SpinButton(adj, 0.0, 0)
        spin.set_wrap(True)
        spins_hbox.pack_start(spin)

        label = gtk.Label(_('y : '))
        spins_hbox.pack_start(label)

        adj = gtk.Adjustment(self.y, 0, 100000, 1, 1, 0)
        spin = gtk.SpinButton(adj, 0.0, 0)
        spin.set_wrap(True)
        spins_hbox.pack_start(spin)

        label = gtk.Label(_('width : '))
        spins_hbox.pack_start(label)

        adj = gtk.Adjustment(self.width, 0, 100000, 1, 1, 0)
        spin = gtk.SpinButton(adj, 0.0, 0)
        spin.set_wrap(True)
        spins_hbox.pack_start(spin)

        label = gtk.Label(_('height : '))
        spins_hbox.pack_start(label)

        adj = gtk.Adjustment(self.height, 0, 100000, 1, 1, 0)
        spin = gtk.SpinButton(adj, 0.0, 0)
        spin.set_wrap(True)
        spins_hbox.pack_start(spin)

        spins_hbox.show_all()

        # Duration
        duration_hbox = gtk.HBox()
        label = gtk.Label(_('Duration : '))
        duration_hbox.pack_start(label)

        duration = int(properties[0] * 1000)
        adj = gtk.Adjustment(duration, 1, 100000, 1, 1, 0)
        spin = gtk.SpinButton(adj, 0.0, 0)
        spin.set_wrap(True)
        duration_hbox.pack_start(spin)

        label = gtk.Label(_('ms'))
        duration_hbox.pack_start(label)
        duration_hbox.show_all()

        cancel_button = dialog.add_button(
            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        ok_button = dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        dialog.show()

        dialog.vbox.pack_start(chooser)
        dialog.vbox.pack_start(d_area)
        dialog.vbox.pack_start(spins_hbox)
        dialog.vbox.pack_start(duration_hbox)
        cancel_button.connect("clicked", self.cancel)
        ok_button.connect("clicked", self.validate)

    def overview(self, d_area, event):
        coord = event.get_coords()
        mouse_x = int(coord[0])
        mouse_y = int(coord[1])

        d_area.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
        if self.__compare(self.x, mouse_x):
            d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.LEFT_SIDE)
                )
        if self.__compare(self.y, mouse_y):
            d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.TOP_SIDE)
                )
        if self.__compare(self.x1, mouse_x):
            d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.RIGHT_SIDE)
                )
        if self.__compare(self.y1, mouse_y):
            d_area.window.set_cursor(gtk.gdk.Cursor(
                gtk.gdk.BOTTOM_SIDE)
                )
        if self.__compare(self.x, mouse_x)\
        and self.__compare(self.y, mouse_y):
            d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_CORNER)
                )
        if self.__compare(self.x1, mouse_x)\
        and self.__compare(self.y, mouse_y):
            d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.TOP_RIGHT_CORNER)
                )
        if self.__compare(self.x, mouse_x)\
        and self.__compare(self.y1, mouse_y):
            d_area.window.set_cursor(
                gtk.gdk.Cursor(gtk.gdk.BOTTOM_LEFT_CORNER)
                )
        if self.__compare(self.x1, mouse_x)\
        and self.__compare(self.y1, mouse_y):
            d_area.window.set_cursor(gtk.gdk.Cursor(
                gtk.gdk.BOTTOM_RIGHT_CORNER)
                )

    def enter(self, d_area, event):
        style = d_area.get_style()
        context_graph = style.fg_gc[gtk.STATE_NORMAL]

        self.picture = gtk.gdk.pixbuf_new_from_file(self.picture_path)

        d_area.window.draw_pixbuf(
            context_graph, self.picture,
            0, 0, 0, 0
            )

        d_area.window.draw_rectangle(
            context_graph, False,
            self.x, self.y,
            self.width, self.height
            )

    def cancel(self, widget):
        pass

    def validate(self, widget):
        pass

    def __compare(self, h_value, m_value):
        '''Compare hardshape value to mouse value :
        the acrochage is set to a value of plus or minus 5 pixels'''
        if h_value <= m_value + 5 and h_value >= m_value - 5:
            return True
