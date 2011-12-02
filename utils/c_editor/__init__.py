#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os

import pygtk
pygtk.require('2.0')
import gtk
required = (2, 16, 0)
assert gtk.ver >= required,\
'You need to upgrade PyGTK, at least version %d.%d.%d is required.' % required

from gettext import gettext as _

from color import color
from project import CharacterProject as CP

CHARACTER_PATH = '../data/characters/'

def validate_xml(xml_path):
    '''Validate form of xml file'''
    return True


class Menu:
    ui = '''<ui>
    <menubar name="Menu_Bar">
        <menu action="File">
            <menuitem action="New"/>
            <menuitem action="Save"/>
            <menuitem action="Reload"/>
            <menuitem action="Quit"/>
        </menu>
        <menu action="Help">
            <menuitem action="About"/>
        </menu>
    </menubar>
    <toolbar name="ToolBar">
        <toolitem name="New character" action="New"/>
        <toolitem name="Save" action="Save"/>
        <toolitem name="Reload" action="Reload"/>
    </toolbar>
    </ui>'''

    def __init__(self):
        window = gtk.Window()
        window.set_title(_('Character Editor'))
        window.connect('destroy', lambda w: gtk.main_quit())
        window.set_size_request(800, 600)
        vbox = gtk.VBox()
        window.add(vbox)

        # UIManager
        ui = gtk.UIManager()

        # shortcuts group
        shortcut_g = ui.get_accel_group()
        window.add_accel_group(shortcut_g)

        # ActionGroup
        self.actions_g = gtk.ActionGroup('Menu')

        # actions
        self.actions_g.add_actions([
            ('File', None, 'File'),
            ('New', gtk.STOCK_NEW, _('New'),
                None, _('Create new character'), self.new),
            ('Save', gtk.STOCK_SAVE, _('Save'),
                None, _('Save character'), self.save),
            ('Reload', gtk.STOCK_REFRESH, _('Reload'),
                'F5', _("Reload the current file"), self.reload_file),
            ('Quit', gtk.STOCK_QUIT,
                '_Quit', None, 'Quit program', self.quit),
            ('Help', None, '_Help'),
            ('About', None, '_About')])

        self.actions_g.get_action('Quit').set_property('short-label', '_Quit')

        ui.insert_action_group(self.actions_g, 0)

        ui.add_ui_from_string(self.ui)

        menu_bar = ui.get_widget('/Menu_Bar')
        vbox.pack_start(menu_bar, False)

        toolbar = ui.get_widget('/ToolBar')
        vbox.pack_start(toolbar, False)

        character_s = gtk.combo_box_new_text()

        #search character project
        first_character = None
        for path in os.listdir(CHARACTER_PATH):
            xml_path = CHARACTER_PATH + path +'/' + path +'.xml'
            if not os.path.isfile(xml_path):
                color(_("project directory '" + path \
                    + "' don't use xml file!"), 'red')
                continue
            if not validate_xml(xml_path):
                color(_("project directory " + path \
                    + " use an incorrect xml file!"), 'red')
                continue
            if first_character == None:
                first_character = xml_path
            character_s.append_text(path)

        character_s.set_active(0)

        # get movements list
        cp = CP(first_character)
        movements = gtk.combo_box_new_text()
        for mov in cp.movements:
            movements.append_text(mov)

        movements.set_active(0)

        self.image = gtk.Image()
        self.image.set_from_file(cp.get_picture(movements.get_active()))
        self.image.show()

        character_s.connect('changed', self.character_s)
        movements.connect('changed', self.movements)

        vbox.pack_start(character_s, False)
        vbox.pack_start(movements, False)
        vbox.pack_start(self.image, False)

        window.show_all()
        return

    def about(self, action):
        # TODO : about window
        return

    def new(self, action):
        pass

    def save(self, action):
        pass

    def reload_file(self, action):
        pass

    def quit(self, b):
        #TODO : question if the xml should be save
        gtk.main_quit()

    def character_s(self, action):
        print 'cool'
        action.get_property("active")

    def movements(self, action):
        pass

def main():
    Menu()
    gtk.main()