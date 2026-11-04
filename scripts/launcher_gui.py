#!/usr/bin/env python3
"""AmethystOS unified launcher.

Uses installed desktop application metadata from GIO (not shell commands), and a
small explicit allowlist of built-in system actions. No internet or telemetry.
Gtk is imported only when the graphical program starts, so --list-actions works
on headless CI systems without GTK.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
import sys

CATEGORIES = ('All', 'Apps', 'Settings', 'Software', 'Wallpapers', 'System', 'Power')

@dataclass(frozen=True)
class Action:
    category: str
    name: str
    subtitle: str
    command: tuple[str, ...]
    icon: str = 'applications-system'

BIN = str(Path.home() / '.local/bin')
ACTIONS = (
    Action('Settings', 'Amethyst Settings', 'Desktop preferences', (f'{BIN}/amethyst-settings',), 'preferences-system'),
    Action('Settings', 'Appearance & themes', 'Light/Dark appearance and text size', (f'{BIN}/amethyst-settings', 'appearance'), 'preferences-desktop-theme'),
    Action('Settings', 'Top bar', 'Layout and visible widgets', (f'{BIN}/amethyst-settings', 'bar'), 'preferences-desktop'),
    Action('Settings', 'Display and workspaces', 'Monitor and Niri controls', (f'{BIN}/amethyst-settings', 'desktop'), 'video-display'),
    Action('Settings', 'Devices and connections', 'Network, audio, Bluetooth', (f'{BIN}/amethyst-settings', 'devices'), 'preferences-system'),
    Action('Software', 'Software', 'Install, remove, and update', (f'{BIN}/amethyst-settings', 'software'), 'system-software-install'),
    Action('Software', 'Install an application', 'Choose from curated Fedora and Flatpak packages', (f'{BIN}/amethyst-software', 'install'), 'system-software-install'),
    Action('Software', 'Remove an application', 'Review the removal before proceeding', (f'{BIN}/amethyst-software', 'remove'), 'edit-delete'),
    Action('Software', 'System updates', 'Review Fedora and user Flatpak updates', (f'{BIN}/amethyst-software', 'update'), 'software-update-available'),
    Action('Wallpapers', 'Wallpaper gallery', 'Browse and select your wallpapers', (f'{BIN}/amethyst-wallpapers',), 'preferences-desktop-wallpaper'),
    Action('System', 'Calendar', 'Month view', (f'{BIN}/amethyst-calendar',), 'x-office-calendar'),
    Action('System', 'System diagnostics', 'Open the diagnostics tools in Settings', (f'{BIN}/amethyst-settings', 'system'), 'utilities-system-monitor'),
    Action('Power', 'Power menu', 'Lock, sign out, reboot, shut down', (f'{BIN}/powermenu',), 'system-shutdown'),
)


def matches(category: str, query: str, actions=ACTIONS):
    q = query.casefold().strip()
    return [a for a in actions if (category == 'All' or a.category == category)
            and (not q or q in f'{a.name} {a.subtitle} {a.category}'.casefold())]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', choices=CATEGORIES, default='All')
    parser.add_argument('--list-actions', action='store_true', help='Print actions for headless validation')
    args = parser.parse_args()
    if args.list_actions:
        for a in ACTIONS:
            print(f'{a.category}\t{a.name}\t{a.subtitle}\t{" ".join(a.command)}')
        return 0
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, Gdk, Gio, GLib, Pango
    except (ImportError, ValueError) as exc:
        print(f'AmethystOS launcher needs GTK3/PyGObject: {exc}', file=sys.stderr)
        return 2

    GLib.set_prgname('amethyst-launcher')
    GLib.set_application_name('AmethystOS Search')

    class Launcher(Gtk.Window):
        def __init__(self):
            super().__init__(title='AmethystOS')
            self.set_name('amethyst-launcher')
            self.set_default_size(690, 510)
            self.set_size_request(570, 410)
            self.set_position(Gtk.WindowPosition.CENTER)
            self.connect('destroy', Gtk.main_quit)
            self.connect('key-press-event', self.on_key)
            self.category = args.category
            self.apps = []
            self.row_actions = {}
            self.load_apps()
            self.provider = Gtk.CssProvider()
            theme = 'dark'
            try:
                import json
                prefs = Path.home()/'.local/state/amethystos-base-v1/appearance.json'
                theme = json.loads(prefs.read_text()).get('theme', 'dark')
            except (OSError, ValueError, TypeError):
                pass
            css = Path.home()/'.local/share/amethystos/launcher'/f'{theme}.css'
            if css.is_file():
                try:
                    self.provider.load_from_path(str(css))
                    Gtk.StyleContext.add_provider_for_screen(self.get_screen(), self.provider,
                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                except GLib.Error as exc:
                    print('Amethyst launcher CSS error:', exc, file=sys.stderr)

            root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            self.add(root)
            top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            top.set_border_width(16)
            icon = Gtk.Image.new_from_icon_name('system-search', Gtk.IconSize.MENU)
            top.pack_start(icon, False, False, 0)
            self.entry = Gtk.SearchEntry()
            self.entry.set_placeholder_text('Search apps and AmethystOS…')
            self.entry.connect('search-changed', lambda *_: self.populate())
            self.entry.connect('key-press-event', self.on_key)
            top.pack_start(self.entry, True, True, 0)
            root.pack_start(top, False, False, 0)
            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            root.pack_start(sep, False, False, 0)
            content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            root.pack_start(content, True, True, 0)
            sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            sidebar.set_name('amethyst-launcher-categories')
            sidebar.set_border_width(11)
            sidebar.set_size_request(142, -1)
            self.category_buttons = {}
            for label in CATEGORIES:
                button = Gtk.Button(label=label)
                button.set_relief(Gtk.ReliefStyle.NONE)
                button.connect('clicked', lambda _, cat=label: self.choose(cat))
                sidebar.pack_start(button, False, False, 0)
                self.category_buttons[label] = button
            content.pack_start(sidebar, False, False, 0)
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scroll.set_hexpand(True)
            scroll.set_vexpand(True)
            self.results = Gtk.ListBox()
            self.results.set_selection_mode(Gtk.SelectionMode.SINGLE)
            self.results.set_activate_on_single_click(False)
            self.results.connect('row-activated', self.activate)
            self.results.connect('key-press-event', self.on_key)
            self.results.set_name('amethyst-launcher-results')
            scroll.add(self.results)
            content.pack_start(scroll, True, True, 0)
            root.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)
            bottom = Gtk.Label(label='↑ ↓ Navigate    Enter Open    Ctrl+1–7 Categories    Esc Close')
            bottom.set_name('amethyst-launcher-hint')
            bottom.set_xalign(0)
            bottom.set_margin_start(18)
            bottom.set_margin_top(9)
            bottom.set_margin_bottom(11)
            root.pack_end(bottom, False, False, 0)
            self.populate()
            self.show_all()
            self.entry.grab_focus()

        def load_apps(self):
            by_name = {}
            for app in Gio.AppInfo.get_all():
                try:
                    if not app.should_show():
                        continue
                    name = app.get_display_name() or app.get_name()
                    if not name:
                        continue
                    # The Amethyst actions already appear under their proper category.
                    if name.startswith('Amethyst'):
                        continue
                    key = (name.casefold(), app.get_id())
                    by_name[key] = app
                except Exception:
                    continue
            self.apps = sorted(((app.get_display_name() or app.get_name(), app)
                                for app in by_name.values()), key=lambda x:x[0].casefold())

        def choose(self, category):
            self.category = category
            self.populate()
            self.entry.grab_focus()

        def populate(self):
            for row in self.results.get_children():
                self.results.remove(row)
            self.row_actions.clear()
            for cat, btn in self.category_buttons.items():
                cls = btn.get_style_context()
                (cls.add_class if cat == self.category else cls.remove_class)('selected-category')
            query = self.entry.get_text().casefold().strip()
            items = []
            # Put useful OS actions first in All, so hundreds of installed apps
            # cannot push Settings or Software past the 100-result limit.
            if self.category != 'Apps':
                for a in matches(self.category, query):
                    items.append((a.name, a.category+'  ·  '+a.subtitle,
                                  Gio.ThemedIcon.new(a.icon), a))
            if self.category in ('All','Apps'):
                for name, app in self.apps:
                    if not query or query in (name + ' ' + (app.get_description() or '')).casefold():
                        items.append((name, 'Application', app.get_icon(), app))
            for name, sub, icon, obj in items[:100]:
                row = Gtk.ListBoxRow()
                self.row_actions[row] = obj
                row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=13)
                row_box.set_border_width(9)
                if icon:
                    image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.DIALOG)
                    image.set_pixel_size(25)
                    row_box.pack_start(image, False, False, 0)
                vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                label = Gtk.Label(label=name)
                label.set_xalign(0)
                label.set_ellipsize(Pango.EllipsizeMode.END)
                vbox.pack_start(label, False, False, 0)
                detail = Gtk.Label(label=sub)
                detail.set_xalign(0)
                detail.get_style_context().add_class('dim-label')
                detail.set_ellipsize(Pango.EllipsizeMode.END)
                vbox.pack_start(detail, False, False, 0)
                row_box.pack_start(vbox, True, True, 0)
                row.add(row_box)
                self.results.add(row)
            self.results.show_all()
            if self.results.get_row_at_index(0):
                self.results.select_row(self.results.get_row_at_index(0))

        def activate(self, _, row):
            if row is None:
                return
            obj = self.row_actions.get(row)
            if obj is None: return
            try:
                if isinstance(obj, Action):
                    executable = obj.command[0]
                    if not Path(executable).is_file():
                        raise FileNotFoundError(executable)
                    subprocess.Popen(list(obj.command), start_new_session=True,
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    # GIO launches desktop files with their normal Exec, icons,
                    # environment and Flatpak portal handling.
                    obj.launch([], None)
            except Exception as exc:
                dialog = Gtk.MessageDialog(self, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR,
                                           Gtk.ButtonsType.CLOSE, f'Could not launch: {exc}')
                dialog.run()
                dialog.destroy()
                return
            self.close()

        def on_key(self, _widget, event):
            name = Gdk.keyval_name(event.keyval)
            if name == 'Escape':
                self.close()
                return True
            if event.state & Gdk.ModifierType.CONTROL_MASK and name in tuple('1234567'):
                self.choose(CATEGORIES[int(name)-1])
                return True
            if name in ('Down','Up'):
                selected = self.results.get_selected_row()
                idx = selected.get_index() if selected else -1
                idx += 1 if name == 'Down' else -1
                idx = max(0, min(idx, len(self.results.get_children())-1))
                next_row = self.results.get_row_at_index(idx)
                if next_row:
                    self.results.select_row(next_row)
                    next_row.grab_focus()
                return True
            if name in ('Return','KP_Enter'):
                self.activate(None, self.results.get_selected_row())
                return True
            # Return focus to search after navigating the result list.
            if len(name or '') == 1 and not (event.state & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK)):
                if self.get_focus() != self.entry:
                    self.entry.grab_focus()
                    self.entry.insert_text(name, -1)
                    return True
            return False

    Launcher()
    Gtk.main()
    return 0


if __name__ == '__main__':
    sys.exit(main())
