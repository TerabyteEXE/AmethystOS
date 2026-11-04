#!/usr/bin/env python3
"""RC2.5 regression tests: no active splash, menu reachability, Settings palettes, legacy safety."""
from __future__ import annotations
import configparser, json, tempfile, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from deploy import install, restore, digest_path, RETIRED_PATHS


def test_no_boot_modifications():
    assert not (ROOT/'scripts/boot_theme.sh').exists()
    assert not (ROOT/'assets/plymouth').exists()
    assert not (ROOT/'payload/local-bin/amethyst-boot').exists()
    assert 'boot-splash' not in (ROOT/'install.sh').read_text()
    assert 'plymouth-set-default-theme' not in (ROOT/'install.sh').read_text()
    ui=(ROOT/'scripts/setup_ui.py').read_text()
    assert "--boot-splash" not in ui and "boot=boot" not in ui
    assert 'Boot splash' not in (ROOT/'scripts/settings_gui.py').read_text()
    assert 'boot' not in __import__('settings_backend').ALIASES
    assert all('amethyst-boot' not in str(src) for src,_ in __import__('deploy').sources())


def test_menu_access_via_search():
    entries=[]
    for file in sorted((ROOT/'payload/applications').glob('amethyst-*.desktop')):
        cp=configparser.ConfigParser(interpolation=None)
        cp.read(file)
        if cp['Desktop Entry'].get('NoDisplay','false').lower()!='true':
            entries.append(cp['Desktop Entry']['Name'])
    assert entries==['Amethyst Menu','Amethyst Settings'],entries
    launcher=(ROOT/'payload/local-bin/amethyst-launcher').read_text()
    assert 'Apps / Amethyst Menu:' in launcher
    hub=(ROOT/'payload/local-bin/amethyst-hub').read_text()
    assert 'amethyst-launcher' in hub
    from launcher_gui import CATEGORIES
    assert set(('Apps','Settings','Software','Wallpapers','System','Power')).issubset(CATEGORIES)
    keys=(ROOT/'payload/niri/keybinds.kdl').read_text()
    assert 'Mod+Space repeat=false' in keys and 'Mod+D repeat=false' in keys


def test_palette_deployed_and_light_dark():
    for name in ('dark','light'):
        css=(ROOT/'assets/settings'/f'{name}.css').read_text()
        assert 'window#amethyst-settings' in css
        assert 'stacksidebar row:selected' in css
        assert css.count('{')==css.count('}')
    code=(ROOT/'scripts/settings_gui.py').read_text()
    assert '_apply_style(self.appearance_prefs' in code
    assert "self._apply_style(self.appearance_prefs.get('theme','dark'))" in code
    with tempfile.TemporaryDirectory() as tmp:
        home=Path(tmp)
        install(home,False,False,False)
        assert (home/'.local/share/amethystos/settings/light.css').is_file()
        assert (home/'.local/share/amethystos/settings/dark.css').is_file()
        assert (home/'.local/share/amethystos/assets/amethyst-logo.png').is_file()
        restore(home,False)


def test_retire_old_user_splash_without_touching_system():
    with tempfile.TemporaryDirectory() as temp:
        home=Path(temp)
        install(home,False,False,False)
        statefile=home/'.local/state/amethystos-base-v1/state.json'
        state=json.loads(statefile.read_text())
        original=home/'.local/state/amethystos-base-v1/backups/original/.local/bin/amethyst-boot'
        original.parent.mkdir(parents=True,exist_ok=True)
        original.write_text('user original tool\n')
        # Fake an old managed install with three obsolete paths.
        for rel in RETIRED_PATHS:
            path=home/rel
            path.parent.mkdir(parents=True,exist_ok=True)
            if rel.endswith('plymouth'):
                path.mkdir()
                (path/'amethystos.plymouth').write_text('old managed theme\n')
            else:
                path.write_text('#!/bin/sh\n# old managed\n')
            state['entries'].append({'path':rel, 'backup':str(original.relative_to(home)) if rel.endswith('amethyst-boot') else None,
                                     'sha256':digest_path(path)})
        statefile.write_text(json.dumps(state))
        install(home,True,False,False)
        assert (home/'.local/bin/amethyst-boot').read_text()=='user original tool\n'
        assert not (home/'.local/share/amethystos/boot_theme.sh').exists()
        assert not (home/'.local/share/amethystos/assets/plymouth').exists()
        now=json.loads(statefile.read_text())
        assert not any(e['path'] in RETIRED_PATHS for e in now['entries'])
        restore(home,False)
        assert (home/'.local/bin/amethyst-boot').read_text()=='user original tool\n'


def test_preserve_user_changed_retired_script():
    with tempfile.TemporaryDirectory() as temp:
        home=Path(temp)
        install(home,False,False,False)
        statefile=home/'.local/state/amethystos-base-v1/state.json'
        state=json.loads(statefile.read_text())
        legacy=home/'.local/bin/amethyst-boot'
        legacy.write_text('#!/bin/sh\n# user-edited old tool\n')
        state['entries'].append({'path':'.local/bin/amethyst-boot','backup':None,'sha256':'not-the-hash'})
        statefile.write_text(json.dumps(state))
        install(home,True,False,False)
        assert 'user-edited' in legacy.read_text()
        after=json.loads(statefile.read_text())
        assert any(e['path']=='.local/bin/amethyst-boot' for e in after['entries'])
        try:restore(home,False)
        except RuntimeError as exc: assert 'Refusing' in str(exc)
        else:raise AssertionError('Unexpectedly removed user-edited legacy script')


if __name__=='__main__':
    for name,fn in sorted(globals().copy().items()):
        if name.startswith('test_'):
            fn()
            print('[test]',name,'OK')
