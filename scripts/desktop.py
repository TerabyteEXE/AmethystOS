#!/usr/bin/env python3
"""Kuhl's desktop preferences, monitor scaling, and GTK integration.

No external Python libraries. Does not require root and never overwrites untracked files.
Niri output changes are staged and validated before writing the managed config.
"""
import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HOME = Path.home()
DATA = Path(os.environ.get('XDG_DATA_HOME', HOME / '.local/share')) / 'kuhl'
STATE = Path(os.environ.get('XDG_STATE_HOME', HOME / '.local/state')) / 'kuhl'
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', HOME / '.config'))
PREF_PATH = STATE / 'preferences.json'
SCALES = (0.75, 0.85, 1.0, 1.10, 1.25, 1.5, 1.75, 2.0)
DEFAULT = {
    'bar_scale': 1.0,
    'bar_position': 'top',
    'ui_scale': 1.0,
    'bar_modules': {'brand': True, 'audio': True, 'battery': True,
                    'language': False, 'clock': True, 'network': True,
                    'workspaces': False, 'tray': False, 'settings': True,
                    'close': True},
}
MODULES = {
    'brand': 'custom/kuhl', 'audio': 'pulseaudio', 'battery': 'battery',
    'language': 'niri/language', 'clock': 'clock', 'network': 'network',
    'workspaces': 'niri/workspaces', 'tray': 'tray', 'settings': 'custom/settings',
    'close': 'custom/close'
}


def preferences():
    p = copy.deepcopy(DEFAULT)
    if PREF_PATH.is_file():
        data = json.loads(PREF_PATH.read_text(encoding='utf8'))
        if isinstance(data, dict):
            for key in ('bar_scale', 'bar_position', 'ui_scale'):
                if key in data: p[key] = data[key]
            if isinstance(data.get('bar_modules'), dict):
                p['bar_modules'].update({k:bool(v) for k,v in data['bar_modules'].items() if k in MODULES})
    return p


def save_preferences(p):
    STATE.mkdir(parents=True, exist_ok=True)
    temp = PREF_PATH.with_suffix('.tmp')
    temp.write_text(json.dumps(p, indent=2, sort_keys=True)+'\n', encoding='utf8')
    os.chmod(temp, 0o600)
    temp.replace(PREF_PATH)


def scale_value(value, low=0.75, high=2.0):
    try:
        value = str(value).replace('%','').strip()
        n = float(value)
        if n > 10: n /= 100
        if not low <= n <= high: raise ValueError()
        return round(n, 2)
    except ValueError:
        raise SystemExit(f'Scale must be {low:.2f}–{high:.2f}, or {low*100:.0f}–{high*100:.0f}%.')


