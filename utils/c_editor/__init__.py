#!/usr/bin/env python2
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
#import gobject
from project import CharacterProject as CP
from remote import RemoteControl as RC

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
        <separator expand="true"/>
    </toolbar>
    <toolbar name="RemoteControl">
        <toolitem name="Begin" action="Begin"/>
        <toolitem name="Previous" action="Previous"/>
        <toolitem name="Play" action="Play"/>
        <toolitem name="Next" action="Next"/>
        <toolitem name="End" action="End"/>
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
                self.project_path = CHARACTER_PATH + path + '/'
                first_character = xml_path
            character_s.append_text(path)

        character_s.set_active(0)

        # get movements list
        self.cp = CP(first_character)
        self.movements = gtk.combo_box_new_text()
        for mov in self.cp.movements:
            self.movements.append_text(mov)

        self.movements.set_active(0)

        self.image = gtk.Image()
        self.image.set_from_file(
            self.cp.get_picture(self.movements.get_active())
            )
        self.image.show()

        character_s.connect('changed', self.__character_s)
        self.movements.connect('changed', self.__movements)

        self.remote = RC(self.image, self.project_path, self.cp)
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
            ('About', None, '_About'),
            ('Begin', gtk.STOCK_MEDIA_REWIND, _('begin'),
                None, _('go to first frame...'), self.remote.begin),
            ('Previous', gtk.STOCK_MEDIA_PREVIOUS, _('previous'),
                None, _('go to previous frame...'), self.remote.previous),
            ('Play', gtk.STOCK_MEDIA_PLAY, _('Play'),
                None, _('Play animation'), self.remote.play),
            ('Next', gtk.STOCK_MEDIA_NEXT, _('Next'),
                None, _('go to next frame...'), self.remote.next),
            ('End', gtk.STOCK_MEDIA_FORWARD, _('End'),
                None, _('go to last frame...'), self.remote.end),
            ])

        self.actions_g.get_action('Quit').set_property('short-label', '_Quit')

        ui.insert_action_group(self.actions_g, 0)

        ui.add_ui_from_string(self.ui)

        menu_bar = ui.get_widget('/Menu_Bar')
        vbox.pack_start(menu_bar, False)

        toolbar = ui.get_widget('/ToolBar')
        tool_item = gtk.ToolItem()
        tool_item.add(character_s)
        toolbar.insert(tool_item, 4)
        tool_item = gtk.ToolItem()
        tool_item.add(self.movements)
        toolbar.insert(tool_item, 5)

        vbox.pack_start(toolbar, False)

        vbox.pack_start(self.image, expand=True)

        remoteC = ui.get_widget('/RemoteControl')
        vbox.pack_end(remoteC, False)

        self.remote.action = self.actions_g.get_action("Play")

        window.show_all()
        window.connect('destroy', self.quit)

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
        self.remote.__del__()
        gtk.main_quit()

    def __character_s(self, action):
        new_c = action.get_model()[action.get_property('active')][0]
        self.project_path = CHARACTER_PATH + new_c +'/'
        new_xml = self.project_path + new_c +'.xml'

        self.movements.get_model().clear()

        self.cp = CP(new_xml)
        for mov in self.cp.movements:
            self.movements.append_text(mov)

        self.movements.set_active(0)

        self.image.set_from_file(
            self.cp.get_picture(self.movements.get_active())
            )
        print 'delete?', self.project_path
        print self.remote
        self.remote.stop()
        self.remote.img = self.image
        self.remote.project_path = self.project_path
        self.remote.frames = self.cp.get_frames()

    def __movements(self, action):
        self.image.set_from_file(
            self.cp.get_picture(action.get_active())
            )
        self.remote.stop()
        self.remote.img = self.image
        self.remote.project_path = self.project_path
        self.remote.frames = self.cp.get_frames()

def main():
    Menu()
    gtk.main()
