#!/usr/bin/env python3
"""RC2.4 regressions: one Settings app, GUI categories, persistent bar, close key."""
from __future__ import annotations
import configparser
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from settings_backend import (PAGES, MODULES, DENSITIES, POSITIONS, SCALES,
                              page_for, bar_action, appearance_action)
from deploy import install, restore


def test_single_settings_entry():
    directory=ROOT/'payload/applications'
    visible=[]
    for source in sorted(directory.glob('amethyst-*.desktop')):
        data=configparser.ConfigParser(interpolation=None)
        data.read(source)
        section=data['Desktop Entry']
        if section.get('NoDisplay','false').lower()!='true':
            visible.append(source.name)
        assert section.get('Exec'), source.name
    assert visible==['amethyst-control.desktop','amethyst-settings.desktop'],visible
    launcher=(ROOT/'payload/local-bin/amethyst-launcher').read_text()
    assert "Apps / Amethyst Menu: " in launcher
    hub=ROOT/'payload/local-bin/amethyst-hub'
    p=subprocess.run(['bash',str(hub),'--list'],capture_output=True,text=True,check=True)
    labels=p.stdout.splitlines()
    assert labels==['Applications','Settings','Software','Wallpapers','Calendar','Power']
    assert len(set(labels))==len(labels)


def test_settings_categories_and_input_validation():
    assert set(PAGES)=={'home','appearance','bar','devices','desktop','software','system'}
    for alias,target in {'network':'devices','scaling':'appearance','bar':'bar','updates':'software','keys':'system','menu':'home'}.items():
        assert page_for(alias)==target
    for value in ('missing','__shell','../other'):
        try:page_for(value)
        except ValueError:pass
        else:raise AssertionError('Unknown page accepted')
    assert bar_action('density','normal')==('density','normal')
    assert appearance_action('theme','light')==('theme','light')
    assert appearance_action('scale','125')==('scale','125')
    for action,value in [('toggle','bogus'),('density','giant'),('position','left')]:
        try:bar_action(action,value)
        except ValueError:pass
        else:raise AssertionError('Invalid bar setting accepted')
    for kind,value in [('scale','200'),('theme','purple')]:
        try:appearance_action(kind,value)
        except ValueError:pass
        else:raise AssertionError('Invalid appearance setting accepted')


def test_gui_shipped_and_deployed():
    gui=ROOT/'scripts/settings_gui.py'
    source=gui.read_text()
    assert 'Gtk.StackSidebar' in source
    assert 'Gtk.main()' in source
    assert 'def build_bar(' in source
    assert 'run_setting(' in source
    assert 'self.stack.set_visible_child_name' in source
    assert 'exec ' not in source
    with tempfile.TemporaryDirectory(prefix='amethyst-settings-stage-') as tmp:
        home=Path(tmp)
        install(home,False,False,False)
        for name in ('settings_gui.py','settings_backend.py'):
            assert (home/'.local/share/amethystos'/name).is_file()
        assert (home/'.local/bin/amethyst-settings').is_file()
        desktop=(home/'.local/share/applications/amethyst-settings.desktop').read_text()
        assert 'NoDisplay=true' not in desktop
        restore(home,False)


def test_close_window_and_docs():
    bindings=(ROOT/'payload/niri/keybinds.kdl').read_text()
    assert re.search(r'^\s*Mod\+W\s+repeat=false\s*\{\s*close-window;',bindings,re.M)
    assert not re.search(r'^\s*Mod\+Q\b.*\{\s*close-window;',bindings,re.M)
    assert re.search(r'^\s*Mod\+Shift\+Tab\s*\{\s*toggle-column-tabbed-display;',bindings,re.M)
    assert bindings.count('Mod+W repeat=false')==1
    assert 'Super + W' in (ROOT/'README.md').read_text()
    assert 'Super + W' in (ROOT/'wiki/index.html').read_text()
    assert 'Super + W' in (ROOT/'wiki/keybinds.html').read_text()


def test_fuzzel_fallback_menu_does_not_exit_after_change():
    with tempfile.TemporaryDirectory(prefix='amethyst-bar-fallback-') as temp:
        base=Path(temp);home=base/'home';(home/'.local/share/amethystos').mkdir(parents=True)
        binpath=base/'bin';binpath.mkdir()
        log=base/'log';state=base/'choices';state.write_text('Density — compact\nShow/hide CPU\nDone\n')
        # A minimal stand-in for the real bar manager: records calls.
        (home/'.local/share/amethystos/bar_config.py').write_text(
            f'from pathlib import Path\nimport sys\np=Path({str(log)!r})\n'
            'with p.open("a") as out: out.write(" ".join(sys.argv[1:])+"\\n")\n')
        (binpath/'fuzzel').write_text('#!/bin/sh\n'
            'choice=$(head -n 1 "$CHOICES")\n'
            'tail -n +2 "$CHOICES" > "$CHOICES.tmp"; mv "$CHOICES.tmp" "$CHOICES"\n'
            'printf "%s\\n" "$choice"\n')
        (binpath/'fuzzel').chmod(0o755)
        env={**os.environ,'HOME':str(home),'PATH':f'{binpath}:'+os.environ['PATH'],
             'CHOICES':str(state),'WAYLAND_DISPLAY':'wayland-0','DISPLAY':''}
        proc=subprocess.run(['bash',str(ROOT/'payload/local-bin/amethyst-bar'),'menu'],
                            env=env,capture_output=True,text=True,timeout=8)
        assert proc.returncode==0,proc.stderr
        assert log.read_text().splitlines()==['density compact','toggle cpu']

if __name__=='__main__':
    for key in sorted(x for x in globals() if x.startswith('test_')):
        globals()[key]()
        print('[test]',key,'OK')
