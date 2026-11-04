#!/usr/bin/env python3
"""RC2.9: focus/scroll, icon integration, source update safety, visual cohesion."""
from pathlib import Path
import io
import stat
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from launcher_gui import scroll_target
from system_update import safely_extract, source_urls, main as update_main


def archive(sha, entries):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        for path, contents in entries.items():
            z.writestr(f'AmethystOS-{sha}/{path}', contents)
    return out.getvalue()


def test_scrolling():
    assert scroll_target(0, 100, 500, 105, 20) == 31
    assert scroll_target(120, 100, 500, 20, 20) == 14
    assert scroll_target(399, 100, 500, 499, 20) == 400
    assert scroll_target(0, 500, 500, 10, 20) == 0
    code = (ROOT/'scripts/launcher_gui.py').read_text()
    assert 'self._scroll_selected()' in code
    assert 'Gtk.Image.new_from_gicon' in code
    assert 'self.hide()' in code
    assert 'self.set_app_paintable(True)' in code


def test_updater_safety():
    sha = '1'*40
    uri, review = source_urls(sha)
    assert uri.endswith(sha) and review.endswith(sha)
    for bad in ('main','1'*39, '../foo','1'*41):
        try: source_urls(bad)
        except ValueError: pass
        else: assert False, 'Unpinned ref accepted'
    assert update_main(['all','--dry-run']) == 0
    good = archive(sha, {
        'install.sh':'#!/usr/bin/env bash\n',
        'LICENSE':'MIT\n',
        'VERSION':'1.0\n',
        'scripts/deploy.py':'# test\n',
    })
    with tempfile.TemporaryDirectory() as t:
        dest=Path(t)/'repo'
        assert safely_extract(good,dest,sha) == dest
        assert (dest/'install.sh').exists()
    bad_zip=archive(sha, {'../escape':'oops'})
    with tempfile.TemporaryDirectory() as t:
        try: safely_extract(bad_zip,Path(t),sha)
        except ValueError: pass
        else: assert False, 'Archive traversal was accepted'
    code=(ROOT/'scripts/system_update.py').read_text()
    assert 'confirm(' in code and "'--preserve-appearance'" in code
    assert "'--no-packages'" in code


def test_cohesion_and_deployment():
    deploy=(ROOT/'scripts/deploy.py').read_text()
    assert 'system_update.py' in deploy and 'amethyst-update' in deploy
    assert 'assets/gallery' in deploy and 'VERSION' in deploy
    assert 'PRESERVE_APPEARANCE' in (ROOT/'install.sh').read_text()
    assert 'set_namespace' in (ROOT/'scripts/bar_popup.py').read_text()
    assert 'close=True' in (ROOT/'scripts/bar_popup.py').read_text()
    assert 'amethyst-popup' in (ROOT/'payload/niri/window_rules.kdl').read_text()
    assert "from system_update import main as update_main" in (ROOT/'scripts/software.py').read_text()
    for theme in ('dark','light'):
        for part in ('launcher','popups','gallery','settings'):
            css = (ROOT/f'assets/{part}/{theme}.css').read_text()
            assert 'rgba(' in css, part
        assert 'background:' in (ROOT/f'assets/themes/{theme}/waybar/style.css').read_text()
    assert 'load_from_path(str(css))' in (ROOT/'scripts/wallpaper_gui.py').read_text()
    assert 'amethyst-still' not in (ROOT/'scripts/wallpaper_gui.py').read_text().casefold()

if __name__=='__main__':
    for name, item in sorted(globals().copy().items()):
        if name.startswith('test_'):
            item()
            print('[test]', name, 'OK')
