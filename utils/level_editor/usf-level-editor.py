#!/usr/bin/env python
import pygame
import operator
import os
import sys
import math
import getopt
import time
from xml.parsers.expat import ExpatError
import logging

try:
    import pygtk
    pygtk.require("2.0")
except:
    print "Incorrect version of pyGTK or pyGTK not found."

try:
    import gtk
    import gtksourceview2
    import gtk.glade
    import gobject
except:
    print "GTK, glade, gobject or gtksourceview not found"
    sys.exit(1)

sys.path.append(os.path.join('..','..'))

from usf.config import Config
from usf import level
from usf import loaders

config = Config()

INVALID = (-5000,-5000)
ORIGIN = (0,0)
TAB = '    '

def adj_up(tup):
    """
    Adjusts a tuple up according to the ORIGIN.
    """
    return [tup[i]+ORIGIN[i] for i in range(2)]

def adj_down(tup):
    """
    Adjusts a tuple down according to the ORIGIN.
    """
    return tuple([tup[i]-ORIGIN[i] for i in range(2)])

class Tools(object):
    """
    This class is responsible for displayinh the properties of different
    elements depending on the selected tool.
    """
    def __init__(self, widget, ok_callback, cancel_callback, texture_callback):
        """
        Initialises some class variables.
        """
        self.bin = widget
        self.mapping = {
                        "block":self.show_block_tool,
                        "entry":self.show_entry_tool,
                        "water":self.show_water_tool,
                        "moving":self.show_moving_tool,
                        "vector":self.show_vector_tool,
                        "select":self.show_select_tool,
                        "delete":self.show_delete_tool,
                        }
        self.vbox = None
        self.ok_cb = ok_callback
        self.cancel_cb = cancel_callback
        self.texture_cb = texture_callback

    def clear(self):
        """
        Clears the entity properties container.
        """
        self.adj = []
        for i in range(10):
            self.adj.append(gtk.Adjustment(0, -5000, 5000, 1, 10, 0))
        if self.bin.get_child() != None:
            self.bin.remove(self.bin.get_child())
        self.bin.set_label("Element Properties")
        self.vbox = gtk.VBox()
        self.bin.add(self.vbox)

    def add_pos(self):
        """
        Add position entry boxes to the properties container.
        """
        x_label = gtk.Label("X Position: ")
        y_label = gtk.Label("Y Position: ")
        hbox1 = gtk.HBox()
        hbox2 = gtk.HBox()

        self.x_entry = gtk.SpinButton(self.adj[0], 1)
        self.y_entry = gtk.SpinButton(self.adj[1], 1)
        self.x_entry.set_width_chars(6)
        self.y_entry.set_width_chars(6)

        hbox1.add(x_label)
        hbox1.add(self.x_entry)
        self.vbox.add(hbox1)
        hbox2.add(y_label)
        hbox2.add(self.y_entry)
        self.vbox.add(hbox2)

    def add_size(self):
        """
        Add size entry boxes to the properties container.
        """
        w_label = gtk.Label("Width:  ")
        h_label = gtk.Label("Height: ")
        hbox1 = gtk.HBox()
        hbox2 = gtk.HBox()

        self.w_entry = gtk.SpinButton(self.adj[2], 1)
        self.h_entry = gtk.SpinButton(self.adj[3], 1)
        self.w_entry.set_width_chars(6)
        self.h_entry.set_width_chars(6)

        hbox1.add(w_label)
        hbox1.add(self.w_entry)
        self.vbox.add(hbox1)
        hbox2.add(h_label)
        hbox2.add(self.h_entry)
        self.vbox.add(hbox2)

    def add_vector(self):
        """
        Add vector entry boxes to the properties container.
        """
        vec_x_label = gtk.Label("X Vector: ")
        vec_y_label = gtk.Label("Y Vector: ")
        hbox1 = gtk.HBox()
        hbox2 = gtk.HBox()

        self.vec_x_entry = gtk.SpinButton(self.adj[4], 1)
        self.vec_y_entry = gtk.SpinButton(self.adj[5], 1)
        self.vec_x_entry.set_width_chars(6)
        self.vec_y_entry.set_width_chars(6)

        hbox1.add(vec_x_label)
        hbox1.add(self.vec_x_entry)
        self.vbox.add(hbox1)
        hbox2.add(vec_y_label)
        hbox2.add(self.vec_y_entry)
        self.vbox.add(hbox2)

    def add_texture(self):
        """
        Add texture entry boxes to the properties container.
        """
        hbox = gtk.HBox()
        tex_label = gtk.Label("Texture: ")
        self.tex_entry = gtk.Entry()
        load_button = gtk.Button("...")

        load_button.connect("clicked", self.texture_cb)

        hbox.add(self.tex_entry)
        hbox.add(load_button)
        self.vbox.add(tex_label)
        self.vbox.add(hbox)

    def add_buttons(self):
        """
        Add an apply and cancel buttons to the properties container.
        """
        ok_button = gtk.Button("Apply")
        cancel_button = gtk.Button("Cancel")
        hbox = gtk.HBox()

        ok_button.connect("clicked", self.ok_cb)
        cancel_button.connect("clicked", self.cancel_cb)
        hbox.set_spacing(3)

        hbox.add(ok_button)
        hbox.add(cancel_button)
        self.vbox.add(hbox)

    def add_table(self):
        """
        Add a table to the properties container.
        """
        scroll = gtk.ScrolledWindow()
        self.model = gtk.ListStore(str, str, str)
        table_label = gtk.Label("Patterns: ")
        treeview = gtk.TreeView(self.model)

        treeview.set_property("height-request", 125)

        x_cell = gtk.CellRendererSpin()
        x_cell.connect("edited", self.changed, self.model, 0)
        x_cell.set_property("editable", True)
        x_cell.set_property("adjustment", self.adj[6])

        y_cell = gtk.CellRendererSpin()
        y_cell.connect("edited", self.changed, self.model, 1)
        y_cell.set_property("editable", True)
        y_cell.set_property("adjustment", self.adj[7])

        t_cell = gtk.CellRendererSpin()
        t_cell.connect("edited", self.changed, self.model, 2)
        t_cell.set_property("editable", True)
        t_cell.set_property("adjustment", self.adj[8])

        x_col = gtk.TreeViewColumn("X", x_cell, text=0)
        y_col = gtk.TreeViewColumn("Y", y_cell, text=1)
        t_col = gtk.TreeViewColumn("Time", t_cell, text=2)

        x_col.set_min_width(50)
        y_col.set_min_width(50)
        t_col.set_min_width(50)

        treeview.append_column(x_col)
        treeview.append_column(y_col)
        treeview.append_column(t_col)

        scroll.add(treeview)
        self.vbox.add(table_label)
        self.vbox.add(scroll)

    def changed(self, *args, **kwargs):
        """
        Updates the liststore whenever a change is made to a pattern.
        """
        self.model.set_value(self.model.get_iter(args[1]), args[4], args[2])

    def format_labels(self):
        """
        Formats all the labels to appear more to the right.
        """
        for w in self.vbox.get_children():
            if isinstance(w, gtk.Label):
                w.set_alignment(0.0, 0.5)
                w.set_padding(5, 0)

            if isinstance(w, gtk.Container):
                for w1 in w.get_children():
                    if isinstance(w1, gtk.Label):
                        w1.set_alignment(0.0, 0.5)
                        w1.set_padding(5, 0)

    def show_block_tool(self, block=None):
        """
        Sets up the GUI to show block properties.
        """
        self.clear()

        self.add_pos()
        self.add_size()
        self.add_buttons()

        self.format_labels()

        if block != None:
            self.x_entry.set_value(block[0])
            self.y_entry.set_value(block[1])
            self.w_entry.set_value(block[2])
            self.h_entry.set_value(block[3])

        self.vbox.show_all()

    def show_moving_tool(self, block=None):
        """
        Sets up the GUI to show moving block properties.
        """
        self.clear()

        self.add_pos()
        self.add_size()
        self.add_texture()
        self.add_table()
        self.add_buttons()

        self.format_labels()

        if block != None:
            self.x_entry.set_value(block.patterns[0]["position"][0])
            self.y_entry.set_value(block.patterns[0]["position"][1])
            self.w_entry.set_value(block.rects[0][2])
            self.h_entry.set_value(block.rects[0][3])
            self.tex_entry.set_text(block.texture)

            for p in block.patterns:
                self.model.append([p["position"][0], p["position"][1], p["time"]])

        self.vbox.show_all()

    def show_vector_tool(self, block=None):
        """
        Sets up the GUI to show vector block properties.
        """
        self.clear()

        self.add_pos()
        self.add_size()

        self.rel_check = gtk.CheckButton("Relative")
        self.vbox.add(self.rel_check)

        self.add_vector()
        self.add_texture()
        self.add_buttons()

        self.format_labels()

        if block != None:
            self.x_entry.set_value(block.position[0])
            self.y_entry.set_value(block.position[1])
            self.w_entry.set_value(block.rects[0][2])
            self.h_entry.set_value(block.rects[0][3])
            self.rel_check.set_active(block.relative)
            self.vec_x_entry.set_value(block.vector[0])
            self.vec_y_entry.set_value(block.vector[1])
            self.tex_entry.set_text(block.texture)

        self.vbox.show_all()

    def show_entry_tool(self, pt=None):
        """
        Sets up the GUI to show entry point properties.
        """
        self.clear()

        self.add_pos()
        self.add_buttons()

        self.format_labels()

        if pt != None:
            self.x_entry.set_value(pt[0])
            self.y_entry.set_value(pt[1])

        self.vbox.show_all()

    def show_water_tool(self, block=None):
        """
        Sets up the GUI to show water block properties.
        """
        self.clear()

        self.add_pos()
        self.add_size()
        self.add_buttons()

        self.format_labels()

        if block != None:
            self.x_entry.set_value(block[0])
            self.y_entry.set_value(block[1])
            self.w_entry.set_value(block[2])
            self.h_entry.set_value(block[3])

        self.vbox.show_all()

    def show_select_tool(self, block=None):
        """
        Sets up the GUI to show select tool properties.
        """
        self.clear()

        label = gtk.Label("No properties for this tool")

        self.vbox.add(label)
        self.vbox.show_all()

    def show_delete_tool(self, block=None):
        """
        Sets up the GUI to show delete tool properties.
        """
        self.clear()

        label = gtk.Label("No properties for this tool")

        self.vbox.add(label)
        self.vbox.show_all()