def bar_files(theme, p):
    """Build a KyleOS-shaped bar with readable fonts and independent scale controls."""
    pref = preferences()
    factor = pref['bar_scale']
    height = round(34 * factor)
    modules = pref['bar_modules']
    def enabled(*names): return [MODULES[x] for x in names if modules[x]]
    conf = {
        'layer': 'top', 'position': pref['bar_position'],
        'height': height, 'spacing': 0, 'margin-top': 0, 'margin-bottom': 0,
        'margin-left': 0, 'margin-right': 0,
        'modules-left': enabled('brand','audio','battery','language'),
        'modules-center': enabled('workspaces','clock'),
        'modules-right': enabled('network','tray','settings','close'),
        'clock': {'format': '{:%a %b %d  ·  %I:%M %p}', 'tooltip-format': '{:%A %B %d, %Y}',
                  'on-click': '$HOME/.local/bin/kuhl settings'},
        'network': {'format-wifi':'Wi-Fi {essid}', 'format-ethernet':'Ethernet',
                    'format-disconnected':'Offline', 'tooltip': True, 'on-click': '$HOME/.local/bin/kuhl settings network'},
        'battery': {'format':'Battery {capacity}%', 'format-charging':'Charging {capacity}%',
                    'states':{'warning':30,'critical':15}},
        'pulseaudio':{'format':'Vol {volume}%', 'format-muted':'Muted', 'scroll-step':5,
                      'on-click':'$HOME/.local/bin/kuhl settings audio', 'tooltip':True},
        'niri/language':{'format':'{}'},
        'niri/workspaces': {'format': '{index}'},
        'tray': {'spacing': 8},
        'custom/kuhl': {'format':'✳ kuhl', 'tooltip':'Open Kuhl Control Center',
                        'on-click':'$HOME/.local/bin/kuhl menu --ui'},
        'custom/settings': {'format':'Settings', 'tooltip':'Customize Kuhl OS',
                            'on-click':'$HOME/.local/bin/kuhl settings'},
        'custom/close': {'format':'×', 'tooltip':'Close focused window (Super+Q)',
                         'on-click':'niri msg action close-window'},
    }
    font = max(10, round(13 * factor))
    pad = max(5, round(12 * factor))
    # KyleOS dark geometric palette; full-width, flat strip. No giant 30px fonts.
    fg = p['fg'] if theme == 'day' else '#e0dccf'
    css = f'''/* KUHL-MANAGED — responsive KyleOS-inspired status strip; {theme}. */
* {{ border: none; border-radius: 0; min-height: 0;
    font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
    font-size: {font}px; }}
window#waybar {{ background: {p['bg']}; color: {fg}; border-bottom: 1px solid {p['border']}; }}
window#waybar.bottom {{ border-bottom: none; border-top: 1px solid {p['border']}; }}
#custom-kuhl, #pulseaudio, #battery, #language, #workspaces, #clock,
#network, #tray, #custom-settings, #custom-close {{ padding: 0 {pad}px; }}
#custom-kuhl {{ color: {p['accent']}; font-weight: 800; letter-spacing: 1px; }}
#clock {{ color: {p['accent']}; font-weight: bold; }}
#custom-settings {{ color: {p['accent2']}; }}
#custom-close {{ color: {p['accent']}; font-size: {max(15,round(19*factor))}px; }}
#custom-close:hover, #custom-settings:hover, #custom-kuhl:hover {{ background: {p['surface2']}; }}
#pulseaudio, #network, #battery, #language {{ color: {fg}; }}
#battery.warning {{ color: {p['accent']}; }}
#battery.critical {{ color: #e88787; }}
#workspaces button {{ padding: 0 {max(3,round(5*factor))}px; color: {fg}; }}
#workspaces button.active {{ color: {p['accent']}; background: {p['surface2']}; }}
#workspaces button:hover {{ background: {p['surface2']}; }}
#tray > .passive {{ -gtk-icon-effect: dim; }}
tooltip {{ background: {p['surface']}; color: {fg}; border: 1px solid {p['border']}; }}
'''
    return (json.dumps(conf, indent=2)+'\n').encode(), css.encode()


def gtk_call(action, key, value=None):
    args = ['gsettings', action, 'org.gnome.desktop.interface', key]
    if value is not None: args.append(value)
    try:
        cp = subprocess.run(args, text=True, capture_output=True, timeout=8, check=False)
        return cp.stdout.strip() if cp.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def sync_gtk(theme, ui_scale=None):
    """GTK applications and Flatpak portal colors; preserve previous user values."""
    themes = json.loads((DATA/'themes.json').read_text())
    if theme not in themes: raise SystemExit('Unknown theme')
    pref = preferences()
    if ui_scale is not None: pref['ui_scale'] = ui_scale
    dark = theme != 'day'
    wanted = {'color-scheme':"'prefer-dark'" if dark else "'prefer-light'",
              'gtk-theme':"'Adwaita-dark'" if dark else "'Adwaita'",
              'icon-theme':"'Papirus-Dark'" if dark else "'Papirus'",
              'text-scaling-factor':str(pref['ui_scale'])}
    marker = STATE/'gtk-restore.json'
    if marker.is_file(): record = json.loads(marker.read_text())
    else: record = {'original':{},'applied':{}}
    good = 0
    for key, value in wanted.items():
        existing = gtk_call('get',key)
        if existing is None: continue
        if key not in record['original']: record['original'][key] = existing
        if existing == value or gtk_call('set', key, value) is not None:
            # 'gsettings set' typically returns no stdout; check via get instead.
            pass
        current = gtk_call('get',key)
        if current == value:
            record['applied'][key] = value; good += 1
    if good:
        STATE.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps(record, indent=2)+'\n')
        os.chmod(marker,0o600)
    print(f'[kuhl] GTK / icon preferences synchronized ({good}/{len(wanted)} keys).')


