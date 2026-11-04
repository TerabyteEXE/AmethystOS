#!/usr/bin/env python3
"""Compact Waybar panel for AmethystOS.

Uses GtkLayerShell when available to anchor the surface below Waybar; otherwise
it becomes a normal small GTK window. Changes use existing user-space tools.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

MODES = ('calendar', 'audio', 'network', 'bluetooth', 'settings')


def run_command(*args):
    if not shutil.which(args[0]) and not Path(args[0]).exists():
        return False
    try:
        subprocess.Popen(args, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
        return True
    except (OSError, ValueError):
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=MODES)
    args = p.parse_args()
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, Gdk, GLib
    except (ImportError, ValueError):
        print('AmethystOS popup requires GTK3', file=sys.stderr)
        return 2
    try:
        gi.require_version('GtkLayerShell', '0.1')
        from gi.repository import GtkLayerShell
    except (ImportError, ValueError):
        GtkLayerShell = None
    GLib.set_prgname('amethyst-bar-popup')
    home = Path.home()
    mode = args.mode

    win = Gtk.Window(title=f'AmethystOS · {mode.title()}')
    win.set_name('amethyst-bar-popup')
    win.set_default_size(315, -1)
    win.set_resizable(False)
    win.set_border_width(15)
    win.connect('destroy', Gtk.main_quit)
    win.connect('key-press-event', lambda _, event: (win.destroy() or True) if Gdk.keyval_name(event.keyval)=='Escape' else False)
    if GtkLayerShell is not None:
        try:
            GtkLayerShell.init_for_window(win)
            GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
            GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.TOP, True)
            if mode != 'calendar':
                GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.RIGHT, True)
                GtkLayerShell.set_margin(win, GtkLayerShell.Edge.RIGHT, 26)
            GtkLayerShell.set_margin(win, GtkLayerShell.Edge.TOP, 38)
            GtkLayerShell.set_exclusive_zone(win, 0)
            if hasattr(GtkLayerShell, 'KeyboardMode'):
                GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.ON_DEMAND)
        except Exception as exc:
            print('AmethystOS: layer-shell positioning unavailable:', exc, file=sys.stderr)

    state = home/'.local/state/amethystos-base-v1/appearance.json'
    theme = 'dark'
    try:
        theme = json.loads(state.read_text()).get('theme', 'dark')
    except (OSError, ValueError, TypeError):
        pass
    css = home/'.local/share/amethystos/popups'/f'{theme}.css'
    if css.is_file():
        try:
            provider = Gtk.CssProvider()
            provider.load_from_path(str(css))
            Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
                                                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        except GLib.Error:
            pass
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    win.add(box)

    label = Gtk.Label(label=mode.title())
    label.set_xalign(0)
    label.set_name('amethyst-popup-title')
    box.pack_start(label, False, False, 0)

    def command_button(text, *command):
        btn = Gtk.Button(label=text)
        btn.connect('clicked', lambda *_: (run_command(*command), win.destroy()))
        box.pack_start(btn, False, False, 0)
        return btn

    script_bin = home/'.local/bin'
    if mode == 'calendar':
        cal = Gtk.Calendar()
        cal.props.show_week_numbers = True
        box.pack_start(cal, True, True, 0)
        command_button('Date and desktop settings', str(script_bin/'amethyst-settings'), 'desktop')
    elif mode == 'audio':
        current = 50
        try:
            p = subprocess.run(['wpctl','get-volume','@DEFAULT_AUDIO_SINK@'], capture_output=True, text=True, timeout=2)
            found = re.search(r'(\d+(?:\.\d+)?)', p.stdout)
            if found:
                current = max(0,min(100,round(float(found[1])*100)))
        except (OSError, subprocess.TimeoutExpired):
            pass
        value = Gtk.Label(label=f'Volume: {current}%')
        value.set_xalign(0)
        box.pack_start(value,False,False,0)
        volume = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        volume.set_value(current)
        volume.set_draw_value(False)
        def on_volume(slider):
            amount = int(slider.get_value())
            value.set_text(f'Volume: {amount}%')
            if shutil.which('wpctl'):
                subprocess.run(['wpctl','set-volume','@DEFAULT_AUDIO_SINK@',f'{amount}%'],check=False)
        volume.connect('value-changed', on_volume)
        box.pack_start(volume,True,True,0)
        command_button('Audio settings', str(script_bin/'amethyst-settings'), 'devices')
    elif mode == 'network':
        command_button('Network connections', str(script_bin/'amethyst-settings'), 'network')
        if shutil.which('nm-connection-editor'):
            command_button('Advanced network editor', 'nm-connection-editor')
    elif mode == 'bluetooth':
        command_button('Bluetooth devices', str(script_bin/'amethyst-settings'), 'bluetooth')
        if shutil.which('blueman-manager'):
            command_button('Bluetooth manager', 'blueman-manager')
    else:
        command_button('Appearance', str(script_bin/'amethyst-settings'), 'appearance')
        command_button('Top bar', str(script_bin/'amethyst-settings'), 'bar')
        command_button('Wallpapers', str(script_bin/'amethyst-wallpapers'))
        command_button('All settings', str(script_bin/'amethyst-settings'))

    win.show_all()
    Gtk.main()
    return 0


if __name__ == '__main__':
    sys.exit(main())
