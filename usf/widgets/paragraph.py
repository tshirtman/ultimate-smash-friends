################################################################################
# copyright 2010 Lucas Baudin <xapantu@gmail.com>                              #
#                                                                              #
# This file is part of Ultimate Smash Friends.                                 #
#                                                                              #
# Ultimate Smash Friends is free software: you can redistribute it and/or      #
# modify it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or (at your   #
# option) any later version.                                                   #
#                                                                              #
# Ultimate Smash Friends is distributed in the hope that it will be useful, but#
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or#
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# You should have received a copy of the GNU General Public License along with #
# Ultimate Smash Friends.  If not, see <http://www.gnu.org/licenses/>.         #
################################################################################

from os.path import join

import pygame

from usf.widgets.widget import Widget

from usf import CONFIG, loaders
from usf.font import fonts
from usf.subpixel.subpixelsurface import SubPixelSurface


class Paragraph(Widget):
    """
    A simple paragraph widget. It reads a text which is in the
    data/text directory. It include a scroll bar but doesn't support
    (yet) auto word wrap.
    """

    animation_speed = 1/30.0
    def __init__(self, path):
        super(Paragraph, self).__init__()
        self.defil = 0
        self.state = False
        self.slider_y = 0
        self.hover = False
        self.auto_scroll = True

        text = open(join(CONFIG.system_path, path), 'r').readlines()
        text_height = loaders.text("", fonts['mono']['normal']).get_height()

        #the slider (at left)
        self.width_slider = 34
        self.height_slider = 125
        self.pos_slider = self.width / 20 * 19

        #the main surface
        self.width = 500 #XXX hardcoded values
        self.height = 125 #XXX hardcoded values
        self.surface = pygame.surface.Surface((self.width, self.height))

        #create the surface whiwh will contain _all_ the text
        width = self.width - self.width_slider * 2
        if width < 0:
            width = 0
        self.surface_text = pygame.surface.Surface(
                (width, len(text) * text_height))

        #draw all the text into the surface
        for i, t in enumerate(text):
            self.surface_text.blit(
                    loaders.text(
                        t.replace('\n', ""),
                        fonts['mono']['normal']),
                    (0, text_height * i))

        self.slider = SubPixelSurface(loaders.image(
            join(
                CONFIG.system_path,
                "gui",
                CONFIG.general.THEME,
                "sliderh_center.png"),
            scale=(self.width_slider, self.height_slider))[0], x_level=4)

    def update_defil(self):
        """
        Update the position of the scroll bar.
        """
        self.slider_y = self.defil*(self.height - self.height_slider)/100

    def draw(self):
        #clear the surface
        #draw the text
        x = self.parentpos[0] + self.x
        y = self.parentpos[1] + self.y
        mask = pygame.surface.Surface((self.width, self.height))
        mask.blit(
                self.surface_text,
                (100,
                    -(self.defil * (
                    self.surface_text.get_height() - self.height)/100)))

        mask.set_colorkey(pygame.color.Color("black"))
        self.screen.blit(mask, (x, y))
        del mask

        #the slider background
        self.screen.blit(loaders.image(join(CONFIG.system_path,
            "gui",
            CONFIG.general.THEME,
            "sliderh_background.png"),
            scale=(self.width_slider, self.height))[0],
            (x + self.pos_slider, y))

        #the slider center
        if self.hover:
            slider_center = "sliderh_center_hover.png"
        else:
            slider_center = "sliderh_center.png"

        self.screen.blit(self.slider.at(self.pos_slider, self.slider_y),
                          (x + self.pos_slider, y + self.slider_y))

        #foreground
        self.screen.blit(loaders.image(join(CONFIG.system_path,
            "gui",
            CONFIG.general.THEME,
            "paragraph_foreground.png"),
            scale=(self.width - self.width_slider*2, self.height))[0],
            (x, y))

        self.start_anim()

    def handle_mouse(self, event):
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]

        #to disable auto scrolling
        if event.type != pygame.MOUSEMOTION:
            self.auto_scroll = False

        if self.state:
            #relative position
            x -= self.parentpos[0] + self.x
            y -= self.parentpos[1] + self.y

        if event.type == pygame.MOUSEBUTTONUP:
            self.state = False
            return self, False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            #scroll button (up)
            if event.dict['button'] == 4:
                if 0 <= self.defil - 5 <= 100:
                    self.defil -= 5
                else:
                    self.defil = 0
            #scroll button (down)
            if event.dict['button'] == 5:
                if 0 <= self.defil + 5 <= 100:
                    self.defil += 5
                else:
                    self.defil = 100
            self.update_defil()

        #left click or mouse hover
        if (
                (event.type == pygame.MOUSEBUTTONDOWN and
                    event.dict['button'] == 1) or
                event.type == pygame.MOUSEMOTION):
            if (
                    self.pos_slider < event.dict['pos'][0] < self.width and
                    self.slider_y < event.dict['pos'][1] < (
                        self.slider_y + self.height_slider)):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.diff_pointer_slider = y - self.slider_y
                    self.state = True
                self.hover = True
                #return False, self
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.state = False
                #self.update_defil()
                return False, False
            elif not self.state:
                self.hover = False

        #if the mouse move the slider
        if self.state and (event.type == pygame.MOUSEMOTION or
                           event.type == pygame.MOUSEBUTTONDOWN):
            y -= self.diff_pointer_slider
            if 0 <= y <= (self.height - self.height_slider):
                self.defil = y * 100 / (self.height - self.height_slider)
            elif y <= 0:
                self.defil = 0
            else:
                self.defil = 100
            self.update_defil()

            return False, self

        return False, False

    def animation(self):
        """
        This function is used for auto scroll.
        It is called by the start_anim method which is in the
        Widget class.
        """
        if self.defil < 100 and self.auto_scroll:
            self.defil += 0.15
            self.update_defil()


