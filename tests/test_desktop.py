#!/usr/bin/env python3
"""Portable test suite for the official-Fedora Noctalia v5 migration."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import deploy
from setup_ui import create_plan, GROUPS


def check_configuration():
    P=ROOT/'payload'
    shell=tomllib.loads((P/'noctalia/config.toml').read_text())
    assert shell['theme']['source']=='custom'
    assert shell['theme']['custom_palette']=='Amethyst'
    assert shell['shell']['launcher']['layout']=='full'
    palette=json.loads((P/'noctalia/palettes/Amethyst.json').read_text())
    assert palette['dark']['mPrimary']=='#B48AF2'
    assert palette['light']['mPrimary']=='#7035AB'
    assert (P/'noctalia/settings.json').exists() is False
    assert not (P/'noctalia/plugins').exists()
    for path in (P/'niri/modules/autostarts.kdl',P/'niri/modules/keybinds.kdl'):
        txt=path.read_text()
        assert 'qs -c noctalia-shell' not in txt, path
    assert 'spawn-at-startup "noctalia"' in (P/'niri/modules/autostarts.kdl').read_text()
    assert '"amethyst-welcome"' in (P/'niri/modules/autostarts.kdl').read_text()
    kb=(P/'niri/modules/keybinds.kdl').read_text()
    assert 'Super+W repeat=false { close-window; }' in kb
    assert 'noctalia msg panel-toggle launcher' in kb
    assert 'noctalia msg session lock' in kb
    assert 'Ctrl+Super+K' in kb
    for i in range(1,6):assert f'Super+{i}' in kb
    assert (P/'local-bin/amethyst-welcome').exists()
    assert (P/'applications/amethyst-welcome.desktop').exists()
    assert 'noctalia msg settings-open' in (P/'local-bin/amethyst-settings').read_text()
    assert 'noctalia msg theme-mode-set' in (P/'local-bin/amethyst-theme').read_text()
    assert 'noctalia msg wallpaper-set' in (P/'local-bin/amethyst-wallpaper').read_text()
    for name in ('AmethystDark.png','AmethystLight.png'):
        assert (ROOT/'assets/wallpapers'/name).stat().st_size>100000
    assert (ROOT/'third_party/gigis-rice/LICENSE').read_bytes()==(ROOT/'LICENSE.gigi').read_bytes()
    assert 'Gigi' in (ROOT/'README.md').read_text().split('## Attribution and licenses')[-1]
    for file in (ROOT/'index.html',ROOT/'install.html',ROOT/'about.html'):
        text=file.read_text().lower()
        assert 'noctalia v5' in text or file.name=='about.html'
        assert 'gigi' not in text
    print('[ok] v5 shell, Niri bindings, branding and website')


def check_selections():
    keys={item[0] for item in GROUPS}
    for key in ('steam','krita','libreoffice','obs','calculator','vscode'):
        assert key in keys,key
    p=create_plan(['steam','krita'],True,True,'light')
    assert p['groups']==['krita','steam']
    assert p['replace'] and p['theme']=='light'
    assert create_plan([])['groups']==[]
    output=subprocess.run([sys.executable,str(ROOT/'scripts/setup_ui.py'), '--output','/dev/null', '--non-interactive','--groups='],capture_output=True,text=True)
    assert output.returncode==0,output.stderr
    print('[ok] individual app choices and noninteractive installer')


def check_deploy():
    with tempfile.TemporaryDirectory() as tmp:
        home=Path(tmp)/'home'
        old=home/'.config/niri';old.mkdir(parents=True)
        (old/'config.kdl').write_text('previous desktop\n')
        noct=home/'.config/noctalia';noct.mkdir(parents=True)
        (noct/'settings.json').write_text('{"legacy":true}\n')
        try:deploy.install(home,replace=False,dry_run=False,require_niri=False)
        except RuntimeError:pass
        else:raise AssertionError('Installer overwrote settings without opt-in')
        assert (old/'config.kdl').read_text()=='previous desktop\n'
        deploy.install(home,replace=True,dry_run=True,require_niri=False)
        assert (noct/'settings.json').is_file()
        deploy.install(home,replace=True,dry_run=False,require_niri=False)
        assert (noct/'config.toml').is_file()
        assert not (noct/'settings.json').exists()
        assert (home/'.local/bin/amethyst-welcome').is_file()
        assert (home/'.local/share/applications/amethyst-welcome.desktop').is_file()
        assert (home/'.local/share/icons/hicolor/128x128/apps/amethystos.png').is_file()
        state=home/'.local/state/amethystos-base-v1/state.json'
        assert state.is_file()
        deploy.install(home,replace=True,dry_run=False,require_niri=False)
        rec=next(x for x in json.loads(state.read_text())['entries'] if x['path']=='.config/noctalia')
        assert rec['backup']
        modified=home/'.config/niri/modules/keybinds.kdl'
        orig=modified.read_text()
        modified.write_text(orig+'// user change\n')
        try:deploy.restore(home,dry_run=False)
        except RuntimeError:pass
        else:raise AssertionError('Uninstaller clobbered modified file')
        modified.write_text(orig)
        deploy.restore(home,dry_run=False)
        assert (noct/'settings.json').is_file()
        assert (old/'config.kdl').read_text()=='previous desktop\n'
    print('[ok] existing v4 config backed up, protected on edits and restored')


def check_wallpaper():
    from wallpapers import install_wallpapers
    with tempfile.TemporaryDirectory() as tmp:
        home=Path(tmp)
        result=install_wallpapers(home,theme='light')
        assert result['selected_dark']
        file=(home/'Pictures/wallpapers/AmethystLight.png')
        assert (home/'.local/state/amethystos-base-v1/wallpaper').read_text().strip()==str(file)
        # Existing selection, including custom artwork, is never reset by an upgrade.
        manual=home/'Pictures/wallpapers/my.png';manual.write_bytes(b'user data')
        chosen=home/'.local/state/amethystos-base-v1/wallpaper'
        chosen.write_text(str(manual)+'\n')
        install_wallpapers(home,theme='dark')
        assert chosen.read_text().strip()==str(manual)
    print('[ok] light and dark wallpaper selection preserved')

if __name__=='__main__':
    check_configuration();check_selections();check_deploy();check_wallpaper()
