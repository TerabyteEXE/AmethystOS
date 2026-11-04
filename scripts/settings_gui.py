#!/usr/bin/env python3
"""AmethystOS Settings — persistent, category-based GTK3 controls.

The GUI is a frontend for the existing reversible, validated managers. It does
not patch config files itself and never runs privileged commands without the
user interacting with the existing terminal-based software tools.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from threading import Thread

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf
from settings_backend import PAGES, MODULES, DENSITIES, POSITIONS, SCALES, page_for, bar_action, appearance_action

HOME = Path.home()
BIN = HOME / '.local/bin'
SHARE = HOME / '.local/share/amethystos'
STATE = HOME / '.local/state/amethystos-base-v1'


class Settings(Gtk.Window):
    def __init__(self, requested='home'):
        super().__init__(title='AmethystOS Settings')
        self.set_name("amethyst-settings")
        self.set_default_size(870, 610)
        self.set_size_request(650, 470)
        self.set_border_width(0)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('destroy', Gtk.main_quit)
        self.pending = False
        self.controls = []
        self.bar_widgets = {}
        self.syncing = False
        self.bar_prefs = self._read_json(STATE/'bar.json', {'position':'top','density':'normal','modules':{}})
        self.appearance_prefs = self._read_json(STATE/'appearance.json', {'theme':'dark','scale':100})

        header = Gtk.HeaderBar()
        header.set_title('AmethystOS Settings')
        header.set_subtitle('Appearance  •  Devices  •  Software')
        header.set_show_close_button(True)
        self.set_titlebar(header)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(outer)
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        outer.pack_start(content, True, True, 0)
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(160)
        side_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        side_panel.set_name('amethyst-sidebar')
        side_panel.set_size_request(204, -1)
        brand = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        brand.set_border_width(17)
        logo = SHARE / 'assets/amethyst-logo.png'
        if logo.is_file():
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(logo), 36, 36, True)
                brand.pack_start(Gtk.Image.new_from_pixbuf(pixbuf), False, False, 0)
            except (GLib.Error, OSError):
                pass
        brand_labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        brand_name = Gtk.Label(label='AmethystOS')
        brand_name.set_name('amethyst-brand')
        brand_name.set_xalign(0)
        brand_labels.pack_start(brand_name, False, False, 0)
        subtitle = Gtk.Label(label='DESKTOP SETTINGS')
        subtitle.set_name('amethyst-tagline')
        subtitle.set_xalign(0)
        brand_labels.pack_start(subtitle, False, False, 0)
        brand.pack_start(brand_labels, True, True, 0)
        side_panel.pack_start(brand, False, False, 0)
        sidebar = Gtk.StackSidebar()
        sidebar.set_stack(self.stack)
        side_panel.pack_start(sidebar, True, True, 0)
        content.pack_start(side_panel, False, False, 0)
        content.pack_start(self.stack, True, True, 0)
        labels = {
            'home':'Overview', 'appearance':'Appearance', 'bar':'Top bar',
            'devices':'Devices', 'desktop':'Desktop', 'software':'Software',
            'system':'System',
        }
        for name in PAGES:
            viewport = Gtk.ScrolledWindow()
            viewport.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
            body.set_border_width(23)
            viewport.add(body)
            self.stack.add_titled(viewport, name, labels[name])
            getattr(self, f'build_{name}')(body)
        self.stack.set_visible_child_name(page_for(requested))
        status_border = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        outer.pack_start(status_border, False, False, 0)
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer.set_border_width(10)
        self.status = Gtk.Label(label='Ready. Changes apply without closing Settings.')
        self.status.set_xalign(0)
        self.status.set_line_wrap(True)
        footer.pack_start(self.status, True, True, 0)
        self.busy_spinner = Gtk.Spinner()
        footer.pack_end(self.busy_spinner, False, False, 0)
        outer.pack_end(footer, False, False, 0)
        self.theme_in_use = None
        self._style_provider = None
        self._apply_style(self.appearance_prefs.get('theme', 'dark'))

    def _apply_style(self, theme):
        """Load scoped CSS for Settings, tracking the active desktop theme."""
        theme = theme if theme in ('light', 'dark') else 'dark'
        css_file = SHARE / 'settings' / f'{theme}.css'
        if not css_file.is_file():
            return
        screen = self.get_screen()
        if screen is None:
            return
        try:
            provider = Gtk.CssProvider()
            provider.load_from_path(str(css_file))
            if self._style_provider is not None:
                Gtk.StyleContext.remove_provider_for_screen(screen, self._style_provider)
            Gtk.StyleContext.add_provider_for_screen(
                screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self._style_provider = provider
            self.theme_in_use = theme
        except GLib.Error as exc:
            print('AmethystOS Settings: CSS could not be loaded:', exc, file=sys.stderr)

    @staticmethod
    def _read_json(path, default):
        try:
            return json.loads(path.read_text())
        except (OSError, ValueError, TypeError):
            return default

    def heading(self, box, title, description):
        heading = Gtk.Label()
        heading.set_markup('<span weight="bold" size="x-large">'+GLib.markup_escape_text(title)+'</span>')
        heading.set_xalign(0)
        box.pack_start(heading, False, False, 0)
        text = Gtk.Label(label=description)
        text.set_xalign(0)
        text.set_line_wrap(True)
        text.get_style_context().add_class('dim-label')
        box.pack_start(text, False, False, 0)

    def section(self, box, title):
        label = Gtk.Label()
        label.set_markup('<span weight="bold">'+GLib.markup_escape_text(title)+'</span>')
        label.set_xalign(0)
        label.set_margin_top(7)
        box.pack_start(label, False, False, 0)

    def button(self, box, title, description, callback):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        label = Gtk.Label(label=title)
        label.set_xalign(0)
        subtitle = Gtk.Label(label=description)
        subtitle.set_line_wrap(True)
        subtitle.set_xalign(0)
        subtitle.get_style_context().add_class('dim-label')
        text.pack_start(label, False, False, 0)
        text.pack_start(subtitle, False, False, 0)
        row.pack_start(text, True, True, 0)
        btn = Gtk.Button(label='Open')
        btn.connect('clicked', lambda _: callback())
        row.pack_end(btn, False, False, 0)
        box.pack_start(row, False, False, 0)
        return btn

    def dropdown(self, box, title, choices, selected, callback):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        label = Gtk.Label(label=title)
        label.set_xalign(0)
        row.pack_start(label, True, True, 0)
        combo = Gtk.ComboBoxText()
        for choice in choices:
            combo.append_text(str(choice).capitalize())
        value = str(selected).capitalize()
        combo.set_active(choices.index(str(selected)) if str(selected) in choices else 0)
        combo.connect('changed', lambda w: callback(choices[w.get_active()]) if w.get_active() >= 0 and not self.syncing else None)
        row.pack_end(combo, False, False, 0)
        box.pack_start(row, False, False, 0)
        self.controls.append(combo)
        return combo

    def _result(self, message, ok=True):
        self.status.set_text(message)
        self.status.get_style_context().remove_class('error')
        if not ok:
            self.status.get_style_context().add_class('error')

    def _done(self, result, ok):
        self.pending = False
        self.busy_spinner.stop()
        for widget in self.controls:
            widget.set_sensitive(True)
        self._result(('Applied: ' if ok else 'Could not apply: ') + result, ok)
        self.bar_prefs = self._read_json(STATE/'bar.json', self.bar_prefs)
        self.appearance_prefs = self._read_json(STATE/'appearance.json', self.appearance_prefs)
        if self.appearance_prefs.get('theme','dark') != self.theme_in_use:
            self._apply_style(self.appearance_prefs.get('theme','dark'))
        self.sync_bar_widgets()
        return False

    def sync_bar_widgets(self):
        # If applying a preference fails, restore the toggles to the actual saved
        # state instead of leaving them visually out of sync with Waybar.
        self.syncing = True
        try:
            position = self.bar_prefs.get('position','top')
            density = self.bar_prefs.get('density','normal')
            if 'position' in self.bar_widgets:
                self.bar_widgets['position'].set_active(POSITIONS.index(position))
            if 'density' in self.bar_widgets:
                self.bar_widgets['density'].set_active(DENSITIES.index(density))
            modules = self.bar_prefs.get('modules',{})
            for name in MODULES:
                if name in self.bar_widgets:
                    self.bar_widgets[name].set_active(bool(modules.get(name,True)))
        finally:
            self.syncing = False

    def run_setting(self, argv, message):
        if self.pending:
            return
        self.pending = True
        self._result('Applying '+message+'…')
        self.busy_spinner.start()
        for widget in self.controls:
            widget.set_sensitive(False)

        def work():
            try:
                completed = subprocess.run([str(v) for v in argv], capture_output=True, text=True, timeout=45)
                result = (completed.stdout if completed.returncode == 0 else completed.stderr).strip()
                detail = (result.splitlines()[-1] if result else message) if completed.returncode else message
                GLib.idle_add(self._done, detail, completed.returncode == 0)
            except (OSError, subprocess.TimeoutExpired) as exc:
                GLib.idle_add(self._done, str(exc), False)
        Thread(target=work, daemon=True).start()

    def open_program(self, argv, label):
        exe = str(argv[0])
        if '/' in exe:
            available = Path(exe).is_file()
        else:
            available = bool(shutil.which(exe))
        if not available:
            self._result(label+' is not installed. See Software or install the package.', False)
            return
        try:
            subprocess.Popen([str(a) for a in argv], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
            self._result('Opened '+label+'. Settings remains open.')
        except OSError as exc:
            self._result(f'Could not open {label}: {exc}', False)

    def run_bin(self, name, *args):
        self.open_program([BIN/name, *args], name.replace('amethyst-','').replace('-',' '))

    def to_page(self, name):
        self.stack.set_visible_child_name(name)

    def build_home(self, box):
        self.heading(box, 'Desktop settings', 'Control your AmethystOS desktop without leaving Settings.')
        self.section(box, 'Most used')
        self.button(box, 'Appearance', 'Dark / Light, wallpaper, and text scaling', lambda: self.to_page('appearance'))
        self.button(box, 'Top bar', 'Position, density, and visible status indicators', lambda: self.to_page('bar'))
        self.button(box, 'Devices', 'Network, volume, and Bluetooth', lambda: self.to_page('devices'))
        self.button(box, 'Software', 'Install, remove, and update applications', lambda: self.to_page('software'))
        self.section(box, 'Quick access')
        self.button(box, 'Wallpaper gallery', 'Browse and apply your Amethyst wallpapers', lambda: self.run_bin('amethyst-wallpapers'))
        self.button(box, 'Calendar', 'Open the monthly calendar', lambda: self.run_bin('amethyst-calendar'))

    def build_appearance(self, box):
        self.heading(box, 'Appearance', 'Apply the Amethyst theme or adjust reading size while this window stays open.')
        self.section(box, 'Color theme')
        theme = self.appearance_prefs.get('theme','dark')
        self.dropdown(box, 'Theme', ('dark','light'), theme, lambda v: self.run_setting([BIN/'amethyst-theme',appearance_action('theme',v)[1]],'theme'))
        self.section(box, 'Interface scale')
        scale = str(self.appearance_prefs.get('scale',100))
        values = tuple(str(x) for x in SCALES)
        self.dropdown(box, 'Text and UI', values, scale, lambda v: self.run_setting([BIN/'amethyst-scale',appearance_action('scale',v)[1]],'scale'))
        self.section(box, 'Wallpaper and app appearance')
        self.button(box,'Wallpaper gallery','Choose from your images and official Light/Dark wallpapers',lambda: self.run_bin('amethyst-wallpapers'))
        self.button(box,'GTK application theme','Customize GTK widgets using nwg-look',lambda: self.open_program(['nwg-look'],'GTK appearance'))
        self.button(box,'Qt application theme','Customize Qt6 widgets using qt6ct',lambda: self.open_program(['qt6ct'],'Qt appearance'))
        self.section(box, 'Note')
        self.note(box,'Wayland monitor DPI is managed by Niri. Some open apps may need a restart to reflect changed text sizes.')

    def build_bar(self, box):
        self.heading(box, 'Top bar', 'Customize Waybar without dismissing the settings window. Each change is saved immediately.')
        self.section(box, 'Layout')
        self.bar_widgets['position'] = self.dropdown(box,'Position',POSITIONS,self.bar_prefs.get('position','top'),lambda v:self.bar_change('position',v))
        self.bar_widgets['density'] = self.dropdown(box,'Density',DENSITIES,self.bar_prefs.get('density','normal'),lambda v:self.bar_change('density',v))
        self.section(box, 'Visible indicators')
        labels={'cpu':'CPU usage','memory':'Memory usage','battery':'Battery','player':'Media player','bluetooth':'Bluetooth','clipboard':'Clipboard','tray':'App tray'}
        active=self.bar_prefs.get('modules',{})
        for name in MODULES:
            row=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=12)
            label=Gtk.Label(label=labels[name]);label.set_xalign(0)
            row.pack_start(label,True,True,0)
            toggle=Gtk.Switch();toggle.set_active(bool(active.get(name,True)))
            toggle.connect('notify::active',lambda widget,_prop,key=name: self.bar_change('toggle',key) if not self.syncing else None)
            row.pack_end(toggle,False,False,0)
            box.pack_start(row,False,False,0)
            self.controls.append(toggle)
            self.bar_widgets[name] = toggle
        self.note(box, 'Waybar briefly reloads when you apply a change; this Settings window remains open. Your preferences survive Light/Dark changes.')

    def bar_change(self, action, value):
        bar_action(action,value)
        self.run_setting([BIN/'amethyst-bar',action,value],f'bar {action}')

    def note(self, box, value):
        line=Gtk.Label(label=value)
        line.set_xalign(0);line.set_line_wrap(True)
        line.get_style_context().add_class('dim-label')
        box.pack_start(line,False,False,0)

    def build_devices(self, box):
        self.heading(box,'Devices','System tools for the hardware connected to this computer.')
        self.button(box,'Network','Wi-Fi, Ethernet, and saved connections',lambda:self.open_program(['nm-connection-editor'],'Network connections'))
        self.button(box,'Sound','Playback and recording devices',lambda:self.open_program(['pavucontrol'],'Audio controls'))
        self.button(box,'Bluetooth','Discover and manage Bluetooth devices',lambda:self.open_program(['blueman-manager'],'Bluetooth manager'))
        self.note(box,'If a tool is missing, install it through Fedora. GNOME Display Settings is not generally compatible with Niri sessions.')

    def build_desktop(self, box):
        self.heading(box,'Desktop','Five persistent workspaces and keyboard-first window management.')
        self.section(box,'Workspaces')
        row=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=8)
        for index,workspace in enumerate(('one','two','three','four','five'),1):
            button=Gtk.Button(label=str(index))
            button.connect('clicked',lambda _btn,w=workspace:self.open_program(['niri','msg','action','focus-workspace',w],f'Workspace {w}'))
            row.pack_start(button,True,True,0)
        box.pack_start(row,False,False,0)
        self.section(box,'Other')
        self.button(box,'Calendar','View the current month',lambda:self.run_bin('amethyst-calendar'))
        self.button(box,'Niri output status','See the currently detected displays in a terminal',lambda:self.open_program(['alacritty','-e','bash','-lc','niri msg outputs; echo; read -r -p "Press Enter to close"'],'Display information'))
        self.note(box,'Super+1–5 switches workspace, Super+W closes the focused window, and Super+Shift+Tab toggles tabbed columns.')

    def build_software(self, box):
        self.heading(box,'Software','Manage a curated selection of applications. Package changes still require your approval.')
        self.button(box,'Install applications','Fedora packages and optional user-scoped Flathub applications',lambda:self.run_bin('amethyst-software','install'))
        self.button(box,'Remove applications','Choose a supported program to uninstall',lambda:self.run_bin('amethyst-software','remove'))
        self.button(box,'System updates','Update Fedora packages and your Flatpak applications',lambda:self.run_bin('amethyst-software','update'))

    def build_system(self, box):
        self.heading(box,'System','Help, diagnostics, power and recovery tools.')
        self.button(box,'Keyboard shortcuts','Niri shortcut reference',lambda:self.open_program(['niri','msg','action','show-hotkey-overlay'],'Shortcut reference'))
        self.button(box,'Diagnostics','Check components and missing programs',lambda:self.open_program(['alacritty','-e',str(BIN/'amethyst-doctor')],'Diagnostics'))
        self.button(box,'Power menu','Lock, log out, reboot, and shut down',lambda:self.open_program([BIN/'powermenu'],'Power menu'))
        self.note(box,'AmethystOS uses existing Fedora packages and does not replace GNOME. For recovery, use amethystos-uninstall.')


def main():
    page = page_for(sys.argv[1] if len(sys.argv)>1 else 'home')
    window = Settings(page)
    window.show_all()
    Gtk.main()
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except ValueError as exc:
        print('AmethystOS Settings: '+str(exc),file=sys.stderr)
        sys.exit(2)
