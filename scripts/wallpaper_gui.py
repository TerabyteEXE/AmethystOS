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
from ui_style import appearance as ui_appearance, install_override, window_size, workarea_size, px

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
    win.set_name('amethyst-wallpaper-gallery')
    theme, ui_scale = ui_appearance()
    win.set_default_size(*window_size(860,570,ui_scale,*workarea_size(Gdk)))
    win.set_border_width(px(14, ui_scale))
    win.connect('destroy',Gtk.main_quit)
    vbox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=px(12, ui_scale))
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
            pixbuf=GdkPixbuf.Pixbuf.new_from_file_at_scale(str(item),px(180,ui_scale),px(110,ui_scale),True)
            model.append([pixbuf,item.name,str(item)])
        except Exception as exc:
            print('Skipping invalid image:',item,exc,file=sys.stderr)
    view=Gtk.IconView.new()
    view.set_model(model)
    view.set_pixbuf_column(0)
    view.set_text_column(1)
    view.set_item_width(px(195,ui_scale))
    view.set_selection_mode(Gtk.SelectionMode.SINGLE)
    view.set_margin(px(10,ui_scale))
    view.set_row_spacing(px(14,ui_scale))
    view.set_column_spacing(px(14,ui_scale))
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
    css=Path.home()/'.local/share/amethystos/gallery'/f'{theme}.css'
    if css.exists():
        style=Gtk.CssProvider()
        style.load_from_path(str(css))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),style,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    sizing_provider=install_override(Gtk,Gdk,'gallery',ui_scale)
    win.show_all()
    Gtk.main();return 0

if __name__=='__main__':sys.exit(main())
