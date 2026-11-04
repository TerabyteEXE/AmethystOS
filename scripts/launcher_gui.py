#!/usr/bin/env python3
"""AmethystOS Home: a small, keyboard-first, category/drill-down menu.

Only known local helpers and desktop-file Gio app launchers are executable.
No generic shell execution or remote service is used. Navigation/model helpers
can be tested without installing GTK.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
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


def input_edit_intent(key: str, text: str, focused: bool, section: str) -> str:
    """Keep text editing ahead of category navigation.

    GTK Entry must process BackSpace/Delete itself while focused; a pressed
    BackSpace means "back one category" only with an *empty* search field.
    For the (rare) case where a result row has focus, editing is forwarded to
    the entry instead of being treated as a menu navigation shortcut.
    """
    if key == 'BackSpace':
        if text:
            return 'native' if focused else 'delete-left'
        return 'back' if section != 'Home' else 'ignore'
    if key == 'Delete':
        return 'native' if focused else ('delete-right' if text else 'ignore')
    return 'other'


def panel_size(section: str) -> tuple[int, int]:
    """Home stays narrow like the reference; installed apps get more room."""
    if section == 'Home':
        return 286, 425
    if section == 'Apps':
        return 402, 425
    n = len(SECTIONS.get(section, ()))
    return 346, max(150, min(340, 99 + 38 * n))


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
        """Compact, search-first GTK menu with conventional text editing."""

        def __init__(self):
            super().__init__(title='AmethystOS Home')
            self.set_name('amethyst-launcher')
            self.set_decorated(False)
            self.set_resizable(True)
            self.set_size_request(258, 130)
            self.set_default_size(*panel_size('Home'))
            self.set_position(Gtk.WindowPosition.CENTER)
            self.connect('destroy', Gtk.main_quit)
            # Important: do NOT bind the parent window to key-press-event.
            # GTK must get the first and only chance to edit a focused Entry.
            self.section = LEGACY_MAP[args.category]
            self.apps = self.load_apps()
            self.app_map = {name: app for name, app in self.apps}
            self.entries: list[MenuItem] = []
            self.provider = Gtk.CssProvider()
            self.load_style()

            frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            frame.set_name('amethyst-home-content')
            self.add(frame)

            self.navline = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
            self.navline.set_name('amethyst-home-nav')
            self.navline.set_margin_start(6)
            self.navline.set_margin_end(6)
            self.back_btn = Gtk.Button(label='‹')
            self.back_btn.set_name('amethyst-home-back')
            self.back_btn.set_relief(Gtk.ReliefStyle.NONE)
            self.back_btn.set_tooltip_text('Back to the main menu (Left or Backspace)')
            self.back_btn.connect('clicked', lambda *_: self.go_back())
            self.navline.pack_start(self.back_btn, False, False, 0)
            self.heading_label = Gtk.Label(label='Apps')
            self.heading_label.set_name('amethyst-home-title')
            self.heading_label.set_xalign(0)
            self.navline.pack_start(self.heading_label, True, True, 0)
            frame.pack_start(self.navline, False, False, 0)

            self.entry = Gtk.Entry()
            self.entry.set_name('amethyst-home-search')
            self.entry.set_placeholder_text('Go...')
            self.entry.set_tooltip_text('Type to search; Up/Down to select, Enter to open')
            self.entry.set_margin_start(8)
            self.entry.set_margin_end(8)
            self.entry.set_margin_top(6)
            self.entry.set_margin_bottom(5)
            self.entry.connect('changed', lambda *_: self.populate())
            self.entry.connect('key-press-event', self.on_key)
            frame.pack_start(self.entry, False, False, 0)

            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scroll.set_name('amethyst-home-scroll')
            scroll.set_hexpand(True)
            scroll.set_vexpand(True)
            self.results = Gtk.ListBox()
            self.results.set_name('amethyst-launcher-results')
            self.results.set_selection_mode(Gtk.SelectionMode.SINGLE)
            self.results.set_activate_on_single_click(False)
            self.results.connect('row-activated', self.activate)
            self.results.connect('key-press-event', self.on_key)
            scroll.add(self.results)
            frame.pack_start(scroll, True, True, 0)

            self._sync_section()
            self.populate()
            self.show_all()
            self.navline.set_visible(self.section != 'Home')
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

        def _sync_section(self):
            self.navline.set_visible(self.section != 'Home')
            self.heading_label.set_text(self.section)
            self.entry.set_placeholder_text('Go...' if self.section == 'Home' else 'Search...')
            self.resize(*panel_size(self.section))

        def navigate(self, section):
            if section not in SECTIONS and section != 'Apps':
                return
            self.section = section
            self.entry.set_text('')
            self._sync_section()
            self.populate()
            self.entry.grab_focus()

        def go_back(self):
            if self.section != 'Home':
                self.section = 'Home'
                self.entry.set_text('')
                self._sync_section()
                self.populate()
                self.entry.grab_focus()

        def populate(self):
            for row in self.results.get_children():
                self.results.remove(row)
            self.entries = search_menu(self.entry.get_text(), self.section, self.apps)[:120]
            for item in self.entries:
                row = Gtk.ListBoxRow()
                line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=9)
                line.set_name('amethyst-home-item')
                glyph = Gtk.Image.new_from_icon_name(item.icon, Gtk.IconSize.MENU)
                glyph.set_pixel_size(15)
                line.pack_start(glyph, False, False, 0)
                title = Gtk.Label(label=item.title)
                title.set_name('amethyst-home-row-title')
                title.set_xalign(0)
                title.set_ellipsize(Pango.EllipsizeMode.END)
                line.pack_start(title, True, True, 0)
                if item.section:
                    chevron = Gtk.Label(label='›')
                    chevron.set_name('amethyst-home-chevron')
                    line.pack_end(chevron, False, False, 0)
                row.add(line)
                self.results.add(row)
            self.results.show_all()
            first = self.results.get_row_at_index(0)
            if first is not None:
                self.results.select_row(first)
            # Selecting a ListBox row must never steal focus from the search.

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

        def _edit_from_results(self, name):
            """Edit the search if a click placed keyboard focus on the list."""
            bounds = self.entry.get_selection_bounds()
            if bounds and len(bounds) == 3:
                selected, start, end = bool(bounds[0]), bounds[1], bounds[2]
            elif bounds and len(bounds) == 2:
                start, end = bounds
                selected = (start != end)
            else:
                selected, start, end = False, 0, 0
            if selected:
                self.entry.delete_text(start, end)
                self.entry.set_position(start)
            else:
                pos = self.entry.get_position()
                if name == 'BackSpace' and pos > 0:
                    self.entry.delete_text(pos-1, pos)
                    self.entry.set_position(pos-1)
                elif name == 'Delete' and pos < len(self.entry.get_text()):
                    self.entry.delete_text(pos, pos+1)
                    self.entry.set_position(pos)
            self.entry.grab_focus()

        def on_key(self, widget, event):
            name = Gdk.keyval_name(event.keyval) or ''
            if name == 'Escape':
                self.close()
                return True
            # Let GTK Entry handle all native text-editing keys, including
            # BackSpace, Delete, Ctrl+Backspace, Ctrl+A and cursor movement.
            # The old parent-window handler interpreted BackSpace as "Back".
            focused = widget is self.entry
            if name in ('BackSpace', 'Delete'):
                intent = input_edit_intent(name, self.entry.get_text(), focused, self.section)
                if intent == 'native':
                    return False
                if intent == 'back':
                    self.go_back()
                elif intent in ('delete-left', 'delete-right'):
                    self._edit_from_results(name)
                return True
            if event.state & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK):
                return False
            if name == 'Left':
                if focused and self.entry.get_text():
                    return False  # text cursor movement, not category navigation
                self.go_back()
                return True
            if name in ('Return', 'KP_Enter', 'Right'):
                if name == 'Right' and focused and self.entry.get_text():
                    return False
                self.activate(None, self.results.get_selected_row())
                return True
            if name in ('Down', 'Up'):
                selected = self.results.get_selected_row()
                count = len(self.entries)
                if count:
                    index = selected.get_index() if selected is not None else (-1 if name=='Down' else 0)
                    index = (index + (1 if name == 'Down' else -1)) % count
                    row = self.results.get_row_at_index(index)
                    if row is not None:
                        self.results.select_row(row)
                        self.entry.grab_focus()
                return True
            if widget is self.results and event.string and event.string.isprintable():
                self.entry.grab_focus()
                self.entry.insert_text(event.string, -1)
                return True
            return False

    Home()
    Gtk.main()
    return 0


if __name__ == '__main__':
    sys.exit(main())
