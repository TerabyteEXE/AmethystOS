#!/usr/bin/env python3
"""AmethystOS palette and font scaling for managed desktop configuration.

Never edits Niri's compositor scale/output settings. Niri and native Wayland
clients handle per-monitor DPI; this adjusts text sizes when explicitly chosen.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
import subprocess
from deploy import digest_path

THEME_FILES=(
 'waybar/style.css','waybar/config.jsonc','kitty/kitty.conf','alacritty/alacritty.toml',
 'fuzzel/fuzzel.ini','mako/config','gtk-3.0/settings.ini',
 'gtk-4.0/settings.ini','qt6ct/qt6ct.conf',
)
VALID_SIZES=(100,115,125,150,175)

def state_path(home): return home/'.local/state/amethystos-base-v1/appearance.json'
def root(home): return home/'.local/share/amethystos'

def managed_preflight(home):
 state=home/'.local/state/amethystos-base-v1/state.json'
 if not state.exists(): raise RuntimeError('AmethystOS deployment state missing; install the desktop first')
 data=json.loads(state.read_text())
 names={str(Path('.config')/f.split('/')[0]) for f in THEME_FILES}
 managed={rec['path']:rec for rec in data['entries']}
 for name in names:
  rec=managed.get(name)
  if rec is None: raise RuntimeError('Unmanaged configuration: '+name)
  p=home/name
  if not p.exists() or digest_path(p)!=rec['sha256']:
   raise RuntimeError('Modified configuration in '+name+'; preserving your edit. Restore or reinstall with backups before using the theme manager.')
 return state,data,names

def scaled_text(rel,text,size):
 factor=size/100
 if rel=='waybar/style.css':
  # Scale geometry too, not just glyphs: padding, margins and rounded corners.
  return re.sub(r'(?<![0-9A-Za-z.])([0-9]+(?:\.[0-9]+)?)px\b',lambda m:str(max(1,round(float(m[1])*factor)))+'px',text)
 if rel=='waybar/config.jsonc':
  return re.sub(r'("icon-size"\s*:\s*)14\b',lambda m:m[1]+str(round(14*factor)),text,count=1)
 if rel=='kitty/kitty.conf':
  return re.sub(r'(?m)^(font_size\s+)\d+(?:\.\d+)?',lambda m:m[1]+str(round(12.5*factor,1)),text,count=1)
 if rel=='alacritty/alacritty.toml':
  return re.sub(r'(?m)^(\[font\]\s*\nsize\s*=\s*)\d+(?:\.\d+)?',lambda m:m[1]+str(round(12.5*factor,1)),text,count=1)
 if rel=='fuzzel/fuzzel.ini':
  text=re.sub(r'(font=[^\n]*:size=)\d+(?:\.\d+)?',lambda m:m[1]+str(round(12*factor,1)),text,count=1)
  return re.sub(r'(?m)^(horizontal-pad|vertical-pad|inner-pad|line-height)=(\d+)',lambda m:m[1]+'='+str(round(int(m[2])*factor)),text)

 if rel=='mako/config':
  text=re.sub(r'(?m)^(font=Cascadia Mono NF )\d+',lambda m:m[1]+str(round(11*factor)),text,count=1)
  return re.sub(r'(?m)^(width|height|margin|max-icon-size|border-radius)=(\d+)',lambda m:m[1]+'='+str(round(int(m[2])*factor)),text)

 if rel.startswith('gtk-'):
  return re.sub(r'(?m)^(gtk-font-name=Noto Sans )\d+',lambda m:m[1]+str(round(11*factor)),text,count=1)
 if rel=='qt6ct/qt6ct.conf':
  return re.sub(r'(Noto Sans,)11',lambda m:m[1]+str(round(11*factor)),text)
 return text


def change_text_scale(home, size):
    """Write a reversible GSettings text multiplier, only for the real user session."""
    if home != Path.home().resolve() or not shutil_which('gsettings'):
        return
    pref = home/'.local/state/amethystos-base-v1/text-scale-prefs.json'
    cmd=['gsettings','get','org.gnome.desktop.interface','text-scaling-factor']
    result=subprocess.run(cmd,capture_output=True,text=True)
    if result.returncode: return
    current=result.stdout.strip()
    if pref.exists():
        state=json.loads(pref.read_text())
    else:
        state={'original':current,'written':None}
    if size==100:
        if state['written'] is not None and current==state['written']:
            subprocess.run(['gsettings','set','org.gnome.desktop.interface','text-scaling-factor',state['original']],check=False)
            pref.unlink(missing_ok=True)
        return
    val=str(size/100)
    if subprocess.run(['gsettings','set','org.gnome.desktop.interface','text-scaling-factor',val],check=False).returncode==0:
        state['written']=val
        pref.parent.mkdir(parents=True,exist_ok=True)
        pref.write_text(json.dumps(state,indent=2)+'\n')

def restore_text_scale(home):
    home=Path(home).resolve()
    pref=home/'.local/state/amethystos-base-v1/text-scale-prefs.json'
    if not pref.exists():return
    if home==Path.home().resolve() and shutil_which('gsettings'):
        state=json.loads(pref.read_text())
        current=subprocess.run(['gsettings','get','org.gnome.desktop.interface','text-scaling-factor'],capture_output=True,text=True)
        if current.returncode==0 and current.stdout.strip()==state.get('written'):
            subprocess.run(['gsettings','set','org.gnome.desktop.interface','text-scaling-factor',state['original']],check=False)
    pref.unlink(missing_ok=True)

def apply(home,theme=None,scale=None,gtk=True,reload=True):
 home=Path(home).resolve()
 pref=state_path(home)
 saved=json.loads(pref.read_text()) if pref.exists() else {'theme':'dark','scale':100}
 theme=theme or saved['theme']; scale=int(scale if scale is not None else saved['scale'])
 if theme not in ('dark','light'): raise ValueError('Theme must be dark or light')
 if scale not in VALID_SIZES: raise ValueError('Choose 100, 115, 125, 150 or 175')
 state, data, names=managed_preflight(home)
 replacements={}
 for rel in THEME_FILES:
  f=root(home)/'themes'/theme/rel
  if not f.is_file(): raise RuntimeError('Missing installed AmethystOS theme file: '+str(f))
  replacements[home/'.config'/rel]=scaled_text(rel,f.read_text(),scale)
 # Store originals before committing. All tracked files are guaranteed unchanged.
 originals={p:p.read_bytes() for p in replacements}
 try:
  for path,contents in replacements.items():
   path.write_text(contents,encoding='utf-8')
  for entry in data['entries']:
   if entry['path'] in names: entry['sha256']=digest_path(home/entry['path'])
  state_tmp=state.with_suffix('.json.tmp')
  state_tmp.write_text(json.dumps(data,indent=2)+'\n')
  state_tmp.replace(state)
  pref.parent.mkdir(parents=True,exist_ok=True)
  pref.write_text(json.dumps({'theme':theme,'scale':scale},indent=2)+'\n')
 except Exception:
  for path,contents in originals.items(): path.write_bytes(contents)
  raise
 if gtk and home==Path.home().resolve():
  helper=root(home)/'desktop_prefs.py'
  if helper.exists():
   subprocess.run(['python3',str(helper),theme],check=False)
  change_text_scale(home, scale)
 if home==Path.home().resolve() and reload:
  wallpaper=home/'Pictures/wallpapers'/('AmethystDark.png' if theme=='dark' else 'AmethystLight.png')
  if wallpaper.exists() and (home/'.local/bin/set-wallpaper').exists():
   subprocess.run([str(home/'.local/bin/set-wallpaper'),'--file',str(wallpaper)],check=False)
  if shutil_which('pkill'):
   subprocess.run(['pkill','-x','-SIGUSR2','waybar'],check=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 print(f'AmethystOS {theme} · {scale}% text and bar size. Niri output DPI remains automatic.')

def shutil_which(cmd):
 import shutil
 return shutil.which(cmd)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('action',choices=['theme','scale','status','restore-scale'])
 ap.add_argument('value',nargs='?')
 ap.add_argument('--home',type=Path,default=Path.home())
 ap.add_argument('--no-gtk',action='store_true')
 ap.add_argument('--no-reload',action='store_true')
 opts=ap.parse_args()
 try:
  if opts.action=='restore-scale':
   restore_text_scale(opts.home);return
  if opts.action=='status':
   p=state_path(opts.home);print(p.read_text() if p.exists() else '{"theme":"dark","scale":100}');return
  if not opts.value: raise ValueError('A theme or scale is required')
  if opts.action=='theme':apply(opts.home,theme=opts.value,gtk=not opts.no_gtk,reload=not opts.no_reload)
  else:
   if opts.value=='auto':
    # Wayland compositor selects per-monitor scale; 100% means no additional text multiplier.
    size=100
   else: size=int(opts.value.rstrip('%'))
   apply(opts.home,scale=size,gtk=not opts.no_gtk,reload=not opts.no_reload)
 except (OSError,RuntimeError,ValueError) as exc:
  print('AmethystOS appearance: '+str(exc),file=sys.stderr);sys.exit(1)
if __name__=='__main__':main()
