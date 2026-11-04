#!/usr/bin/env python3
"""RC2.2 regression checks; no Fedora GUI or root required."""
from __future__ import annotations
import json, os, re, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from deploy import install,restore
from appearance import apply
from setup_ui import GROUPS,create_plan

def test_named_workspaces():
 text=(ROOT/'payload/niri/config.kdl').read_text()
 keys=(ROOT/'payload/niri/keybinds.kdl').read_text()
 waybar=(ROOT/'payload/waybar/modules/workspaces.jsonc').read_text()
 for i,name in enumerate(('one','two','three','four','five'),1):
  assert f'workspace "{name}"' in text
  assert f'Mod+{i} {{ focus-workspace "{name}"; }}' in keys
  assert f'Mod+Ctrl+{i} {{ move-column-to-workspace "{name}"; }}' in keys
 assert '"format": "{icon}"' in waybar
 assert 'duration-ms 150' in text

def test_bundled_appearance():
 for name in ['dark','light']:
  for component in ['waybar/style.css','waybar/config.jsonc','kitty/kitty.conf','alacritty/alacritty.toml','fuzzel/fuzzel.ini','mako/config','gtk-3.0/settings.ini','gtk-4.0/settings.ini','qt6ct/qt6ct.conf']:
   assert (ROOT/'assets/themes'/name/component).is_file(),(name,component)
 assert (ROOT/'assets/plymouth/boot-logo.png').is_file()
 assert (ROOT/'payload/fastfetch/amethyst-logo.png').is_file()
 assert '__HOME__/.config/fastfetch/amethyst-logo.png' in (ROOT/'payload/fastfetch/config.jsonc').read_text()
 assert 'plymouth-set-default-theme "$THEME" -R' in (ROOT/'scripts/boot_theme.sh').read_text()
 assert 'plymouth-set-default-theme "$previous" -R' in (ROOT/'scripts/boot_theme.sh').read_text()


def test_themes_scale_restore():
 with tempfile.TemporaryDirectory() as temp:
  h=Path(temp)
  (h/'.config/niri').mkdir(parents=True)
  (h/'.config/niri/config.kdl').write_text('personal niri\n')
  install(h,True,False,False)
  for theme,scale in [('light',100),('dark',125),('light',150),('dark',175),('dark',100)]:
   apply(h,theme=theme,scale=scale,gtk=False,reload=False)
   data=json.loads((h/'.local/state/amethystos-base-v1/appearance.json').read_text())
   assert data=={'theme':theme,'scale':scale}
   kitty=(h/'.config/kitty/kitty.conf').read_text()
   assert 'font_size' in kitty and str(round(12.5*scale/100,1)) in kitty
  # New intentional user modification must not be silently discarded.
  mod=h/'.config/waybar/style.css'; mod.write_text(mod.read_text()+'\n/* user comment */\n')
  try:apply(h,theme='light',scale=125,gtk=False,reload=False)
  except RuntimeError as e:assert 'Modified configuration' in str(e)
  else:raise AssertionError('Theme switch overwrote a manual style edit')
  # Restore after correction; user edits still protect uninstall.
  try:restore(h,False)
  except RuntimeError as e:assert 'Refusing' in str(e)
  else:raise AssertionError('Uninstaller would discard a manual edit')
  mod.write_text(mod.read_text().removesuffix('\n/* user comment */\n'))
  restore(h,False)
  assert (h/'.config/niri/config.kdl').read_text()=='personal niri\n'
  assert not (h/'.config/waybar').exists()


def test_app_choices():
 keys={key for key,*_ in GROUPS}
 for name in ('steam','obs','discord','flatseal','krita','kdenlive','libreoffice'):
  assert name in keys
 assert create_plan(['steam','firefox'])['groups']==['firefox','steam']
 pkg=(ROOT/'scripts/packages.sh').read_text()
 for k in keys:assert f'[{k}]=' in pkg, k
 assert 'flatpak remote-add --user --if-not-exists' in pkg
 assert 'flathub' in pkg

if __name__=='__main__':
 for fn in [test_named_workspaces,test_bundled_appearance,test_themes_scale_restore,test_app_choices]:
  fn();print('[test]',fn.__name__,'OK')
