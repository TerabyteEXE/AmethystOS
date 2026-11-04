#!/usr/bin/env python3
"""AmethystOS bar popovers — local information, no network service or telemetry.

Gtk-layer-shell anchors panels beneath the original Waybar when supported.
On systems without layer shell these become ordinary small floating windows.
"""
from __future__ import annotations
from datetime import datetime
import getpass
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from ui_style import appearance as ui_appearance, install_override, window_size, workarea_size, px

MODES = ('calendar', 'audio', 'network', 'bluetooth', 'settings')


def read_output(args, timeout=2):
    """Read a small piece of local state; never invoke a shell."""
    if not shutil.which(args[0]):
        return ''
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                                check=False)
        return result.stdout.strip() if result.returncode == 0 else ''
    except (OSError, subprocess.TimeoutExpired):
        return ''


def volume_percent():
    output = read_output(['wpctl','get-volume','@DEFAULT_AUDIO_SINK@'])
    match = re.search(r'\b(\d+(?:\.\d+)?)\b',output)
    return max(0,min(100,round(float(match[1])*100))) if match else None


def active_wifi():
    output = read_output(['nmcli','-t','-f','IN-USE,SSID','dev','wifi'])
    for line in output.splitlines():
        if line.startswith('*:'):
            return line[2:] or 'Connected to Wi-Fi'
    return None


def bluetooth_powered():
    output = read_output(['bluetoothctl','show'])
    match = re.search(r'^\s*Powered:\s*(yes|no)\s*$', output, flags=re.MULTILINE)
    return None if not match else (match[1] == 'yes')


def appearance_state(home=Path.home()):
    try:
        data = json.loads((home/'.local/state/amethystos-base-v1/appearance.json').read_text())
        return {'theme':data.get('theme','dark'), 'scale':data.get('scale',100)}
    except (OSError, ValueError, TypeError):
        return {'theme':'dark','scale':100}


