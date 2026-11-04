#!/usr/bin/env python3
"""RC2.7 regression checks for the keyboard-first Amethyst Home + local popovers."""
from pathlib import Path
import importlib.util
import sys
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from launcher_gui import HOME_SECTIONS,SECTIONS,LEGACY_MAP,search_menu,ACTIONS,MenuItem
import bar_popup


def test_home_categories_and_keyboard_contract():
    assert tuple(item.title for item in HOME_SECTIONS)==(
        'Apps','Learn','Style','Setup','Install','Remove','Update','About','System','Power')
    assert search_menu('', 'Home')==list(HOME_SECTIONS)
    assert search_menu('style','Home')[0].section=='Style'
    assert any(item.title=='Top bar' for item in search_menu('bar','Home'))
    assert any(item.title=='Amethyst Settings' for item in search_menu('amethyst','Setup'))
    assert not search_menu('unrelated nonsense','Setup')
    assert any(item.title=='Firefox' for item in search_menu('fire','Apps',[('Firefox',object())]))
    assert any(item.title=='Firefox' for item in search_menu('fire','Home',[('Firefox',object())]))
    assert all(item.title in SECTIONS or item.title=='Apps' for item in HOME_SECTIONS)
    assert LEGACY_MAP['Settings']=='Setup'
    code=(ROOT/'scripts/launcher_gui.py').read_text()
    for name in ('Down','Up','Return','KP_Enter','Right','Left','Escape','search-changed'):
        assert name in code,name
    assert 'shell=True' not in code


def test_same_super_d_and_super_space_menu():
    lines=(ROOT/'payload/niri/keybinds.kdl').read_text().splitlines()
    bindings=[l for l in lines if 'Mod+Space repeat=false' in l or 'Mod+D repeat=false' in l]
    assert len(bindings)==2
    assert all('amethyst-launcher' in line for line in bindings)
    assert all('--category' not in line for line in bindings)
    assert 'amethyst-launcher' in (ROOT/'payload/local-bin/amethyst-hub').read_text()
    assert 'open-floating true' in (ROOT/'payload/niri/window_rules.kdl').read_text()


def test_popover_personal_status_and_switching():
    assert 'Hello, {getpass.getuser()}' in (ROOT/'scripts/bar_popup.py').read_text()
    assert 'Back to today' in (ROOT/'scripts/bar_popup.py').read_text()
    assert 'Volume:' in (ROOT/'scripts/bar_popup.py').read_text()
    assert 'bar-popup.mode' in (ROOT/'payload/local-bin/amethyst-popover').read_text()
    assert 'amethyst-popover' in (ROOT/'payload/local-bin/amethyst-calendar').read_text()
    with patch.object(bar_popup,'read_output',return_value='Volume: 0.47'):
        assert bar_popup.volume_percent()==47
    with patch.object(bar_popup,'read_output',return_value='*:HomeNetwork\n:CoffeeShop'):
        assert bar_popup.active_wifi()=='HomeNetwork'
    with patch.object(bar_popup,'read_output',return_value='Powered: yes'):
        assert bar_popup.bluetooth_powered() is True
    with patch.object(bar_popup,'read_output',return_value=''):
        assert bar_popup.bluetooth_powered() is None


def test_styles_preserve_original_wallpapers():
    for theme in ('dark','light'):
        css=(ROOT/'assets/launcher'/f'{theme}.css').read_text()
        popup=(ROOT/'assets/popups'/f'{theme}.css').read_text()
        assert 'rgba(' in css and 'rgba(' in popup
    for name in ('AmethystDark.png','AmethystLight.png'):
        assert (ROOT/'assets/wallpapers'/name).is_file()

if __name__=='__main__':
    for name,fn in sorted(globals().copy().items()):
        if name.startswith('test_'):
            fn(); print('[test]',name,'OK')
