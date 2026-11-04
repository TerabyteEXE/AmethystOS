#!/usr/bin/env python3
"""Portable integration/regression tests for polish release (no Fedora needed)."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from setup_ui import create_plan, DEFAULTS
from wallpapers import install_wallpapers


def call(*cmd, env=None, ok=True):
    p = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True)
    if ok and p.returncode:
        raise AssertionError(f"{cmd}: exit={p.returncode}\nSTDOUT: {p.stdout}\nSTDERR: {p.stderr}")
    return p


def test_optional_app_plan():
    assert create_plan(['firefox','essentials'])['groups'] == ['essentials','firefox']
    assert DEFAULTS == {'firefox','essentials'}
    result = call('bash', 'install.sh', '--dry-run', '--apps=')
    assert 'Optional apps: none' in result.stdout
    assert create_plan([])['groups'] == []
    assert create_plan([], appearance=False)['apply_dark'] is False
    try: create_plan(['hijack'])
    except ValueError: pass
    else: raise AssertionError('Arbitrary package names were accepted')
    call('bash', 'install.sh', '--dry-run', '--apps=chromium,dev')
    assert 'chromium,dev' in call('bash', 'install.sh', '--dry-run', '--apps=chromium,dev').stdout
    bad = call('bash', 'install.sh', '--dry-run', '--apps=hijack', ok=False)
    assert bad.returncode != 0


def test_wallpaper_copy_and_selection():
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        result = install_wallpapers(home)
        assert sorted(result['copied']) == ['AmethystDark.png', 'AmethystLight.png']
        assert result['selected_dark']
        selection = home / '.local/state/amethystos-base-v1/wallpaper'
        assert selection.read_text().endswith('AmethystDark.png\n')
        saved_dark = home / 'Pictures/wallpapers/AmethystDark.png'
        saved_dark.write_bytes(b'custom user edit')
        custom = home / 'Pictures/wallpapers/Mine.jpg'
        custom.write_bytes(b'user image')
        selection.write_text(str(custom)+'\n')
        result = install_wallpapers(home)
        assert not result['copied'] and not result['selected_dark']
        assert saved_dark.read_bytes() == b'custom user edit'
        assert selection.read_text().strip() == str(custom)
        call('bash', str(ROOT/'payload/local-bin/set-wallpaper'), '--light',
             env={**os.environ, 'HOME': str(home), 'WAYLAND_DISPLAY':''})
        assert selection.read_text().strip() == str(home/'Pictures/wallpapers/AmethystLight.png')


def test_restore_after_upgrade():
    with tempfile.TemporaryDirectory() as tmp:
        home=Path(tmp)
        (home/'.config/niri').mkdir(parents=True)
        original=home/'.config/niri/config.kdl'
        original.write_text('original Niri user config\n')
        for _ in range(2):
            call('python3','scripts/deploy.py','install','--home',str(home),'--replace')
        restored=call('bash',str(home/'.local/bin/amethystos-uninstall'),'--yes',
                      env={**os.environ,'HOME':str(home)})
        assert 'Restoration completed' in restored.stdout
        assert original.read_text() == 'original Niri user config\n'
        assert not (home/'.local/bin/amethystos-uninstall').exists()
        assert not (home/'.local/share/applications/amethyst-settings.desktop').exists()
        assert not (home/'.local/state/amethystos-base-v1/state.json').exists()
        assert not (home/'.config/waybar').exists()


def test_gsettings_backup_and_nonclobber():
    # Stub the GSettings API in process; avoid D-Bus and host preferences.
    import desktop_prefs
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        original = {'color-scheme':'prefer-light','gtk-theme':'Adwaita','icon-theme':'Adwaita'}
        db = dict(original)
        read, write = desktop_prefs.get, desktop_prefs.set_value
        desktop_prefs.get = lambda key: db[key]
        desktop_prefs.set_value = lambda key, value: db.__setitem__(key, value)
        try:
            desktop_prefs.apply(home, 'dark')
            assert db['color-scheme'] == 'prefer-dark'
            desktop_prefs.apply(home, 'light')
            db['icon-theme'] = 'UserCustom'  # an edit outside AmethystOS
            desktop_prefs.restore(home)
            assert db['gtk-theme'] == original['gtk-theme']
            assert db['color-scheme'] == original['color-scheme']
            assert db['icon-theme'] == 'UserCustom'
        finally:
            desktop_prefs.get, desktop_prefs.set_value = read, write


def strip_jsonc(text):
    # All bundled module comments occupy their own line; trailing commas are legal JSONC.
    text=re.sub(r'^\s*//[^\n]*', '', text, flags=re.M)
    return re.sub(r',\s*([}\]])',r'\1',text)


def test_waybar_links_and_fonts():
    base=ROOT/'payload/waybar'
    main=json.loads(strip_jsonc((base/'config.jsonc').read_text()))
    for item in main['include']:
        relative=item.replace('~/.config/waybar/','')
        file=base/relative
        assert file.exists(),f'Waybar includes missing {file}'
        config=json.loads(strip_jsonc(file.read_text()))
        for settings in config.values():
            if not isinstance(settings, dict): continue
            for k,v in settings.items():
                if not isinstance(v,str): continue
                if v.startswith('~/.config/waybar/scripts/'):
                    script=v.split()[0].replace('~/.config/waybar/','')
                    assert (base/script).exists(),f'Missing Waybar action: {script}'
                if v.startswith('~/.local/bin/'):
                    command=v.split()[0].removeprefix('~/.local/bin/')
                    assert (ROOT/'payload/local-bin'/command).exists(),f'Missing app launcher: {command}'
    for filename in ['payload/alacritty/alacritty.toml','payload/kitty/kitty.conf','payload/waybar/style.css']:
        assert 'Cascadia Mono NF' in (ROOT/filename).read_text()
    assert 'cascadia-mono-nf-fonts' in (ROOT/'scripts/packages.sh').read_text()
    assert '"tray"' in (base/'config.jsonc').read_text()


def main():
    for test in [test_optional_app_plan, test_wallpaper_copy_and_selection,
                 test_restore_after_upgrade, test_gsettings_backup_and_nonclobber,
                 test_waybar_links_and_fonts]:
        test(); print('  [ok]',test.__name__)
    print('[test] Installer/UI/themes/restore integration checks: OK')

if __name__=='__main__':main()
