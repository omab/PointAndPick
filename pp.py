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
import gtk
from gtk import gdk


TITLE = 'Point & Pick' 
SYS_COLORMAP = gdk.colormap_get_system()
WHITE_RGB = (255, 255, 255)


def rgb_to_string(rgb):
    """Taks an rgb tuple and returns it hex string"""
    return "#" + ''.join('%02x' % c for c in rgb)


def pick_stop(*args, **kwargs):
    """Stop application"""
    gtk.main_quit()


def draw_color(win):
    """Drag the color box with the pixel under the mouse pointer"""
    gc_obj = win.pick_data['drawing'].window.new_gc()
    gc_obj.set_foreground(SYS_COLORMAP.\
            alloc_color(rgb_to_string(win.pick_data['rgb']), True))
    win.pick_data['drawing'].window.draw_rectangle(gc_obj, True,
                                                   11, 11, 99, 99)


def ungrab(win):
    """Ungrab mouse"""
    gdk.pointer_ungrab()
    while win.pick_data['events']:
        win.disconnect(win.pick_data['events'].pop())
    win.pick_data['grabbing'] = False
    win.pick_data['button1'].set_label('Grab')


def motion_notify_event(win, event):
    """Mouse motion_notify_event handler"""
    if event.type.value_nick == "button-press":
        ungrab(win)
    else:
        pixbuf = gdk.Pixbuf(gdk.COLORSPACE_RGB, False, 8, 1, 1)
        root = gdk.get_default_root_window()
        xcoord, ycoord = event.get_root_coords()
        from_draw = pixbuf.get_from_drawable(root, root.get_colormap(),
                                             int(xcoord), int(ycoord),
                                             0, 0, 1, 1)
        pixel = from_draw.get_pixels_array()[0][0]
        win.pick_data['rgb'] = (pixel[0], pixel[1], pixel[2])
        draw_color(win)
        win.pick_data['label'].\
            set_label(rgb_to_string(win.pick_data['rgb']).upper())


def grab_ungrab(win):
    """Toggle pointer grabbing status"""
    if win.pick_data['grabbing']:
        ungrab(win)
    else:
        if gdk.pointer_grab(win.window, True,
           gdk.POINTER_MOTION_MASK|gdk.BUTTON_PRESS_MASK) == gdk.GRAB_SUCCESS:
            win.pick_data['grabbing'] = True
            win.pick_data['button1'].set_label('Ungrab')
            win.pick_data['events'] = [ win.connect(e, motion_notify_event)
                                         for e in ('motion_notify_event',
                                                   'button_press_event') ]


def do_expose(win, *args, **kwargs):
    """Expose the window"""
    drawing = win.pick_data['drawing']
    gc_obj = drawing.window.new_gc()
    gc_obj.set_foreground(SYS_COLORMAP.alloc_color('black'))
    drawing.window.draw_rectangle(gc_obj, False, 10, 10, 100, 100)
    draw_color(win)


def init_win():
    """Initialize main window with it's widgets"""
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title(TITLE)
    window.connect('destroy', pick_stop)
    window.add_events(gdk.POINTER_MOTION_MASK)

    button1 = gtk.Button('Grab')
    button1.connect_object('clicked', grab_ungrab, window)

    button2 = gtk.Button('Exit')
    button2.connect_object('clicked', pick_stop, window)

    drawing = gtk.DrawingArea()
    drawing.connect_object('expose_event', do_expose, window)

    label = gtk.Label(rgb_to_string(WHITE_RGB))

    table = gtk.Table(2, 2, True)
    table.attach(drawing, 0, 1, 0, 1)
    table.attach(label,   0, 1, 1, 2)
    table.attach(button1, 1, 2, 0, 1)
    table.attach(button2, 1, 2, 1, 2)
    window.add(table)

    for item in (button1, button2, drawing, label, table, window):
        item.show()

    data = { 'events': [], 'rgb': WHITE_RGB,
             'grabbing': False, 'button1': button1,
             'label': label, 'drawing': drawing, }
    setattr(window, 'pick_data', data)


def pick_start():
    """Start picker"""
    init_win()
    gtk.main()


if __name__ == '__main__':
    try:
        pick_start()
    except KeyboardInterrupt:
        pick_stop()