def restore_gtk():
    marker = STATE/'gtk-restore.json'
    if not marker.exists(): return
    record = json.loads(marker.read_text())
    for key,value in record.get('original',{}).items():
        now = gtk_call('get',key)
        if now == record.get('applied',{}).get(key):
            gtk_call('set',key,value)
            print(f'[restored] GTK {key}')
        else: print(f'[kept] GTK {key} edited since Kuhl')
    marker.unlink()


def apply_pref(p):
    import render
    current = (STATE/'theme').read_text().strip() if (STATE/'theme').exists() else 'frontier'
    backup = preferences()
    # Refuse partial preferences deployment when managed appearance files were edited.
    m=render.manifest_load()
    paths=[CONFIG/'waybar/config.jsonc',CONFIG/'waybar/style.css',
           CONFIG/'rofi/kuhl.rasi',CONFIG/'alacritty/alacritty.toml',
           CONFIG/'kitty/colors.conf']
    for path in paths:
        rec=m['files'].get(str(path))
        if not rec or path.is_symlink() or not path.is_file() or render.digest(path.read_bytes())!=rec['sha256']:
            raise RuntimeError(f'{path} is not Kuhl-managed or was edited. No settings changed; use installer replace-with-backups if you want Kuhl to manage it.')
    save_preferences(p)
    try:
        changed = render.apply_theme(current, render.manifest_load())
        if not changed: raise RuntimeError('No managed theme files were updated. Upgrade using the installer replacement option.')
    except Exception:
        save_preferences(backup)
        raise
    if os.environ.get('NIRI_SOCKET'):
        # Reload just the current user's Waybar when in an active Niri session.
        subprocess.run(['pkill','-USR2','-u',str(os.getuid()),'-x','waybar'], stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)
    return 0


def output_names():
    if not shutil.which('niri'): return []
    proc = subprocess.run(['niri','msg','--json','outputs'], text=True,capture_output=True, check=False)
    if proc.returncode: return []
    try:
        parsed=json.loads(proc.stdout)
        return list(parsed) if isinstance(parsed,dict) else []
    except (ValueError,TypeError): return []


def display_scales():
    path = STATE/'display-scales.json'
    return json.loads(path.read_text()) if path.exists() else {}


def set_output(name=None, scale=None, clear=False):
    from render import digest, manifest_load, manifest_save, put
    path = CONFIG/'niri/output.kdl'
    original = display_scales()
    scales = dict(original)
    if clear and name is None: scales.clear()
    elif clear: scales.pop(name, None)
    else: scales[name]=scale
    text=['// KUHL-MANAGED — optional per-output scaling; Kuhl display reset restores automatic scaling.']
    for connector,num in sorted(scales.items()):
        # niri output names cannot contain newlines; encode as KDL-quoted JSON string.
        if not connector or any(x in connector for x in '\n\r'):
            raise SystemExit('Invalid monitor identifier')
        text.extend([f'output {json.dumps(connector)} {{',f'    scale {num}', '}'])
    content=('\n'.join(text)+'\n').encode()
    m=manifest_load()
    rec=m['files'].get(str(path))
    if path.is_symlink() or (path.exists() and (not rec or rec['sha256']!=digest(path.read_bytes()))):
        raise SystemExit('Niri output config was edited separately. Kuhl will not overwrite it; restore the managed version first.')
    config_dir=CONFIG/'niri'
    if shutil.which('niri') and (config_dir/'config.kdl').is_file():
        with tempfile.TemporaryDirectory(prefix='kuhl-output-') as td:
            folder=Path(td)
            for f in config_dir.glob('*.kdl'):
                if f.name != 'output.kdl': shutil.copy2(f,folder/f.name)
            (folder/'output.kdl').write_bytes(content)
            proc=subprocess.run(['niri','validate','--config',str(folder/'config.kdl')],capture_output=True,text=True,check=False)
            if proc.returncode:
                raise SystemExit('Rejected display setting. No config changed:\n'+proc.stderr.strip())
    if not put(path,content,m): raise SystemExit('Could not update monitor config.')
    manifest_save(m)
    STATE.mkdir(parents=True,exist_ok=True)
    (STATE/'display-scales.json').write_text(json.dumps(scales,indent=2)+'\n')
    print(f'[kuhl] Display configuration applied. Scales: {scales or "automatic"}')


