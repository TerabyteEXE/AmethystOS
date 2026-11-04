#!/usr/bin/env python3
"""Offline RC2.3 tests: persistent Waybar, launcher, wallpaper, software actions."""
from __future__ import annotations
import configparser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from deploy import install,restore
from bar_config import change,load,render
from appearance import apply
from wallpaper_gui import wallpapers
from software import command, APPS


def test_bar_customization_and_rollback():
    with tempfile.TemporaryDirectory() as tmp:
        h=Path(tmp)/'user';h.mkdir()
        (h/'.config/niri').mkdir(parents=True)
        (h/'.config/niri/config.kdl').write_text('custom\n')
        install(h,True,False,False)
        change(h,position='bottom',density='compact',toggle='cpu',reload=False)
        prefs=load(h)
        assert prefs['position']=='bottom' and prefs['density']=='compact'
        assert prefs['modules']['cpu'] is False
        def check(expected_font):
            cfg=(h/'.config/waybar/config.jsonc').read_text()
            css=(h/'.config/waybar/style.css').read_text()
            assert '"position": "bottom"' in cfg
            assert '"cpu"' not in re.search(r'"modules-right"\s*:\s*\[([^]]+)\]',cfg).group(1)
            assert f'window#waybar {{ font-size: {expected_font}px; }}' in css
        check(11)
        apply(h,theme='light',scale=125,gtk=False,reload=False)
        check(14)
        # Correctly refuses to reset manual Waybar user changes.
        p=h/'.config/waybar/style.css';p.write_text(p.read_text()+'\n/* external edit */\n')
        try:change(h,density='roomy',reload=False)
        except RuntimeError as exc:assert 'Modified configuration' in str(exc)
        else:raise AssertionError('User edits overwritten')
        assert load(h)['density']=='compact'
        p.write_text(p.read_text().removesuffix('\n/* external edit */\n'))
        restore(h,False)
        assert (h/'.config/niri/config.kdl').read_text()=='custom\n'


def test_shortcut_collision_free_and_search():
    text=(ROOT/'payload/niri/keybinds.kdl').read_text()
    matches=re.findall(r'^\s*((?:Mod|Ctrl|Alt|Shift|Super|XF86|Print)[^\s{]*)\s+(?:repeat=false\s+)?(?:hotkey-overlay-title="[^"]*"\s+)?\{',text,re.M)
    assert len(matches)==len(set(matches)), 'Duplicate active Niri shortcut'
    assert 'Mod+Space repeat=false' in text and 'amethyst-launcher' in text
    assert 'Mod+D repeat=false' in text and 'amethyst-launcher' in text
    assert 'Mod+Shift+D' in text
    assert 'amethyst-wallpapers' in text


def test_apps_staged_and_executable():
    with tempfile.TemporaryDirectory() as tmp:
        h=Path(tmp)/'person';h.mkdir()
        install(h,True,False,False)
        for name in ('amethyst-launcher','amethyst-bar','amethyst-wallpapers',
                     'amethyst-calendar','amethyst-software','amethyst-hub'):
            path=h/'.local/bin'/name
            assert path.is_file() and os.access(path,os.X_OK), path
        for source in (ROOT/'payload/applications').glob('*.desktop'):
            target=h/'.local/share/applications'/source.name
            assert target.is_file()
            cp=configparser.ConfigParser(interpolation=None)
            cp.read(target)
            assert cp.get('Desktop Entry','Exec')
            assert '__HOME__' not in target.read_text()
        restore(h,False)


def test_software_safe_commands():
    assert command('install','steam')==['flatpak','install','--user','flathub','com.valvesoftware.Steam']
    assert command('remove','gimp')==['sudo','dnf','remove','gimp']
    assert len(APPS)>12
    try:command('remove','unsafe-package')
    except ValueError:pass
    else:raise AssertionError('Arbitrary packages are not allowed')


def test_wallpaper_listing():
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)
        for name in ('C.jpg','B.webp','A.png','bad.txt'):(p/name).write_bytes(b'test')
        assert [x.name for x in wallpapers(p)]==['A.png','B.webp','C.jpg']


def test_launcher_repeat_toggle():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);binpath=root/'bin';binpath.mkdir();runtime=root/'run'
        # Fake fuzzel: a harmless sleeping process. It can be killed only via
        # the PID created by the Amethyst wrapper.
        exe=binpath/'fuzzel'
        exe.write_text('#!/bin/bash\nexec -a fuzzel sleep 10\n')
        exe.chmod(0o755)
        env=dict(os.environ,PATH=f'{binpath}:'+os.environ['PATH'],XDG_RUNTIME_DIR=str(runtime))
        script=ROOT/'payload/local-bin/amethyst-launcher'
        first=subprocess.Popen(['bash',str(script)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        pidfile=runtime/'amethystos/launcher.pid'
        for _ in range(50):
            if pidfile.is_file():break
            time.sleep(.05)
        else:
            first.kill();raise AssertionError('Launcher state not created')
        second=subprocess.run(['bash',str(script)],env=env,capture_output=True,text=True,timeout=5)
        assert second.returncode==0,second.stderr
        first.wait(timeout=5)
        assert first.returncode==0

if __name__=='__main__':
    for name in sorted(x for x in globals() if x.startswith('test_')):
        globals()[name]()
        print('[test]',name,'OK')
