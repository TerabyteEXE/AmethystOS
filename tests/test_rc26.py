#!/usr/bin/env python3
"""RC2.6: restrained launcher, one menu, original wallpapers retained."""
from pathlib import Path
import subprocess
import tempfile
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from deploy import install, restore
from launcher_gui import CATEGORIES,ACTIONS,matches

def test_one_search_ui():
 assert CATEGORIES==('All','Apps','Settings','Software','Wallpapers','System','Power')
 assert any(a.name=='Top bar' for a in matches('Settings','bar'))
 assert not matches('Power','appearance')
 keys=(ROOT/'payload/niri/keybinds.kdl').read_text()
 assert 'Mod+Space' in keys and 'Mod+D' in keys
 assert 'amethyst-launcher' in keys
 assert (ROOT/'payload/local-bin/amethyst-hub').read_text().count('amethyst-launcher')==1
 assert 'fuzzel' in (ROOT/'payload/local-bin/amethyst-launcher').read_text()
 assert 'launcher_gui.py' in (ROOT/'payload/local-bin/amethyst-launcher').read_text()


def test_installs_and_removes_without_patching_wallpaper():
 assert (ROOT/'assets/wallpapers/AmethystDark.png').is_file()
 assert (ROOT/'assets/wallpapers/AmethystLight.png').is_file()
 with tempfile.TemporaryDirectory() as tmp:
  home=Path(tmp)
  install(home,False,False,False)
  assert (home/'.local/share/amethystos/launcher_gui.py').is_file()
  for theme in ('dark','light'):
   assert (home/f'.local/share/amethystos/launcher/{theme}.css').is_file()
  restore(home,False)
  assert not (home/'.local/share/amethystos/launcher_gui.py').exists()

def test_bar_popups_keep_orig_style():
 for module,mode in (("clock","calendar"),("pulseaudio","audio"),("network","network"),("bluetooth","bluetooth"),("settings","settings")):
  source=(ROOT/'payload/waybar/modules'/f'{module}.jsonc').read_text()
  assert f'amethyst-popover {mode}' in source
 for theme in ('dark','light'):
  assert (ROOT/'assets/popups'/f'{theme}.css').is_file()


def test_launcher_actions_are_invokable():
  for action in ACTIONS:
    assert action.command[0].startswith(str(Path.home()/'.local/bin'))
    assert action.command[0].split('/')[-1] in __import__('deploy').EXTRA_FILES
    if action.command[0].endswith('amethyst-software'):
      assert len(action.command)==2 and action.command[1] in ('install','remove','update')

if __name__=='__main__':
 for name,fn in sorted(globals().copy().items()):
  if name.startswith('test_'):
   fn(); print('[test]',name,'OK')
