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

'''
A nice coverflow effect for images

'''

#standard imports
import pygame
import os

#our module
from usf.widgets.widget import Widget
from usf import loaders
from usf.font import fonts
CONFIG = loaders.get_config()


def get_text_transparent(name):
    text = loaders.text(name, fonts['mono']['10']).convert()
    #FIXME: the colorkey should be in a skin configuration file
    text.fill(pygame.color.Color("black"))
    text.set_colorkey(pygame.color.Color("black"))
    text.blit(loaders.text(name, fonts['mono']['22']), (0, 0))
    return text


class Coverflow(Widget):
    """
    The coverflow widget is used to display many image and choose one of
    the them.
    It should be big, about 800 * 275. This widget is animated and requires
    a lot of CPU.
    """
    #the animation() function wil be called each frame
    #FIXME: the animation speed souldn't depend of the computer
    animation_speed = True

    def __init__(self, values):
        super(Coverflow, self).__init__()
        self.values = values
        for value in self.values:
            #adding (false) size for the image, there will be updated later
            value.append((None, None))
            value.append(None)

        self.in_anim = False
        self.anim_state = ""
        self.advance = 0

        #compatibility with the others widget only
        self.state = False

        self.set_size((800, 230)) # FIXME hardcoded value
        self.center_size = (self.sizex(195), self.sizey(120))
        self.posy_center = self.sizey(60)
        self.foreground = loaders.image(
                os.path.join(CONFIG.sys_data_dir,
                    "gui",
                    CONFIG.general['THEME'],
                    "coverflow",
                    "foreground.png"),
                scale=(CONFIG.general["WIDTH"], CONFIG.general["HEIGHT"]))[0]

        self.frame = loaders.image(
                os.path.join(CONFIG.sys_data_dir,
                    "gui",
                    CONFIG.general['THEME'],
                    "coverflow",
                    "frame.png"),
                scale=(self.sizex(137), self.sizey(86)))

        self.surface = pygame.surface.Surface((self.width, self.height))
        self.index = 0
        self.text = get_text_transparent(self.values[self.index][0])
        self.previous()
        self.load_main_frame()

        for value in self.values:
            size = loaders.image(value[1])[1]
            if size[3] > size[2]:
                value[2] = (
                        self.frame[1][2] - self.sizex(25),
                        size[3] * (
                            self.frame[1][2] - self.sizex(25)) / size[2])
            else:
                value[2] = (
                        size[2] * (
                            self.frame[1][3] - self.sizex(25)) / size[3],
                            self.frame[1][3] - self.sizey(25))

            value[3] = (self.frame[1][2] / 2 - value[2][0]/2,
                        self.frame[1][3] / 2 - value[2][1]/2)

        self.need_update = True
        self.screen = pygame.display.get_surface()

    def draw(self):
        """
        Draw the widget, the surface will be redrawed if the widget is animated.
        You can force redrawing by set need_update to True.
        """
        x, y = (self.parentpos[0] + self.x, self.parentpos[1] + self.y)
        self.pos = self.width/2 - self.main_frame.get_width()/2 + self.advance
        self.draw_main()
        self.draw_right()
        self.draw_left()
        reflection = pygame.transform.flip(self.surface, False, True)
        reflection.set_colorkey(pygame.color.Color("black"))
        #reflection.set_alpha(20)
        self.screen.blit(reflection, (0, self.sizey(100)))
        self.screen.blit(self.text, (
            x + self.width/2 - self.text.get_width()/4,
            y + self.sizey(30)))

        self.screen.blit(self.foreground, (0, 0))
        self.need_update = False
        if self.in_anim:
            self.start_anim()

    def draw_main(self):
        """
        Draw the selected image, it is bigger than the other and in the center
        """
        x, y = (self.parentpos[0] + self.x, self.parentpos[1] + self.y)
        #main frame
        self.screen.blit(self.main_frame, (x + self.pos, y + self.posy_center))
        self.screen.blit(loaders.image(
            self.values[self.index][1],
            scale=self.center_image)[0], (
                x + self.pos + self.center_image_indent[0],
                y + self.posy_center  + self.center_image_indent[1]))

        self.pos += self.main_frame.get_width()

    def draw_right(self):
        """
        Draw three small image at right.
        """
        x, y = (self.parentpos[0] + self.x, self.parentpos[1] + self.y)
        for i in range(
                self.index - len(self.values) + 1,
                self.index - len(self.values) + 4):

            self.screen.blit(self.frame[0], (x + self.pos, y + self.sizey(82)))
            self.screen.blit(loaders.image(
                self.values[i][1],
                scale=self.values[i][2])[0], (
                    x + self.pos + self.values[i][3][0],
                    y + self.sizey(82) + self.values[i][3][1]))

            self.pos += self.frame[1][2]

    def draw_left(self):
        """
        Draw three small image at left.
        """
        x, y = (self.parentpos[0] + self.x, self.parentpos[1] + self.y)
        #at left now
        self.pos = (
                self.width/2
                - self.main_frame.get_width()/2
                - self.frame[1][2] * 3
                + self.advance)

        for i in range(self.index - 3, self.index):
            self.screen.blit(self.frame[0], (x + self.pos, y + self.sizey(82)))
            self.screen.blit(loaders.image(
                self.values[i][1],
                scale=self.values[i][2])[0], (
                    x + self.pos + self.values[i][3][0],
                    y + self.sizey(82) + self.values[i][3][1]))

            self.pos += self.frame[1][2]

    def next(self):
        """
        Select the next item.
        """
        self.index = (self.index - 1) % len(self.values)
        self.text = get_text_transparent(self.values[self.index][0])

    def previous(self):
        """
        Select the previous item.
        """
        self.index = (self.index + 1) % len(self.values)
        self.text = get_text_transparent(self.values[self.index][0])

    def handle_mouse(self, event):
        """
        This function handle all mouse events which are on the widget.
        """
        if not self.in_anim:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x = event.dict['pos'][0]
                # y = event.dict['pos'][1] #
                if x > self.width/2 + self.frame[1][2] / 2:
                    self.launch_anim(False)
                elif x < self.width/2 - self.frame[1][2] / 2:
                    self.launch_anim(True)
        return False, False

    def launch_anim(self, direction):
        """ start a translation animation in the direction
        """
        #self.last_c_update = time.time()
        self.anim_state = "start"
        self.last_index = self.index
        self.in_anim = True
        self.sens = direction

    def animation(self):
        """ update the animation
        """
        if self.in_anim:
            if self.anim_state == "start" or self.anim_state == "slide":
                if self.center_size[0] - self.sizex(10) > self.sizey(137):
                    w = self.center_size[0] - self.sizex(30)
                    h = self.center_size[1] * w / self.center_size[0]
                    #self.advance += self.sizex(5)
                    self.text.set_alpha(self.text.get_alpha() - 50)

                else:
                    self.anim_state = "slide"
                    self.text.set_alpha(0)
                    w = self.sizey(137)
                    h = self.sizey(86)

                self.posy_center = self.sizey(125) - h/2
                self.center_size = (w, h)
                self.load_main_frame()
                if self.sens:
                    if self.advance + 40 < self.frame[1][2]:
                        self.advance += 40
                    else:
                        self.advance = self.frame[1][2]
                        self.anim_state = "change"
                else:
                    if self.advance - 40 > - (self.frame[1][2]):
                        self.advance -= 40
                    else:
                        self.advance = - self.frame[1][2]
                        self.anim_state = "change"

            elif self.anim_state == "change":
                if self.sens:
                    self.next()
                else:
                    self.previous()
                self.text.set_alpha(0)
                self.advance = 0
                self.anim_state = "end"

            elif self.anim_state == "end":
                if self.center_size[0] < self.sizey(195):
                    w = self.center_size[0] + self.sizex(30)
                    h = self.center_size[1] * w / self.center_size[0]
                    #self.advance -= self.sizex(5)
                    self.text.set_alpha(self.text.get_alpha() + 50)

                else:
                    w = self.sizex(195)
                    h = self.sizey(120)
                    self.text.set_alpha(250)
                    #self.in_anim = False
                    self.anim_state = ""
                    self.advance = 0

                self.posy_center = self.sizey(125) - h/2
                self.center_size = (w, h)
                self.load_main_frame()
                self.need_update = True

            elif self.anim_state == "":
                self.in_anim = False
                self.need_update = True


    def handle_keys(self, event):
        """ manage keyboard input events
        """
        if (
                event.dict["key"] == pygame.K_DOWN or
                event.dict["key"] == pygame.K_UP) and not self.state:
            self.state = True
            return False, self

        if event.dict["key"] == pygame.K_RETURN:
            return self, self

        if not self.in_anim and (event.dict["key"] == pygame.K_LEFT
                or event.dict["key"] == pygame.K_RIGHT):

            if event.dict["key"] == pygame.K_LEFT:
                self.launch_anim(True)
            if event.dict["key"] == pygame.K_RIGHT:
                self.launch_anim(False)
            return self, self

        self.state = False
        return False, False

    def load_main_frame(self):
        """ #FIXME get xapantu to document a little! :P
        """
        self.main_frame = loaders.image(os.path.join(CONFIG.sys_data_dir,
            "gui",
            CONFIG.general['THEME'],
            "coverflow",
            "frame.png"),
            scale=self.center_size)[0]

        img = loaders.image(self.values[self.index][1])[0]

        #keep the image ratio
        if img.get_height() > img.get_width():
            self.center_image = (
                    self.main_frame.get_width() - self.sizex(25),
                    img.get_height() * (self.main_frame.get_width() -
                        self.sizex(25)) / img.get_width())
        else:
            self.center_image = (
                    img.get_width() * (
                        self.main_frame.get_height() - self.sizey(25))
                    / img.get_height(),
                self.main_frame.get_height()- self.sizey(25))

        self.center_image_indent = (
                self.main_frame.get_width()/2 - self.center_image[0]/2,
                self.main_frame.get_height()/2 - self.center_image[1]/2)

    def get_value(self):
        """ return the currently selected value
        """
        return self.values[self.index][0]

    def sizex(self, x):
        """
        This method is used to get the real size of an element. All size in the
        code above are for a widget size = 800*275. So, if the size is
        different, this function modify it.  This function is used for the x
        axis. Use sizey for y axis.
        """
        return x * self.width / 800

    def sizey(self, y):
        """
        Same as sizex, but for the y axis.
        """
        return y * self.height / 275

