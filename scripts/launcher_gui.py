#!/usr/bin/env python3
"""AmethystOS Home: a small, keyboard-first, category/drill-down menu.

Only known local helpers and desktop-file Gio app launchers are executable.
No generic shell execution or remote service is used. Navigation/model helpers
can be tested without installing GTK.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from datetime import datetime
import getpass
from pathlib import Path
import subprocess
import sys

BIN = str(Path.home() / '.local/bin')
CATEGORIES = ('All', 'Apps', 'Settings', 'Software', 'Wallpapers', 'System', 'Power')  # legacy CLI/API


@dataclass(frozen=True)
class Action:
    category: str
    name: str
    subtitle: str
    command: tuple[str, ...]
    icon: str = 'applications-system'


ACTIONS = (
    Action('Settings', 'Amethyst Settings', 'All desktop preferences', (f'{BIN}/amethyst-settings',), 'preferences-system'),
    Action('Settings', 'Appearance & themes', 'Color, text size and accessibility', (f'{BIN}/amethyst-settings', 'appearance'), 'preferences-desktop-theme'),
    Action('Settings', 'Top bar', 'Position, density and widgets', (f'{BIN}/amethyst-settings', 'bar'), 'preferences-desktop'),
    Action('Settings', 'Display and workspaces', 'Monitors and Niri controls', (f'{BIN}/amethyst-settings', 'desktop'), 'video-display'),
    Action('Settings', 'Devices and connections', 'Audio, network and Bluetooth', (f'{BIN}/amethyst-settings', 'devices'), 'preferences-system'),
    Action('Software', 'Software', 'Install, remove and update', (f'{BIN}/amethyst-settings', 'software'), 'system-software-install'),
    Action('Software', 'Install an application', 'Curated Fedora and Flatpak software', (f'{BIN}/amethyst-software', 'install'), 'list-add'),
    Action('Software', 'Remove an application', 'Review changes before removal', (f'{BIN}/amethyst-software', 'remove'), 'edit-delete'),
    Action('Software', 'System updates', 'Fedora and Flatpak updates', (f'{BIN}/amethyst-software', 'update'), 'software-update-available'),
    Action('Wallpapers', 'Wallpaper gallery', 'Choose from installed wallpapers', (f'{BIN}/amethyst-wallpapers',), 'preferences-desktop-wallpaper'),
    Action('System', 'Calendar', 'Today and monthly calendar', (f'{BIN}/amethyst-calendar',), 'x-office-calendar'),
    Action('System', 'System diagnostics', 'Check desktop components', (f'{BIN}/amethyst-settings', 'system'), 'utilities-system-monitor'),
    Action('Power', 'Power menu', 'Lock, sign out, reboot or shut down', (f'{BIN}/powermenu',), 'system-shutdown'),
)


def matches(category: str, query: str, actions=ACTIONS):
    q = query.casefold().strip()
    return [a for a in actions if (category == 'All' or a.category == category)
            and (not q or q in f'{a.name} {a.subtitle} {a.category}'.casefold())]


@dataclass(frozen=True)
class MenuItem:
    title: str
    description: str
    icon: str
    section: str = ''          # nonempty -> drill into a section
    action: Action | None = None
    url: str = ''              # fixed, project-owned links


HOME_SECTIONS = (
    MenuItem('Apps', 'Installed desktop applications', 'view-grid-symbolic', section='Apps'),
    MenuItem('Learn', 'Documentation and keyboard help', 'help-browser-symbolic', section='Learn'),
    MenuItem('Style', 'Themes, wallpapers and the bar', 'preferences-desktop-theme', section='Style'),
    MenuItem('Setup', 'Desktop settings and hardware', 'preferences-system-symbolic', section='Setup'),
    MenuItem('Install', 'Add applications', 'list-add-symbolic', section='Install'),
    MenuItem('Remove', 'Uninstall software safely', 'edit-delete-symbolic', section='Remove'),
    MenuItem('Update', 'Keep the system current', 'software-update-available-symbolic', section='Update'),
    MenuItem('About', 'AmethystOS and upstream credits', 'help-about-symbolic', section='About'),
    MenuItem('System', 'Calendar, diagnostics and tools', 'utilities-system-monitor-symbolic', section='System'),
    MenuItem('Power', 'Lock, sign out and shutdown', 'system-shutdown-symbolic', section='Power'),
)

# Navigate only to allowlisted executable actions; don't pass typed text to a shell.
BY_NAME = {a.name: a for a in ACTIONS}
WEBSITE = 'https://terabyteexe.github.io/AmethystOS/'
SECTIONS = {
    'Learn': (
        MenuItem('Keyboard shortcuts', 'Full searchable shortcut reference', 'input-keyboard', url=WEBSITE+'wiki/keybinds.html'),
        MenuItem('Getting started', 'First steps and installation', 'help-browser', url=WEBSITE+'install.html'),
        MenuItem('Troubleshooting', 'Common problems and fixes', 'dialog-information', url=WEBSITE+'wiki/troubleshooting.html'),
    ),
    'Style': (
        MenuItem('Appearance & themes', 'Light/Dark and scaling', 'preferences-desktop-theme', action=BY_NAME['Appearance & themes']),
        MenuItem('Wallpaper gallery', 'Pick a wallpaper visually', 'preferences-desktop-wallpaper', action=BY_NAME['Wallpaper gallery']),
        MenuItem('Top bar', 'Widgets and layout', 'preferences-desktop', action=BY_NAME['Top bar']),
    ),
    'Setup': (
        MenuItem('Amethyst Settings', 'Open all settings', 'preferences-system', action=BY_NAME['Amethyst Settings']),
        MenuItem('Display and workspaces', 'Monitors and tiling', 'video-display', action=BY_NAME['Display and workspaces']),
        MenuItem('Devices and connections', 'Audio, Wi-Fi and Bluetooth', 'network-wireless', action=BY_NAME['Devices and connections']),
        MenuItem('Top bar', 'Widgets and layout', 'preferences-desktop', action=BY_NAME['Top bar']),
    ),
    'Install': (
        MenuItem('Install an application', 'Curated Fedora / Flatpak choices', 'list-add', action=BY_NAME['Install an application']),
        MenuItem('Software settings', 'Software and update controls', 'system-software-install', action=BY_NAME['Software']),
    ),
    'Remove': (
        MenuItem('Remove an application', 'Review and confirm changes', 'edit-delete', action=BY_NAME['Remove an application']),
        MenuItem('Software settings', 'Manage installed software', 'system-software-install', action=BY_NAME['Software']),
    ),
    'Update': (
        MenuItem('System updates', 'Fedora and Flatpak', 'software-update-available', action=BY_NAME['System updates']),
    ),
    'About': (
        MenuItem('About AmethystOS', 'Version and system information', 'help-about', action=BY_NAME['System diagnostics']),
        MenuItem('Project website', 'Documentation and download', 'web-browser', url=WEBSITE),
        MenuItem('Source and credits', 'GitHub project', 'text-x-generic', url='https://github.com/TerabyteEXE/AmethystOS'),
    ),
    'System': (
        MenuItem('Calendar', 'Today and the current month', 'x-office-calendar', action=BY_NAME['Calendar']),
        MenuItem('System diagnostics', 'Troubleshooting and system information', 'utilities-system-monitor', action=BY_NAME['System diagnostics']),
        MenuItem('Amethyst Settings', 'All system preferences', 'preferences-system', action=BY_NAME['Amethyst Settings']),
    ),
    'Power': (
        MenuItem('Power menu', 'Lock, log out, reboot or shut down', 'system-shutdown', action=BY_NAME['Power menu']),
    ),
}
LEGACY_MAP = {'All':'Home','Apps':'Apps','Settings':'Setup','Software':'Install',
              'Wallpapers':'Style','System':'System','Power':'Power'}


def search_menu(query: str, section: str = 'Home', applications=()):
    """Search items in Home globally, or just the current drill-down category."""
    q = query.strip().casefold()
    if section == 'Home' and not q:
        return list(HOME_SECTIONS)
    if section == 'Home':
        grouped = [(group, item) for group, items in SECTIONS.items() for item in items]
        found = [item for item in HOME_SECTIONS if q in f'{item.title} {item.description}'.casefold()]
        keys = {(item.title, item.url) for item in found}
        for group, item in grouped:
            key = (item.title, item.url)
            if key not in keys and q in f'{item.title} {item.description} {group}'.casefold():
                found.append(item)
                keys.add(key)
        return found + [MenuItem(name, 'Application', 'application-x-executable')
                        for name, _ in applications if q in name.casefold()]
    if section == 'Apps':
        return [MenuItem(name, 'Application', 'application-x-executable')
                for name, _ in applications if not q or q in name.casefold()]
    return [item for item in SECTIONS.get(section, ()) if not q or
            q in f'{item.title} {item.description} {section}'.casefold()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', choices=CATEGORIES, default='All', help='Open an existing menu section')
    parser.add_argument('--list-actions', action='store_true', help='Headless action inventory')
    parser.add_argument('--list-menu', action='store_true', help='Headless Home menu inventory')
    args = parser.parse_args()
    if args.list_actions:
        for a in ACTIONS:
            print(f'{a.category}\t{a.name}\t{a.subtitle}\t{" ".join(a.command)}')
        return 0
    if args.list_menu:
        for item in HOME_SECTIONS:
            print(f'{item.title}\t{item.description}')
        return 0
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, Gdk, Gio, GLib, Pango, GdkPixbuf
    except (ImportError, ValueError) as exc:
        print(f'Amethyst Home requires GTK3/PyGObject: {exc}', file=sys.stderr)
        return 2

    GLib.set_prgname('amethyst-launcher')
    GLib.set_application_name('AmethystOS Home')

    class Home(Gtk.Window):
        def __init__(self):
            super().__init__(title='AmethystOS Home')
            self.set_name('amethyst-launcher')
            self.set_decorated(False)
            self.set_default_size(460, 535)
            self.set_size_request(405, 400)
            self.set_position(Gtk.WindowPosition.CENTER)
            self.connect('destroy', Gtk.main_quit)
            self.connect('key-press-event', self.on_key)
            self.section = LEGACY_MAP[args.category]
            self.apps = self.load_apps()
            self.app_map = {name: app for name, app in self.apps}
            self.entries = []
            self.provider = Gtk.CssProvider()
            self.load_style()

            frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            frame.set_name('amethyst-home-content')
            self.add(frame)
            header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            header.set_name('amethyst-home-header')
            header.set_border_width(14)
            logo = Path.home()/'.local/share/amethystos/assets/amethyst-logo.png'
            if logo.is_file():
                try:
                    pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(logo), 26, 26, True)
                    header.pack_start(Gtk.Image.new_from_pixbuf(pb), False, False, 0)
                except (GLib.Error, OSError):
                    pass
            brand = Gtk.Label(label='AMETHYSTOS')
            brand.set_name('amethyst-home-brand')
            brand.set_xalign(0)
            header.pack_start(brand, True, True, 0)
            self.clock = Gtk.Label(label=datetime.now().strftime('%a %b %-d'))
            self.clock.set_name('amethyst-home-time')
            header.pack_end(self.clock, False, False, 0)
            frame.pack_start(header, False, False, 0)

            heading = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            heading.set_margin_start(16)
            heading.set_margin_end(16)
            heading.set_margin_top(2)
            heading.set_margin_bottom(9)
            self.back_btn = Gtk.Button(label='‹')
            self.back_btn.set_name('amethyst-home-back')
            self.back_btn.set_relief(Gtk.ReliefStyle.NONE)
            self.back_btn.connect('clicked', lambda *_: self.go_back())
            heading.pack_start(self.back_btn, False, False, 0)
            self.heading_label = Gtk.Label(label='Home')
            self.heading_label.set_name('amethyst-home-title')
            self.heading_label.set_xalign(0)
            heading.pack_start(self.heading_label, True, True, 0)
            self.welcome = Gtk.Label(label=f'Hi, {getpass.getuser()}')
            self.welcome.set_name('amethyst-home-welcome')
            heading.pack_end(self.welcome, False, False, 0)
            frame.pack_start(heading, False, False, 0)

            self.entry = Gtk.SearchEntry()
            self.entry.set_name('amethyst-home-search')
            self.entry.set_placeholder_text('Search apps, settings, actions…')
            self.entry.set_margin_start(14)
            self.entry.set_margin_end(14)
            self.entry.set_margin_bottom(11)
            self.entry.connect('search-changed', lambda *_: self.populate())
            self.entry.connect('key-press-event', self.on_key)
            frame.pack_start(self.entry, False, False, 0)

            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scroll.set_hexpand(True)
            scroll.set_vexpand(True)
            scroll.set_name('amethyst-home-scroll')
            self.results = Gtk.ListBox()
            self.results.set_name('amethyst-launcher-results')
            self.results.set_selection_mode(Gtk.SelectionMode.SINGLE)
            self.results.set_activate_on_single_click(False)
            self.results.connect('row-activated', self.activate)
            self.results.connect('key-press-event', self.on_key)
            scroll.add(self.results)
            frame.pack_start(scroll, True, True, 0)
            hint = Gtk.Label(label='↑ ↓ Select      Enter Open      ← Back      Esc Close')
            hint.set_name('amethyst-launcher-hint')
            hint.set_xalign(0)
            hint.set_margin_start(17)
            hint.set_margin_top(11)
            hint.set_margin_bottom(12)
            frame.pack_end(hint, False, False, 0)
            self.populate()
            self.show_all()
            self.entry.grab_focus()

        def load_style(self):
            theme = 'dark'
            try:
                import json
                data = json.loads((Path.home()/'.local/state/amethystos-base-v1/appearance.json').read_text())
                if data.get('theme') == 'light':
                    theme = 'light'
            except (OSError, ValueError, TypeError):
                pass
            css = Path.home()/'.local/share/amethystos/launcher'/f'{theme}.css'
            if css.is_file():
                try:
                    self.provider.load_from_path(str(css))
                    Gtk.StyleContext.add_provider_for_screen(self.get_screen(), self.provider,
                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                except GLib.Error as exc:
                    print('Amethyst Home CSS:',exc,file=sys.stderr)

        @staticmethod
        def load_apps():
            found = {}
            for app in Gio.AppInfo.get_all():
                try:
                    if not app.should_show():
                        continue
                    name = app.get_display_name() or app.get_name()
                    if name and not name.lower().startswith('amethyst'):
                        found.setdefault(name, app)
                except Exception:
                    continue
            return sorted(found.items(), key=lambda item: item[0].casefold())

        def navigate(self, section):
            if section not in SECTIONS and section != 'Apps':
                return
            self.section = section
            self.entry.set_text('')
            self.heading_label.set_text(section)
            self.populate()
            self.entry.grab_focus()

        def go_back(self):
            if self.section != 'Home':
                self.section = 'Home'
                self.entry.set_text('')
                self.heading_label.set_text('Home')
                self.populate()
                self.entry.grab_focus()

        def populate(self):
            for row in self.results.get_children():
                self.results.remove(row)
            self.entries = search_menu(self.entry.get_text(), self.section, self.apps)
            for item in self.entries[:120]:
                row = Gtk.ListBoxRow()
                line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=11)
                line.set_border_width(9)
                glyph = Gtk.Image.new_from_icon_name(item.icon, Gtk.IconSize.MENU)
                glyph.set_pixel_size(18)
                line.pack_start(glyph, False, False, 0)
                labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                title = Gtk.Label(label=item.title)
                title.set_xalign(0)
                title.set_ellipsize(Pango.EllipsizeMode.END)
                labels.pack_start(title, False, False, 0)
                sub = Gtk.Label(label=item.description)
                sub.set_name('amethyst-home-detail')
                sub.set_xalign(0)
                sub.set_ellipsize(Pango.EllipsizeMode.END)
                labels.pack_start(sub, False, False, 0)
                line.pack_start(labels, True, True, 0)
                if item.section:
                    chevron = Gtk.Label(label='›')
                    chevron.set_name('amethyst-home-chevron')
                    line.pack_end(chevron, False, False, 0)
                row.add(line)
                self.results.add(row)
            self.results.show_all()
            self.back_btn.set_sensitive(self.section!='Home')
            first = self.results.get_row_at_index(0)
            if first is not None:
                self.results.select_row(first)

        def launch_action(self, action):
            command = action.command
            if not Path(command[0]).is_file():
                raise FileNotFoundError(f'{command[0]} is missing. Try reinstalling the AmethystOS helpers.')
            subprocess.Popen(list(command), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)

        def activate(self, _list, row):
            if row is None:
                return
            index = row.get_index()
            if not 0 <= index < len(self.entries):
                return
            item = self.entries[index]
            try:
                if item.section:
                    self.navigate(item.section)
                    return
                if item.action:
                    self.launch_action(item.action)
                elif item.url:
                    Gio.AppInfo.launch_default_for_uri(item.url, None)
                elif self.section == 'Apps' or item.description == 'Application':
                    app = self.app_map.get(item.title)
                    if app is None:
                        raise RuntimeError('Application is no longer installed')
                    if not app.launch([], None):
                        raise RuntimeError('Desktop launcher returned an error')
                else:
                    return
            except Exception as exc:
                dialog = Gtk.MessageDialog(self, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR,
                                           Gtk.ButtonsType.CLOSE, f'Cannot open {item.title}: {exc}')
                dialog.run()
                dialog.destroy()
                return
            self.close()

        def on_key(self, widget, event):
            name = Gdk.keyval_name(event.keyval) or ''
            if name == 'Escape':
                self.close()
                return True
            if name in ('Left','BackSpace') and (widget != self.entry or not self.entry.get_text()):
                self.go_back()
                return True
            if name in ('Return','KP_Enter','Right'):
                if name == 'Right' and widget == self.entry and self.entry.get_text():
                    return False   # allow search cursor movement
                self.activate(None, self.results.get_selected_row())
                return True
            if name in ('Down','Up'):
                selected = self.results.get_selected_row()
                index = selected.get_index() if selected else (-1 if name=='Down' else 1)
                index += 1 if name=='Down' else -1
                index = max(0,min(index,len(self.results.get_children())-1))
                row = self.results.get_row_at_index(index)
                if row:
                    self.results.select_row(row)
                    # Keep focus in search for typing after arrow navigation.
                    self.entry.grab_focus()
                return True
            if widget == self.results and len(name)==1 and not (event.state & (Gdk.ModifierType.CONTROL_MASK|Gdk.ModifierType.MOD1_MASK)):
                self.entry.grab_focus()
                self.entry.insert_text(name, -1)
                return True
            return False

    Home()
    Gtk.main()
    return 0


if __name__ == '__main__':
    sys.exit(main())