class PygameHandler(object):
    """
    Class responsible for most of the pygame related functions
    i.e. mainly drawing the level and its elements.
    """
    def __init__(self, widget):
        """
        Initialises class variables.
        """
        self.alpha = 128
        self.xml_file = "emptyLevel/emptyLevel"
        self.level = level.Level(self.xml_file)

        self.parts = {
                    "block":{"visible":True, "colour":pygame.Color("#FF0000")},
                    "moving":{"visible":True, "colour":pygame.Color("#FFFF00")},
                    "water":{"visible":True, "colour":pygame.Color("#0000FF")},
                    "vector":{"visible":True, "colour":pygame.Color("#00FF00")},
                    "entry":{"visible":True, "colour":pygame.Color("#FF00FF")},
                    }

        self.surface = pygame.display.set_mode(level.SIZE)
        self.tool = "block"
        self.start_pt = INVALID
        self.widget = widget
        self.secondary = False
        self.texture = os.path.join(
                                    config.sys_data_dir,
                                    "levels",
                                    "emptyPod.png"
                                    )

    def set_level_property(self, property, value):
        """
        Sets the level properties in Level.
        """
        if property == "background":
            self.level.background = value
        elif property == "foreground":
           self.level.foreground = value
        elif property == "level":
            self.level.level = value
        elif property == "name":
            self.level.name = value
        else:
            print "Invalid property."

    def draw_arrow(self, surface, colour, from_pt, to_pt):
        """
        Draws an arrow from one point to another.
        """
        pygame.draw.line(surface, colour, from_pt, to_pt, 2)
        pygame.draw.circle(surface, colour, from_pt, 4, 0)

        arrow=pygame.Surface((20,20))
        arrow.fill(pygame.Color("#FFFFFE"))
        pygame.draw.line(arrow, colour, (0,0), (10,10), 2)
        pygame.draw.line(arrow, colour, (0,20), (10,10), 2)
        arrow.set_colorkey(pygame.Color("#FFFFFE"))

        angle=math.degrees(math.atan2(-(
                                        from_pt[1]-to_pt[1]),
                                        from_pt[0]-to_pt[0]
                                        )
                                    )+180

        final_arrow = pygame.transform.rotate(arrow,angle)
        surface.blit(final_arrow, final_arrow.get_rect(center=to_pt))

    def draw(self):
        """
        Draws all the pygame related things:
        i.e. the level and overlays
        """
        self.level.draw_background(self.surface)
        self.level.draw_level(self.surface, ORIGIN, 1)

        for block in self.level.moving_blocs:
            self.surface.blit(
                            loaders.image(block.texture, 1)[0],
                            adj_up(block.patterns[0]["position"])
                            )

        for block in self.level.vector_blocs:
            self.surface.blit(
                            loaders.image(block.texture, 1)[0],
                            adj_up(block.position)
                            )

        self.level.draw_foreground(self.surface, ORIGIN, 1)

        overlay = pygame.Surface(level.SIZE)
        overlay.set_colorkey(pygame.Color("#FFFFFE"))
        overlay.fill(pygame.Color("#FFFFFE"))
        overlay.set_alpha(self.alpha)

        #Draw water blocks
        if self.parts["water"]["visible"]:
            for water_block in self.level.water_blocs:
                pygame.draw.rect(
                                overlay,
                                self.parts["water"]["colour"],
                                water_block.move(ORIGIN)
                                )

        #Draw solid blocks
        if self.parts["block"]["visible"]:
            for block in self.level.map:
                pygame.draw.rect(
                                overlay,
                                self.parts["block"]["colour"],
                                block.move(ORIGIN)
                                )

        #Draw moving blocks
        if self.parts["moving"]["visible"]:
            for moving_block in self.level.moving_blocs:
                #moving_block.patterns.sort(key=lambda item:item["time"])
                for rect in moving_block.rects:
                    pygame.draw.rect(
                                    overlay,
                                    self.parts["moving"]["colour"],
                                    rect.move(
                                            moving_block.patterns[0]["position"]
                                            ).move(ORIGIN)
                                    )

                colour = tuple(
                            [max(i-100,0) for i in self.parts["moving"]["colour"]]
                            )

                for i in range(len(moving_block.patterns)):
                    self.draw_arrow(
                                    overlay,
                                    colour,
                                    adj_up(
                                        moving_block.patterns[i-1]["position"]
                                        ),
                                    adj_up(
                                        moving_block.patterns[i]["position"]
                                        )
                                    )

        #Draw vector blocks
        if self.parts["vector"]["visible"]:
            for vector_block in self.level.vector_blocs:
                for rect in vector_block.rects:
                    pygame.draw.rect(
                                    overlay,
                                    self.parts["vector"]["colour"],
                                    rect.move(
                                            vector_block.position
                                            ).move(ORIGIN)
                                    )

                colour = tuple(
                            [max(i-100,0) for i in self.parts["vector"]["colour"]]
                            )

                self.draw_arrow(
                                overlay,
                                colour,
                                adj_up(vector_block.position),
                                tuple(
                                    [vector_block.position[i] +
                                    vector_block.vector[i] +
                                    ORIGIN[i] for i in range(2)]
                                    )
                                )

        #Draw entry points
        if self.parts["entry"]["visible"]:
            for entry_point in self.level.entrypoints:
                pygame.draw.rect(
                                overlay,
                                self.parts["entry"]["colour"],
                                pygame.Rect(
                                            entry_point,
                                            (10,10)
                                            ).move(ORIGIN)
                                )

        #Draw tool stuff
        pointer = self.widget.get_pointer()

        if not self.secondary:
            if (self.start_pt != INVALID and
                (self.tool in ["block", "water", "vector", "moving"])):
                pygame.draw.rect(
                                overlay,
                                self.parts[self.tool]["colour"],
                                pygame.Rect(
                                            self.start_pt,
                                            (pointer[0]-self.start_pt[0],
                                            pointer[1]-self.start_pt[1])
                                            )
                                )

            if self.tool in ["vector", "moving"] and self.start_pt != INVALID:
                self.surface.blit(loaders.image(self.texture, 1)[0], self.start_pt)
        else:
            if self.tool in ["vector", "moving"]:
                self.draw_arrow(
                                overlay,
                                self.parts[self.tool]["colour"],
                                self.start_pt,
                                pointer
                                )

        #TODO margins and layers
        self.surface.blit(overlay, (0,0))