def spawn(*args):
    if not (shutil.which(args[0]) or Path(args[0]).is_file()):
        return False
    try:
        subprocess.Popen(args, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
        return True
    except (OSError, ValueError):
        return False


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=MODES)
    args=parser.parse_args()
    try:
        import gi
        gi.require_version('Gtk','3.0')
        from gi.repository import Gtk,Gdk,GLib,GdkPixbuf
    except (ImportError,ValueError):
        print('AmethystOS panel requires GTK3/PyGObject.',file=sys.stderr)
        return 2
    try:
        gi.require_version('GtkLayerShell','0.1')
        from gi.repository import GtkLayerShell
    except (ImportError, ValueError):
        GtkLayerShell=None

    GLib.set_prgname('amethyst-bar-popup')
    home=Path.home()
    preferences=appearance_state(home)
    theme, ui_scale = ui_appearance(home)
    mode=args.mode
    win=Gtk.Window(title=f'AmethystOS · {mode.title()}')
    win.set_name('amethyst-bar-popup')
    width, _ = window_size(324, 375, ui_scale, *workarea_size(Gdk))
    win.set_default_size(width,-1)
    win.set_resizable(False)
    win.set_border_width(px(16, ui_scale))
    win.connect('destroy',Gtk.main_quit)
    def escape(_widget,event):
        if Gdk.keyval_name(event.keyval)=='Escape':
            win.destroy()
            return True
        return False
    win.connect('key-press-event',escape)
    if GtkLayerShell is not None:
        try:
            GtkLayerShell.init_for_window(win)
            if hasattr(GtkLayerShell, 'set_namespace'):
                GtkLayerShell.set_namespace(win, 'amethyst-popup')
            GtkLayerShell.set_layer(win,GtkLayerShell.Layer.OVERLAY)
            GtkLayerShell.set_anchor(win,GtkLayerShell.Edge.TOP,True)
            GtkLayerShell.set_margin(win,GtkLayerShell.Edge.TOP,39)
            # Waybar's original grouping is preserved; offsets approximate
            # the right-side widget positions on typical displays.
            offsets={'calendar':None,'audio':320,'network':190,'bluetooth':115,'settings':38}
            if offsets[mode] is not None:
                GtkLayerShell.set_anchor(win,GtkLayerShell.Edge.RIGHT,True)
                GtkLayerShell.set_margin(win,GtkLayerShell.Edge.RIGHT,offsets[mode])
            GtkLayerShell.set_exclusive_zone(win,0)
            if hasattr(GtkLayerShell,'KeyboardMode'):
                GtkLayerShell.set_keyboard_mode(win,GtkLayerShell.KeyboardMode.ON_DEMAND)
        except Exception as exc:
            print('AmethystOS: bar anchoring unavailable:',exc,file=sys.stderr)
    screen=Gdk.Screen.get_default()
    if screen is not None:
        rgba=screen.get_rgba_visual()
        if rgba is not None and screen.is_composited():
            win.set_visual(rgba)
    css=home/'.local/share/amethystos/popups'/f'{theme}.css'
    if css.is_file():
        try:
            provider=Gtk.CssProvider()
            provider.load_from_path(str(css))
            Gtk.StyleContext.add_provider_for_screen(screen,provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        except GLib.Error as exc:
            print('AmethystOS popup CSS:',exc,file=sys.stderr)

    sizing_provider = install_override(Gtk, Gdk, 'popup', ui_scale)
    box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=px(10, ui_scale))
    box.set_name('amethyst-popup-content')
    win.add(box)
    row=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=8)
    title=Gtk.Label(label=mode.capitalize())
    title.set_name('amethyst-popup-title')
    title.set_xalign(0)
    row.pack_start(title,True,True,0)
    time_label=Gtk.Label(label=datetime.now().strftime('%a %-d %b'))
    time_label.set_name('amethyst-popup-muted')
    row.pack_end(time_label,False,False,0)
    box.pack_start(row,False,False,3)

    def label(value,muted=False):
        field=Gtk.Label(label=value)
        field.set_line_wrap(True)
        field.set_xalign(0)
        if muted:
            field.set_name('amethyst-popup-muted')
        box.pack_start(field,False,False,0)
        return field

    def button(text,*command,close=True):
        item=Gtk.Button(label=text)
        item.set_relief(Gtk.ReliefStyle.NONE)
        def clicked(_):
            ok=spawn(*command)
            if not ok:
                note.set_text(f'Unable to open {text}. Check installed applications.')
                note.show()
            elif close:
                win.destroy()
        item.connect('clicked',clicked)
        box.pack_start(item,False,False,0)
        return item

    local_bin=home/'.local/bin'
    label(f'Hello, {getpass.getuser()}',muted=True)
    note=label('',muted=True)
    note.set_no_show_all(True)
    if mode=='calendar':
        label(datetime.now().strftime('%A, %B %-d, %Y'))
        cal=Gtk.Calendar()
        cal.props.show_week_numbers=True
        box.pack_start(cal,True,True,0)
        reset=Gtk.Button(label='Back to today')
        def today(_):
            dt=datetime.now()
            cal.select_month(dt.month-1,dt.year)
            cal.select_day(dt.day)
        reset.connect('clicked',today)
        box.pack_start(reset,False,False,0)
        if shutil.which('gnome-calendar'):
            button('Open Calendar app','gnome-calendar')
        label('Dates shown in your local time zone.',muted=True)
    elif mode=='audio':
        current=volume_percent()
        label('Default audio output')
        value=label(f'Volume: {current}%' if current is not None else 'Volume not available',muted=True)
        volume=Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,100,5)
        volume.set_value(current if current is not None else 50)
        volume.set_sensitive(current is not None)
        volume.set_draw_value(False)
        def changed(slider):
            amount=int(slider.get_value())
            value.set_text(f'Volume: {amount}%')
            if shutil.which('wpctl'):
                subprocess.run(['wpctl','set-volume','@DEFAULT_AUDIO_SINK@',f'{amount}%'],check=False)
        volume.connect('value-changed',changed)
        box.pack_start(volume,False,False,0)
        if shutil.which('wpctl'):
            button('Toggle mute','wpctl','set-mute','@DEFAULT_AUDIO_SINK@','toggle',close=False)
        button('Audio settings',str(local_bin/'amethyst-settings'),'devices')
    elif mode=='network':
        wifi=active_wifi()
        label('Wi-Fi: '+wifi if wifi else 'Wi-Fi not connected or not available')
        if shutil.which('nm-connection-editor'):
            button('Manage connections','nm-connection-editor')
        button('Network settings',str(local_bin/'amethyst-settings'),'network')
    elif mode=='bluetooth':
        status=bluetooth_powered()
        label('Bluetooth: '+('On' if status else 'Off' if status is False else 'Unavailable'))
        if shutil.which('blueman-manager'):
            button('Manage devices','blueman-manager')
        button('Bluetooth settings',str(local_bin/'amethyst-settings'),'bluetooth')
    else:
        label('AmethystOS · '+theme.capitalize()+' theme')
        label(f'UI scale: {preferences.get("scale",100)}%',muted=True)
        button('Appearance',str(local_bin/'amethyst-settings'),'appearance')
        button('Top bar layout',str(local_bin/'amethyst-settings'),'bar')
        button('Wallpapers',str(local_bin/'amethyst-wallpapers'))
        button('All settings',str(local_bin/'amethyst-settings'))
    win.show_all()
    Gtk.main()
    return 0

if __name__=='__main__':
    sys.exit(main())
