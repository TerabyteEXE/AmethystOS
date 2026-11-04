#!/usr/bin/env python3
"""RC2.10: readable/consistent custom GUIs with defensive scaling."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from ui_style import appearance, css_rules, window_size, px
from launcher_gui import panel_size
from bar_config import load as load_bar, render as render_bar
from deploy import install, restore
from appearance import apply


def test_corrupt_preferences_never_crash_a_gui():
    with tempfile.TemporaryDirectory() as folder:
        home = Path(folder)
        state = home/'.local/state/amethystos-base-v1/appearance.json'
        state.parent.mkdir(parents=True)
        assert appearance(home) == ('dark',100)
        for data in ('oops', '[]', '{"theme":"dark","scale":1000}', '{"theme":"blue","scale":115}'):
            state.write_text(data)
            theme,scale=appearance(home)
            assert theme in ('light','dark') and scale in (100,115,125,150,175)
        state.write_text('{"theme":"light","scale":150}')
        assert appearance(home) == ('light',150)


def test_geometry_and_css_are_readable_and_bounded():
    assert px(14,150) == 21
    for scale in (100,115,125,150,175):
        w,h = panel_size('Home',scale,1366,768)
        assert 250 <= w <= 1366*.88 and h <= 768*.85
        assert panel_size('Apps',scale,1366,768)[0] >= w
        assert window_size(870,610,scale,1024,768)[0] <= 1024*.88
        for kind in ('launcher','settings','popup','gallery'):
            css = css_rules(kind,scale)
            assert f'{scale}%' in css and 'font-size:' in css and 'min-height:' in css
            assert css.count('{') == css.count('}')
    assert int(css_rules('launcher',150).split('font-size: ')[1].split('px')[0]) > int(css_rules('launcher',100).split('font-size: ')[1].split('px')[0])
    try: css_rules('other',100)
    except ValueError: pass
    else: assert False, 'Unknown app accepted for CSS overrides'


def test_launcher_sets_scale_before_sizing():
    code = (ROOT/'scripts/launcher_gui.py').read_text()
    initialization = code[code.index('class Home(Gtk.Window):'):code.index('def load_style(self):')]
    assert initialization.index('self.theme, self.ui_scale = ui_appearance()') < initialization.index("panel_size('Home', self.ui_scale")
    assert 'install_override(Gtk, Gdk' in initialization
    assert 'glyph.set_pixel_size(px(19, self.ui_scale))' in code


def test_waybar_density_respects_scale_without_color_replacement():
    config = (ROOT/'payload/waybar/config.jsonc').read_text()
    style = (ROOT/'payload/waybar/style.css').read_text()
    with tempfile.TemporaryDirectory() as folder:
        prefs = load_bar(Path(folder))
    _, normal = render_bar(config,style,prefs,scale=100)
    _, large = render_bar(config,style,prefs,scale=150)
    assert 'window#waybar { font-size: 13px; }' in normal
    assert 'window#waybar { font-size: 20px; }' in large
    assert normal.count('AmethystOS bar preferences') == 1
    assert '#custom-logo' in large
    for theme in ('dark','light'):
        for kind in ('launcher','settings','popups','gallery'):
            path = ROOT/'assets'/kind/f'{theme}.css'
            assert path.is_file() and 'Amethyst' in path.read_text()


def test_gtk4_files_are_real_css_and_match_modes():
    for theme in ('dark','light'):
        for name in ('gtk.css','gtk-dark.css'):
            p = ROOT/'assets/themes'/theme/'gtk-4.0'/name
            content = p.read_text(encoding='utf-8')
            assert '@define-color accent_color' in content
            assert '\x00' not in content and 'IntxLNK' not in content
    assert (ROOT/'assets/themes/dark/gtk-4.0/gtk.css').read_text() != (ROOT/'assets/themes/light/gtk-4.0/gtk.css').read_text()


def test_install_theme_scale_restore():
    with tempfile.TemporaryDirectory(prefix='amethyst-rc210-') as folder:
        home=Path(folder)
        install(home,False,False,False)
        assert (home/'.local/share/amethystos/ui_style.py').is_file()
        apply(home,theme='light',scale=150,gtk=False,reload=False)
        saved=json.loads((home/'.local/state/amethystos-base-v1/appearance.json').read_text())
        assert saved == {'theme':'light','scale':150}
        css=(home/'.config/waybar/style.css').read_text()
        assert 'window#waybar { font-size: 20px; }' in css
        restore(home,False)
        assert not (home/'.local/share/amethystos/ui_style.py').exists()

if __name__=='__main__':
    for name,fun in sorted(globals().copy().items()):
        if name.startswith('test_'):
            fun()
            print('[test]',name,'OK')
