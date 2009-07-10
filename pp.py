#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
Gtk pixel color picker
Copyright (C) 2009  Matías Aguirre

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import pygtk
pygtk.require("2.0")
from gtk import main_quit, Window, WINDOW_TOPLEVEL, Button, DrawingArea, \
                Label, Table, main, WINDOW_POPUP
from gtk.gdk import colormap_get_system, POINTER_MOTION_MASK, \
                    BUTTON_PRESS_MASK, pointer_ungrab, Pixbuf, \
                    COLORSPACE_RGB, get_default_root_window, pointer_grab, \
                    GRAB_SUCCESS


TITLE = 'Point & Pick' 
SYS_COLORMAP = colormap_get_system()
WHITE_RGB = (255, 255, 255)
GRAB_MASK = POINTER_MOTION_MASK | BUTTON_PRESS_MASK


def rgb_to_string(rgb):
    """Taks an rgb tuple and returns it hex string"""
    return "#" + ''.join('%02x' % c for c in rgb)


class PointAndPick(object):
    def __init__(self, title=TITLE, level=WINDOW_TOPLEVEL, on_exit=None):
        self.title = title
        self.grabbing = False
        self.events = []
        self.rgb = WHITE_RGB
        self.on_exit = on_exit

        self.window = Window(level)
        self.window.set_title(title)
        self.window.set_resizable(True)
        self.window.add_events(POINTER_MOTION_MASK)
        self.window.set_default_size(350, 150)
        self.colors = []

        grab_btn = Button('Grab')
        grab_btn.connect_object('clicked', self.toggle_grab, self.window)
        self.grab_btn = grab_btn

        exit_btn = Button('Exit')
        exit_btn.connect_object('clicked', self.destroy, self.window)

        drawing = DrawingArea()
        drawing.connect_object('expose_event', self.do_expose, self.window)
        self.drawing = drawing

        label = Label(rgb_to_string(WHITE_RGB))
        self.label = label

        table = Table(2, 2, True)
        table.attach(self.drawing, 0, 1, 0, 1)
        table.attach(label,   0, 1, 1, 2)
        table.attach(grab_btn, 1, 2, 0, 1)
        table.attach(exit_btn, 1, 2, 1, 2)
        self.window.add(table)

    def show(self):
        self.window.show_all()

    def destroy(self, *args, **kwargs):
        self.window.hide_all()
        self.window.do_destroy(self.window)
        if self.on_exit:
            self.on_exit()

    def toggle_grab(self, *args, **kwargs):
        """Toggle pointer grabbing"""
        { True: self.ungrab, False: self.grab }[self.grabbing]()

    def grab(self):
       """Grab pointer"""
       if pointer_grab(self.window.window, True, GRAB_MASK) == GRAB_SUCCESS:
            self.grabbing = True
            self.grab_btn.set_label('Ungrab')

            e = [ ('motion_notify_event', self.motion_notify_event),
                  ('button_press_event',  self.button_press_event) ]
            self.events = [ self.window.connect(n, h) for n, h in e ]

    def ungrab(self):
        """Ungrab pointer"""
        pointer_ungrab()
        while self.events:
            self.window.disconnect(self.events.pop())
        self.grabbing = False
        self.grab_btn.set_label('Grab')

    def do_expose(self, *args, **kwargs):
        """Expose the window"""
        gc_obj = self.drawing.window.new_gc()
        gc_obj.set_foreground(SYS_COLORMAP.alloc_color('black'))
        self.drawing.window.draw_rectangle(gc_obj, False, 10, 10, 100, 100)
        self.draw_color()

    def draw_color(self):
        """Drag the color box with the pixel under the mouse pointer"""
        gc_obj = self.drawing.window.new_gc()
        gc_obj.set_foreground(SYS_COLORMAP.alloc_color(rgb_to_string(self.rgb),
                              True))
        self.drawing.window.draw_rectangle(gc_obj, True, 11, 11, 99, 99)

    def motion_notify_event(self, win, event):
        """Mouse motion_notify_event handler"""
        pixbuf = Pixbuf(COLORSPACE_RGB, False, 8, 1, 1)
        root = get_default_root_window()
        xcoord, ycoord = event.get_root_coords()
        from_draw = pixbuf.get_from_drawable(root, root.get_colormap(),
                                             int(xcoord), int(ycoord),
                                             0, 0, 1, 1)
        pixel = from_draw.get_pixels_array()[0][0]
        self.rgb = (pixel[0], pixel[1], pixel[2])
        self.draw_color()
        self.label.set_label(rgb_to_string(self.rgb).upper())

    def button_press_event(self, *args, **kwargs):
        """Mouse button_press_event handler"""
        self.ungrab()


class PointAndPickPopup(PointAndPick):
    def __init__(self, *args, **kwargs):
        super(PointAndPickPopup, self).__init__(level=WINDOW_POPUP, *args, **kwargs)


if __name__ == '__main__':
    p = PointAndPickPopup(on_exit=main_quit)
    try:
        p.show()
        main()
    except KeyboardInterrupt:
        p.destroy()
