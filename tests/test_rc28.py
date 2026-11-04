#!/usr/bin/env python3
"""RC2.8: compact menu, conventional text editing, no changes to desktop base."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from launcher_gui import (HOME_SECTIONS, search_menu, input_edit_intent, panel_size, SECTIONS)


def test_search_and_drill_down():
    assert len(HOME_SECTIONS) == 10
    assert search_menu('', 'Home') == list(HOME_SECTIONS)
    assert search_menu('Apps', 'Home')[0].section == 'Apps'
    apps = [('Alacritty', object()), ('Firefox', object())]
    assert [x.title for x in search_menu('fire', 'Apps', apps)] == ['Firefox']
    assert [x.title for x in search_menu('fire', 'Home', apps)] == ['Firefox']
    assert 'Style' in SECTIONS and 'Power' in SECTIONS


def test_text_editing_precedes_back_navigation():
    # A nonempty entry must be edited with GTK's own editing functions.
    assert input_edit_intent('BackSpace', 'hello', True, 'Home') == 'native'
    assert input_edit_intent('BackSpace', 'hello', True, 'Apps') == 'native'
    assert input_edit_intent('Delete', 'hello', True, 'Apps') == 'native'
    # Clicking a result may focus it: send deletion back to the search entry.
    assert input_edit_intent('BackSpace', 'hello', False, 'Apps') == 'delete-left'
    assert input_edit_intent('Delete', 'hello', False, 'Apps') == 'delete-right'
    # Empty Backspace navigates, Delete never does.
    assert input_edit_intent('BackSpace', '', True, 'Home') == 'ignore'
    assert input_edit_intent('BackSpace', '', True, 'Apps') == 'back'
    assert input_edit_intent('Delete', '', True, 'Apps') == 'native'
    assert input_edit_intent('Delete', '', False, 'Apps') == 'ignore'


def test_visual_contract_and_shortcuts():
    w, h = panel_size('Home')
    aw, ah = panel_size('Apps')
    assert 250 <= w <= 320 and 350 <= h <= 460
    assert aw > w and ah >= h-20
    code = (ROOT/'scripts/launcher_gui.py').read_text()
    assert 'Gtk.Entry()' in code
    assert 'self.entry.connect(\'key-press-event\', self.on_key)' in code
    assert "self.connect('key-press-event', self.on_key)" not in code
    assert 'self.entry.set_placeholder_text(\'Go...\')' in code
    assert 'self.entry.get_text()' in code
    assert 'Delete' in code and 'BackSpace' in code
    assert 'Ctrl' not in code or 'CONTROL_MASK' in code
    for theme in ('dark','light'):
        css = (ROOT/'assets/launcher'/f'{theme}.css').read_text()
        assert 'row:selected' in css and '#amethyst-home-search' in css
        assert 'rgba' in css
    binds = (ROOT/'payload/niri/keybinds.kdl').read_text()
    assert 'Mod+Space repeat=false' in binds and 'Mod+D repeat=false' in binds
    assert 'amethyst-launcher' in binds
    assert (ROOT/'assets/wallpapers/AmethystDark.png').is_file()
    assert (ROOT/'assets/wallpapers/AmethystLight.png').is_file()


if __name__ == '__main__':
    for name, test in sorted(globals().copy().items()):
        if name.startswith('test_'):
            test(); print('[test]', name, 'OK')
