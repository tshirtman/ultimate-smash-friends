#!/usr/bin/env python
#coding=utf-8
import os

from gettext import gettext as _

import pygtk
pygtk.require('2.0')
import gtk
required = (2, 16, 0)
assert gtk.ver >= required,\
_('You need to upgrade PyGTK, at least version %d.%d.%d is required.')\
% required

from color import color

from project import CharacterProject as CP
from remote import RemoteControl as RC, TimeLine as TM

CHARACTER_PATH = '../data/characters/'


def validate_xml(xml_path):
    '''Validate form of xml file'''
    return True


class Menu:
    def __init__(self):
        self.ui = open('c_editor/ui.xml', 'r').read()

        window = gtk.Window()
        window.set_title(_('Character Editor'))
        window.set_size_request(800, 600)
        self.vbox = gtk.VBox()
        window.add(self.vbox)

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
            xml_path = CHARACTER_PATH + path + '/' + path + '.xml'
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

        # zoom selector
        zoom = gtk.combo_box_new_text()
        self.zoom_sizes = [0.25, 0.5, 1, 2, 3]
        for size in self.zoom_sizes:
            zoom.append_text(str(int(size * 100)) + ' %')
        self.size = 1000
        zoom.set_active(2)

        self.timeline = TM(self.cp.get_frames())
        self.remote = RC(self.image, self.project_path, self.cp, self.timeline)
        self.remote.zoom = zoom
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
                None, _('go to last frame...'), self.remote.end)
            ])

        self.actions_g.get_action('Quit').set_property('short-label', '_Quit')

        ui.insert_action_group(self.actions_g, 0)

        ui.add_ui_from_string(self.ui)

        menu_bar = ui.get_widget('/Menu_Bar')
        self.vbox.pack_start(menu_bar, False)

        toolbar = ui.get_widget('/ToolBar')
        tool_item = gtk.ToolItem()
        tool_item.add(character_s)
        toolbar.insert(tool_item, 4)
        tool_item = gtk.ToolItem()
        tool_item.add(self.movements)
        toolbar.insert(tool_item, 5)

        self.vbox.pack_start(toolbar, False)

        self.vbox.pack_start(self.image, expand=True)

        self.vbox.pack_start(self.timeline, False)

        remoteC = ui.get_widget('/RemoteControl')
        tool_item = gtk.ToolItem()
        tool_item.add(zoom)
        remoteC.insert(tool_item, 5)
        self.vbox.pack_end(remoteC, False)

        character_s.connect('changed', self.__character_s)
        self.movements.connect('changed', self.__movements)
        zoom.connect('changed', self.__zoom)
        self.window = window
        window.show_all()
        window.connect('destroy', self.quit)
        #self.connect('event-after', gtk.main_quit)

    def main(self):
        gtk.main()

    def quit(self, b):
        ''' Graphical usage to quit application '''
        #TODO : question if the xml should be save
        gtk.main_quit()
        self.__del__()

    def __del__(self):
        ''' CTRL + C usage to quit application '''
        self.remote.__del__()

    def about(self, action):
        # TODO : about window
        return

    def new(self, action):
        pass

    def save(self, action):
        pass

    def reload_file(self, action):
        pass

    def __character_s(self, action):
        new_c = action.get_model()[action.get_property('active')][0]
        self.project_path = CHARACTER_PATH + new_c + '/'
        new_xml = self.project_path + new_c + '.xml'

        self.movements.get_model().clear()

        self.cp = CP(new_xml)
        for mov in self.cp.movements:
            self.movements.append_text(mov)

        self.movements.set_active(0)

        self.image.set_from_file(
            self.cp.get_picture(self.movements.get_active())
            )

        self.remote.img = self.image
        self.remote.project_path = self.project_path
        self.remote.frames = self.cp.get_frames()
        self.remote.stop(self.actions_g.get_action("Play"))
        self.remote.cp = self.cp

        self.__timeline()

    def __movements(self, action):
        self.image.set_from_file(
            self.cp.get_picture(action.get_active())
            )
        self.remote.img = self.image
        self.remote.project_path = self.project_path
        self.remote.frames = self.cp.get_frames()
        self.remote.stop(self.actions_g.get_action("Play"))
        self.remote.cp = self.cp

        self.__timeline()

    def __timeline(self):
        self.vbox.remove(self.timeline)
        self.timeline = TM(self.cp.get_frames(), self.size)
        self.remote.timeline = self.timeline
        self.vbox.pack_start(self.timeline, False)
        self.remote.create_frame(self.timeline.frames)
        self.remote.zoom.set_sensitive(True)
        #self.vbox.set_focus_child(self.timeline)

    def __zoom(self, action):
        self.size = self.zoom_sizes[action.get_active()] * 1000
        if not self.remote.frame.isAlive():
            frames = self.remote.timeline.frames
            inc = 0
            for frame in frames:
                if frame[3] == self.remote.frame.timeline.frame:
                    break
                inc += 1

            self.vbox.remove(self.timeline)
            self.timeline = TM(self.cp.get_frames(), self.size)
            self.remote.timeline = self.timeline
            self.remote.frame.timeline = self.timeline
            self.vbox.pack_start(self.timeline, False)
            self.remote.create_frame(self.timeline.frames)

            import itertools
            self.remote.travel(
                itertools.cycle(self.timeline.frames), len(frames) - inc - 1
                )


def main():
    menu = Menu()
    try:
        menu.main()
    except KeyboardInterrupt:
        menu.__del__()
