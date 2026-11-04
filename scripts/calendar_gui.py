#!/usr/bin/env python3
"""A minimal local GTK calendar; Waybar also shows the month on hover."""
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

win=Gtk.Window(title='AmethystOS · Calendar')
win.set_default_size(350,285)
win.set_border_width(15)
win.connect('destroy',Gtk.main_quit)
box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12)
win.add(box)
label=Gtk.Label(label='Calendar')
label.set_xalign(0)
box.pack_start(label,False,False,0)
calendar=Gtk.Calendar()
calendar.props.show_week_numbers = True
box.pack_start(calendar,True,True,0)
win.show_all()
Gtk.main()