class USFLevelEditor(object):
    """
    This is a gtk application to create and edit levels for
    ultimate-smash-friends.
    """
    def __init__(self):
        """
        Initializes the GUI and pygame surface.
        """
        glade_file = os.path.join(
                                config.sys_data_dir,
                                "glade",
                                "usf_level_editor.glade"
                                )

        self.wTree = gtk.glade.XML(glade_file, "mainWindow")
        self.window = self.wTree.get_widget("mainWindow")
        self.window.set_title("USF Level Editor")
        self.window.maximize()

        #connect signals
        if self.window:
            signals = {
                        "delete-event": self.callback_quit,
                        "menu_file_open": self.callback_menu_file_open,
                        "menu_file_new": self.callback_menu_file_new,
                        "menu_file_quit": self.callback_quit,
                        "menu_file_save": self.callback_menu_file_save,
                        "menu_file_save_as": self.callback_menu_file_save_as,
                        "alpha_change": self.callback_alpha_change,
                        "visible_toggle":self.callback_visible_toggle,
                        "colour_change": self.callback_colour_change,
                        "select_tool": self.callback_select_tool,
                        "png_load": self.callback_level_properties_change,
                        "pygame_press": self.callback_pygame_press,
                        "pygame_release": self.callback_pygame_release,
                        }
            self.wTree.signal_autoconnect(signals)

        #XML viewer
        language_manager = gtksourceview2.LanguageManager()
        lang = language_manager.get_language("xml")
        self.xml_buffer = gtksourceview2.Buffer(language=lang)
        self.xml_buffer.set_max_undo_levels(1000)

        view = gtksourceview2.View()
        view.set_buffer(self.xml_buffer)
        view.set_show_line_numbers(True)
        view.set_indent_on_tab(True)
        view.set_indent_width(4)
        view.set_editable(False)

        self.wTree.get_widget("xmlViewerScroller").add(view)
        view.show()

        self.level_property_entry = {
                        "foreground":self.wTree.get_widget("foreground_entry"),
                        "background":self.wTree.get_widget("background_entry"),
                        "level":self.wTree.get_widget("level_entry"),
                        "name":self.wTree.get_widget("name_entry"),
                        }

        #pygame stuff
        self.pygame_widget = self.wTree.get_widget("pygame")

        gobject.idle_add(self.update)
        os.environ["SDL_WINDOWID"] = str(self.pygame_widget.window.xid)
        pygame.init()

        #level stuff
        self.pyHandle = PygameHandler(self.pygame_widget)
        self.resize_viewport()

        self.tools = Tools(
                            self.wTree.get_widget("tools"),
                            self.callback_accept_tool,
                            self.callback_cancel_tool,
                            self.callback_texture_load
                            )

        self.tools.show_block_tool()
        self.current_entity = [None, None]

        self.cancel = False

    def create_file_loader(self, opener):
        """
        Creates a default file loader.
        """
        buttons = (
                gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL,
                opener and gtk.STOCK_OPEN or gtk.STOCK_SAVE,
                gtk.RESPONSE_OK
                )

        file_loader = gtk.FileChooserDialog(
                                opener and "Open..." or "Save As...",
                                None,
                                opener and
                                    gtk.FILE_CHOOSER_ACTION_OPEN or
                                    gtk.FILE_CHOOSER_ACTION_SAVE,
                                buttons
                                )

        file_loader.set_current_folder(os.sep.join([".", "data", "levels"]))
        return file_loader

    def attach_filter(self, widget, title, types):
        """
        Attaches the file extensions in types to the filechooser widget
        and gives it a title.
        """
        file_filter = gtk.FileFilter()
        file_filter.set_name(title)

        for i in types:
            file_filter.add_mime_type(i)

        widget.add_filter(file_filter)

    def resize_viewport(self):
        """
        Resizes the pygame surface and the pygame widget.
        """
        global ORIGIN
        mid = pygame.image.load(self.pyHandle.level.level).get_size()
        front = pygame.image.load(self.pyHandle.level.foreground).get_size()
        level.SIZE = tuple([int(i*1.5) for i in max(mid, front)])

        ORIGIN = (
                (level.SIZE[0] - mid[0]) / 2,
                (level.SIZE[1] - mid[1]) / 2
                )
        self.pyHandle.surface = pygame.display.set_mode(level.SIZE)
        self.pygame_widget.set_size_request(level.SIZE[0], level.SIZE[1])

    def callback_menu_file_open(self, *args, **kwargs):
        """
        Handles the opening of a level.
        """
        #TODO:if file is already open and it is not saved show 'are you sure' dialog
        file_loader = self.create_file_loader(True)
        self.attach_filter(file_loader, "All XML files", ["text/xml"])

        if file_loader.run() == gtk.RESPONSE_OK:
            file = open(file_loader.get_filename())

            self.pyHandle.xml_file = file_loader.get_filename()
            self.pyHandle.level = level.Level(
                file_loader.get_filename().split(os.sep)[-1].split(os.extsep)[0]
                )

            self.window.set_title("USF Level Editor: " + self.pyHandle.level.name)
            self.xml_buffer.set_text(file.read())
            file.close()

            self.resize_viewport()

            #toolbar updates
            self.level_property_entry["background"].set_text(
                            self.pyHandle.level.background.split(os.sep)[-1]
                            )

            self.level_property_entry["level"].set_text(
                            self.pyHandle.level.level.split(os.sep)[-1]
                            )

            self.level_property_entry["foreground"].set_text(
                        self.pyHandle.level.foreground.split(os.sep)[-1]
                        )

            self.level_property_entry["name"].set_text(self.pyHandle.level.name)

        file_loader.destroy()
        self.tools.mapping[self.pyHandle.tool]

    def callback_alpha_change(self, *args, **kwargs):
        """
        Adjusts the transparency of the overlay according
        to the transparency scale widget.
        """
        self.pyHandle.alpha = int(
            self.wTree.get_widget("alphaScale").get_adjustment().get_value() / 100.0 * 255
            )

    def callback_menu_file_new(self, *args, **kwargs):
        """
        """
        #TODO: saving???
        self.pyHandle.xml_file = "emptyLevel/emptyLevel"
        self.pyHandle.level = level.Level(self.pyHandle.xml_file)
        self.resize_viewport()

    def callback_quit(self, *args, **kwargs):
        """
        Stops the application and quits.
        """
        #TODO saving??
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.window.hide()
        gtk.main_quit()

    def callback_menu_file_save(self, *args, **kwargs):
        """
        Saves the current level.
        """
        if self.pyHandle.xml_file == "emptyLevel/emptyLevel":
            self.callback_menu_file_save_as(None, None)
        else:
            self.save()

    def callback_menu_file_save_as(self, *args, **kwargs):
        """
        Asks the user to pick a name to save the level to.
        """
        file_saver = self.create_file_loader(False)
        self.attach_filter(file_saver, "All XML files", ["text/xml"])

        if file_saver.run() == gtk.RESPONSE_OK:
            self.pyHandle.xml_file = file_saver.get_filename()

        file_saver.destroy()
        self.callback_menu_file_save(None)

    def callback_level_properties_change(self, *args, **kwargs):
        """
        Changes level properties according to values entered in the
        Level Properties section of the GUI.
        """
        if args[0].get_name() == "name_entry":
            self.pyHandle.py_set_properties("name", args.get_text())
        else:
            file_loader = self.create_file_loader(True)
            self.attach_filter(file_loader, "All PNG files", ["image/png"])

            if file_loader.run() == gtk.RESPONSE_OK:
                self.level_property_entry[
                                    args[0].get_name().split("_")[0]
                                    ].set_text(
                                        file_loader.get_filename().split(
                                            os.sep
                                            )[-1]
                                        )

                self.pyHandle.set_level_property(
                                            args[0].get_name().split("_")[0],
                                            file_loader.get_filename()
                                            )

            file_loader.destroy()
            self.resize_viewport()

    def callback_visible_toggle(self, *args, **kwargs):
        """
        Handles pygame visibility according to GUI check button changes.
        """
        self.pyHandle.parts[
                        args[0].get_name().split("_")[0]
                        ]["visible"] = args[0].get_active()

    def callback_colour_change(self, *args, **kwargs):
        """
        Handles GUI colour changes.
        """
        colour_widget = args[0].get_color()

        self.pyHandle.parts[
            args[0].get_name().split("_")[0]]["colour"] = pygame.Color(
                                    int(colour_widget.red / 65535.0 * 255),
                                    int(colour_widget.green / 65535.0 * 255),
                                    int(colour_widget.blue / 65535.0 * 255)
                                    )

    def callback_select_tool(self, *args, **kwargs):
        """
        Selects the appropriate tool according to the GUI.
        """
        self.pyHandle.secondary = False
        self.pyHandle.start_pt = INVALID

        if args[0].get_active():
            self.pyHandle.tool = args[0].get_name()
            self.tools.mapping[self.pyHandle.tool]()

    def callback_texture_load(self, *args, **kwargs):
        """
        Sets the texture to use for tools that require textures.
        """
        file_loader = self.create_file_loader(True)
        self.attach_filter(file_loader, "All PNG files", ["image/png"])

        if file_loader.run() == gtk.RESPONSE_OK:
            self.tools.tex_entry.set_text(file_loader.get_filename())
            self.pyHandle.texture = file_loader.get_filename()

        file_loader.destroy()
        self.resize_viewport()

    def callback_accept_tool(self, *args, **kwargs):
        """
        Applies changes made in the entity properties container.
        """
        self.current_entity[0].remove(self.current_entity[1])

        if self.pyHandle.tool in ["block", "water"]:
            self.current_entity[1] = pygame.Rect(
                                                self.tools.x_entry.get_value(),
                                                self.tools.y_entry.get_value(),
                                                self.tools.w_entry.get_value(),
                                                self.tools.h_entry.get_value()
                                                )
        elif self.pyHandle.tool == "entry":
            self.current_entity[1] = (
                                    self.tools.x_entry.get_value(),
                                    self.tools.y_entry.get_value()
                                    )
        elif self.pyHandle.tool == "moving":
            it = self.tools.model.get_iter_root()

            pat = [{
                    "time":int(self.tools.model.get_value(it, 2)),
                    "position":[
                                int(self.tools.model.get_value(it, 0)),
                                int(self.tools.model.get_value(it, 1))
                                ]
                    }]

            while self.tools.model.iter_next(it) != None:
                it = self.tools.model.iter_next(it)

                pat.append({
                            "time":int(self.tools.model.get_value(it, 2)),
                            "position":[
                                        int(self.tools.model.get_value(it, 0)),
                                        int(self.tools.model.get_value(it, 1))
                                        ]
                            })

            self.current_entity[1] = level.MovingPart(
                        [pygame.Rect(
                            (0, 0),
                            (self.tools.w_entry.get_value(),
                            self.tools.h_entry.get_value())
                            )
                        ],
                        self.tools.tex_entry.get_text().split(os.sep)[-1],
                        pat
                        )

        elif self.pyHandle.tool == "vector":
            self.current_entity[1] = level.VectorBloc(
                        [pygame.Rect(
                            (0, 0),
                            (self.tools.w_entry.get_value(),
                            self.tools.h_entry.get_value())
                            )
                        ],
                        (
                            self.tools.x_entry.get_value(),
                            self.tools.y_entry.get_value()
                        ),
                        (
                            self.tools.vec_x_entry.get_value(),
                            self.tools.vec_y_entry.get_value()
                        ),
                        self.tools.rel_check.get_active(),
                        self.tools.tex_entry.get_text().split(os.sep)[-1]
                        )

        self.current_entity[0].append(self.current_entity[1])

    def callback_cancel_tool(self, *args, **kwargs):
        """
        Cancels any changes made to the properties.
        """
        self.tools.mapping[self.pyHandle.tool](self.current_entity[1])

    def callback_pygame_press(self, *args, **kwargs):
        """
        Changes drawing states according to the user input and tool selected.
        """
        if not self.pyHandle.secondary:
            if self.pyHandle.tool not in ["entry", "select", "delete"]:
                self.pyHandle.start_pt = self.pygame_widget.get_pointer()

    def callback_pygame_release(self, *args, **kwargs):
        """
        Updates the level according to user modifications and input.
        """
        if self.cancel:
            self.cancel = False

        if args[1].button == 3:
            self.pyHandle.secondary = False
            self.pyHandle.start_pt = INVALID
            self.cancel = True
            return

        pointer = adj_down(self.pygame_widget.get_pointer())
        self.pyHandle.start_pt = adj_down(self.pyHandle.start_pt)

        rect = pygame.Rect(
                            self.pyHandle.start_pt,
                            (
                                pointer[0]-self.pyHandle.start_pt[0],
                                pointer[1]-self.pyHandle.start_pt[1]
                            )
                            )

        if self.pyHandle.tool == "entry":
            self.pyHandle.level.entrypoints.append(pointer)

            self.current_entity = [
                                self.pyHandle.level.entrypoints,
                                self.pyHandle.level.entrypoints[-1]
                                ]

            self.tools.show_entry_tool(self.pyHandle.level.entrypoints[-1])
        elif self.pyHandle.tool == "block":
            self.pyHandle.level.map.append(rect)

            self.current_entity = [
                                self.pyHandle.level.map,
                                self.pyHandle.level.map[-1]
                                ]

            self.tools.show_block_tool(self.pyHandle.level.map[-1])
        elif self.pyHandle.tool == "water":
            self.pyHandle.level.water_blocs.append(rect)

            self.current_entity = [
                                self.pyHandle.level.water_blocs,
                                self.pyHandle.level.water_blocs[-1]
                                ]

            self.tools.show_water_tool(self.pyHandle.level.water_blocs[-1])
        elif self.pyHandle.tool == "vector":
            bloc = None
            if self.tools.tex_entry.get_text() == "":
                self.tools.tex_entry.set_text(self.pyHandle.texture)

            if self.pyHandle.secondary:
                self.pyHandle.level.vector_blocs.remove(self.current_entity[1])

                bloc = level.VectorBloc(
                                self.current_entity[1].rects,
                                self.current_entity[1].position,
                                rect.size,
                                self.tools.rel_check.get_active(),
                                self.tools.tex_entry.get_text().split(os.sep)[-1]
                                )

                self.pyHandle.start_pt = INVALID
                self.pyHandle.secondary = False
            else:
                bloc = level.VectorBloc(
                                [pygame.Rect((0,0),rect.size)],
                                rect.topleft,
                                (0,0),
                                self.tools.rel_check.get_active(),
                                self.tools.tex_entry.get_text().split(os.sep)[-1]
                                )

                self.pyHandle.secondary = True
                self.pyHandle.start_pt = adj_up(self.pyHandle.start_pt)

            self.pyHandle.level.vector_blocs.append(bloc)
            self.current_entity = [self.pyHandle.level.vector_blocs, self.pyHandle.level.vector_blocs[-1]]
            self.tools.show_vector_tool(self.pyHandle.level.vector_blocs[-1])
        elif self.pyHandle.tool == "moving":
            bloc = None
            if self.tools.tex_entry.get_text() == "":
                self.tools.tex_entry.set_text(self.pyHandle.texture)

            if self.pyHandle.secondary:
                self.pyHandle.level.moving_blocs.remove(self.current_entity[1])

                self.current_entity[1].patterns.append({
                        "time":self.current_entity[1].patterns[-1]["time"]+100,
                        "position":list(pointer)
                        })

                bloc = level.MovingPart(
                                self.current_entity[1].rects,
                                self.tools.tex_entry.get_text().split(os.sep)[-1],
                                self.current_entity[1].patterns
                                )

                self.pyHandle.start_pt = adj_up(pointer)
            else:
                bloc = level.MovingPart(
                                    [pygame.Rect((0,0),rect.size)],
                                    self.tools.tex_entry.get_text().split(os.sep)[-1],
                                    [{"time":1, "position":list(rect.topleft)}]
                                    )

                self.pyHandle.secondary = True
                self.pyHandle.start_pt = adj_up(self.pyHandle.start_pt)

            self.pyHandle.level.moving_blocs.append(bloc)
            self.current_entity = [self.pyHandle.level.moving_blocs, self.pyHandle.level.moving_blocs[-1]]
            self.tools.show_moving_tool(self.pyHandle.level.moving_blocs[-1])
        elif self.pyHandle.tool == "delete":
            delete = self.find(pointer)

            if delete != None:
                delete[0].remove(delete[1])

        elif self.pyHandle.tool == "select":
            select = self.find(pointer)

            if select != None:
                self.current_entity = [select[0], select[1]]
                self.pyHandle.tool = select[2]
                self.tools.mapping[select[2]](select[1])

        if self.pyHandle.tool not in ["vector", "moving"]:
            self.pyHandle.start_pt = INVALID

    def find(self, pt):
        """
        Finds any entity that intersects with the given point along with its
        container.
        """
        for entry in self.pyHandle.level.entrypoints:
            if pygame.Rect(entry, (10,10)).collidepoint(pt):
                return (self.pyHandle.level.entrypoints, entry, "entry")

        for water in self.pyHandle.level.water_blocs:
            if water.collidepoint(pt):
                return (self.pyHandle.level.water_blocs, water, "water")

        for block in self.pyHandle.level.map:
            if block.collidepoint(pt):
                return (self.pyHandle.level.map, block, "block")

        for vector in self.pyHandle.level.vector_blocs:
            if pygame.Rect(vector.position, vector.rects[0].size).collidepoint(pt):
                return (self.pyHandle.level.vector_blocs, vector, "vector")

        for moving in self.pyHandle.level.moving_blocs:
            if pygame.Rect(
                        moving.patterns[0]["position"],
                        moving.rects[0].size
                        ).collidepoint(pt):
                return (self.pyHandle.level.moving_blocs, moving, "moving")

        return None

    def update(self):
        """
        Performs what is needed for each iteration i.e. the body of the main loop.
        """
        self.pyHandle.draw()
        pointer = self.pygame_widget.get_pointer()

        sb = self.wTree.get_widget("statusBar")
        if sb != None:
            if (pointer[0] in range(level.SIZE[0]) and
                pointer[1] in range(level.SIZE[1])):
                p = adj_down(pointer)
                sb.push(
                    sb.get_context_id("SB"),
                    "x: " + str(p[0]) + " y: " + str(p[1]))
            else:
                sb.push(sb.get_context_id("SB"), "x: - y: -")

        pygame.display.flip()
        return True

    def save(self):
        """
        Saves the contents of the level to XML.
        """
        f = open(self.pyHandle.xml_file, "w")
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<map\n')
        f.write(TAB + 'name="' + self.level_property_entry["name"].get_text() + '"\n')
        f.write(TAB + 'background="' + self.level_property_entry["background"].get_text() + '"\n')
        f.write(TAB + 'foreground="' + self.level_property_entry["foreground"].get_text() + '"\n')
        f.write(TAB + 'middle="' + self.level_property_entry["level"].get_text() + '"\n')
        f.write(TAB + 'margins="' + str(self.pyHandle.level.border[0]) + ',' + 
                                    str(self.pyHandle.level.border[1]) + ',' + 
                                    str(self.pyHandle.level.border[2]) + ',' +
                                    str(self.pyHandle.level.border[3]) + '">\n')

        f.write('\n')
        for entry_point in self.pyHandle.level.entrypoints:
            f.write(TAB + '<entry-point coords="' + str(entry_point[0]) + ' '
                        +str(entry_point[1])+'"></entry-point>\n')
                        
        f.write('\n')
        for block in self.pyHandle.level.map:
            f.write(TAB + '<block coords="' + str(block[0]) + ' ' + 
                        str(block[1]) + ' ' + str(block[2]) + ' ' + 
                        str(block[3])+'"></block>\n')
                        
        f.write('\n')
        for water in self.pyHandle.level.water_blocs:
            f.write(TAB + '<water coords="' + str(block[0]) + ' ' + 
                        str(block[1]) + ' ' + str(block[2]) + ' ' + 
                        str(block[3])+'"></water>\n')
                        
        f.write('\n')
        for mov in self.pyHandle.level.moving_blocs:
            f.write(TAB + '<moving-block\n' + TAB * 2 + 'texture="' + 
                        mov.texture.split(os.sep)[-1]+'">\n')
                        
            for rect in mov.rects:
                f.write(TAB + '<rect coords="' + str(rect[0]) + ' ' + 
                            str(rect[1]) + ' ' + str(rect[2]) + ' ' + 
                            str(rect[3])+'"></rect>\n')
                            
            for pat in mov.patterns:
                f.write(TAB * 2 + '<pattern\n')
                f.write(TAB * 3 + 'position="' + str(pat["position"][0]) + ' ' +
                            str(pat["position"][1]) + '"\n')
                f.write(TAB * 3 + 'time="' + str(pat["time"]) + '"></pattern>\n')
                
            f.write(TAB + '</moving-block>\n\n')
            
        for vec in self.pyHandle.level.vector_blocs:
            f.write(TAB + '<vector-block\n' + TAB * 2 + 'texture="' + 
                    vec.texture.split(os.sep)[-1] + '"\n')
                    
            f.write(TAB * 2 + 'vector="' + str(vec.vector[0]) + ' ' + 
                    str(vec.vector[1])+'"\n')
                    
            f.write(TAB * 2 + 'relative="'+str(vec.relative and 1 or 0)+'">\n')
            
            for rect in vec.rects:
                f.write(TAB * 2 + '<rect coords="'+str(rect[0])+' '+str(rect[1])+' '+str(rect[2])+' '+str(rect[3])+'"></rect>\n')
            f.write(TAB + '</vector-block>\n')
        f.write('</map>\n')
        f.close()

        f = open(self.pyHandle.xml_file, "r")
        self.xml_buffer.set_text(f.read())
        f.close()

if __name__ == "__main__":
    ule = USFLevelEditor()
    gtk.main()