def display_wizard():
    names = output_names()
    if not names:
        print('No running Niri outputs detected. Run: niri msg outputs, then kuhl display scale OUTPUT 1.25')
        return 1
    print('Connected displays:')
    for i,n in enumerate(names,1): print(f'  {i}. {n}')
    try:
        number=int(input('Display number (blank cancels): ').strip() or '0')
        if number not in range(1,len(names)+1): return 0
        print('100% / 125% / 150% / 175% / 200% (or a custom percentage 75–300)')
        value=input('Scale percentage (blank cancels): ').strip()
        if not value: return 0
        set_output(names[number-1],scale_value(value,0.75,3.0))
        print('If scaling is wrong, run: kuhl display reset')
        return 0
    except (EOFError, ValueError) as e:
        print('No changes made:',e)
        return 1


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='command',required=True)
    bar=sub.add_parser('bar');bar.add_argument('action',choices=['show','scale','position','module','reset']);bar.add_argument('arg',nargs='?');bar.add_argument('value',nargs='?')
    ui=sub.add_parser('ui');ui.add_argument('action',choices=['scale','show','reset']);ui.add_argument('value',nargs='?')
    display=sub.add_parser('display');display.add_argument('action',choices=['outputs','scale','reset','wizard']);display.add_argument('name',nargs='?');display.add_argument('value',nargs='?')
    appearance=sub.add_parser('appearance');appearance.add_argument('action',choices=['apply','restore']);appearance.add_argument('theme',nargs='?')
    a=ap.parse_args()
    if a.command=='appearance':
        if a.action=='restore': restore_gtk();return 0
        theme=a.theme or ((STATE/'theme').read_text().strip() if (STATE/'theme').exists() else 'frontier')
        sync_gtk(theme);return 0
    if a.command=='display':
        if a.action=='outputs':
            if shutil.which('niri'): return subprocess.call(['niri','msg','outputs'])
            print('Niri executable not installed.');return 1
        if a.action=='wizard':return display_wizard()
        if a.action=='reset': set_output(a.name,clear=True);return 0
        if not a.name or a.value is None: ap.error('Usage: kuhl display scale OUTPUT 1.25')
        set_output(a.name,scale_value(a.value,0.75,3.0));return 0
    p=preferences()
    if a.command=='bar':
        if a.action=='show':
            print(json.dumps({k:p[k] for k in ('bar_scale','bar_position','bar_modules')},indent=2));return 0
        if a.action=='scale':
            if a.arg is None:ap.error('bar scale requires a percentage such as 125')
            p['bar_scale']=scale_value(a.arg)
        elif a.action=='position':
            if a.arg not in ('top','bottom'): ap.error('bar position top|bottom')
            p['bar_position']=a.arg
        elif a.action=='module':
            if a.arg not in MODULES or a.value not in ('on','off'): ap.error('bar module MODULE on|off')
            p['bar_modules'][a.arg]=(a.value=='on')
        else:
            p['bar_scale']=1.;p['bar_position']='top';p['bar_modules']=copy.deepcopy(DEFAULT['bar_modules'])
        apply_pref(p);print('[kuhl] Bar settings updated.');return 0
    if a.action=='show':print(f'UI scale: {p["ui_scale"]*100:.0f}%');return 0
    if a.action=='scale':
        if a.value is None:ap.error('ui scale requires percentage, e.g. 125')
        p['ui_scale']=scale_value(a.value,0.75,2.0)
    else:p['ui_scale']=1.0
    apply_pref(p)
    if os.environ.get('NIRI_SOCKET'):sync_gtk((STATE/'theme').read_text().strip())
    print('[kuhl] UI font scaling updated. New terminal windows reflect the font size.');return 0

if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,RuntimeError,KeyError,ValueError) as exc:
        print(f'[kuhl] {exc}',file=sys.stderr);sys.exit(1)
