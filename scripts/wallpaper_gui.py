#!/usr/bin/env python3
"""Small scrollable GTK3 image gallery for user and bundled wallpapers.

Uses only local images; does not make network requests or overwrite wallpaper
files. The image selected is applied through the existing set-wallpaper tool.
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

WALLDIR=Path.home()/'Pictures/wallpapers'
EXTS={'.png','.jpeg','.jpg','.webp'}

def wallpapers(folder=WALLDIR):
    if not folder.exists():return []
    return sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXTS),key=lambda p:p.name.casefold())

def main():
    if '--list' in sys.argv:
        for p in wallpapers():print(p)
        return 0
    import gi
    gi.require_version('Gtk','3.0')
    from gi.repository import Gtk,Gdk,GdkPixbuf
    win=Gtk.Window(title='AmethystOS · Wallpapers')
    win.set_default_size(860,570)
    win.set_border_width(14)
    win.connect('destroy',Gtk.main_quit)
    vbox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12)
    win.add(vbox)
    title=Gtk.Label(label='Wallpapers · double-click to apply, or select and press Apply')
    title.set_xalign(0)
    vbox.pack_start(title,False,False,0)
    scroller=Gtk.ScrolledWindow()
    scroller.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
    vbox.pack_start(scroller,True,True,0)
    model=Gtk.ListStore(GdkPixbuf.Pixbuf,str,str)
    for item in wallpapers():
        try:
            pixbuf=GdkPixbuf.Pixbuf.new_from_file_at_scale(str(item),180,110,True)
            model.append([pixbuf,item.name,str(item)])
        except Exception as exc:
            print('Skipping invalid image:',item,exc,file=sys.stderr)
    view=Gtk.IconView.new()
    view.set_model(model)
    view.set_pixbuf_column(0)
    view.set_text_column(1)
    view.set_item_width(195)
    view.set_selection_mode(Gtk.SelectionMode.SINGLE)
    view.set_margin(10)
    view.set_row_spacing(14)
    view.set_column_spacing(14)
    scroller.add(view)
    bottom=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=10)
    vbox.pack_start(bottom,False,False,0)
    feedback=Gtk.Label(label=f'{len(model)} wallpapers in {WALLDIR}')
    feedback.set_xalign(0)
    bottom.pack_start(feedback,True,True,0)
    def apply(*_):
        selected=view.get_selected_items()
        if not selected:return
        path=model[selected[0]][2]
        result=subprocess.run([str(Path.home()/'.local/bin/set-wallpaper'),'--file',path],capture_output=True,text=True)
        feedback.set_text('Applied '+Path(path).name if result.returncode==0 else 'Could not apply wallpaper: '+result.stderr.strip()[:120])
    def pick(*_):apply()
    view.connect('item-activated',pick)
    button=Gtk.Button(label='Apply Wallpaper')
    button.connect('clicked',apply)
    bottom.pack_end(button,False,False,0)
    # Arrow keys navigate thumbnails automatically in Gtk.IconView.
    style=Gtk.CssProvider()
    style.load_from_data(b'''window {background:#151923;color:#eeeaf6;} label{color:#e7e2f3;} button{border-radius:8px;} iconview{background:#171c29;}''')
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),style,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    win.show_all()
    Gtk.main();return 0

if __name__=='__main__':sys.exit(main())
