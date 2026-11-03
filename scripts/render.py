#!/usr/bin/env python3
"""Kuhl's safe, standard-library-only Fedora + Niri configuration deployment.

Do not clobber pre-existing files, preserve manually-edited managed files,
back up explicit replacements, and restore originals on uninstall.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HOME = Path.home()
DATA = Path(os.environ.get('XDG_DATA_HOME', HOME / '.local/share')) / 'kuhl'
STATE = Path(os.environ.get('XDG_STATE_HOME', HOME / '.local/state')) / 'kuhl'
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', HOME / '.config'))
MANIFEST = STATE / 'managed.json'


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def manifest_load():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding='utf-8'))
    return {'version': 1, 'files': {}}


def manifest_save(m):
    STATE.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.managed-', dir=STATE)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(m, f, indent=2, sort_keys=True)
            f.write('\n')
        os.chmod(temp, 0o600)
        os.replace(temp, MANIFEST)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def put(path: Path, content: bytes, m: dict, *, replace=False) -> bool:
    """Only rewrite unchanged Kuhl-owned files; never silently replace user work."""
    key = str(path)
    record = m['files'].get(key)
    if path.is_symlink():
        print(f'[skip] Symlink not followed: {path}')
        return False
    if path.exists():
        old_hash = digest(path.read_bytes())
        known = record is not None and record['sha256'] == old_hash
        if not known:
            if not replace:
                print(f'[skip] Existing or edited config kept: {path}')
                return False
            # An explicit replacement always saves the original (and the path).
            backups = STATE / 'backups'
            backups.mkdir(parents=True, exist_ok=True)
            if record and record.get('backup'):
                # A previously backed-up file must keep its original backup.
                backup = Path(record['backup'])
            else:
                backup = backups / (digest(key.encode()) + '.bak')
                if not backup.exists():
                    shutil.copy2(path, backup)
            # Even when replaced manually later, we keep the original in the manifest.
            backup_path = str(backup)
        else:
            backup_path = record.get('backup')
    else:
        backup_path = record.get('backup') if record else None
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.kuhl-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as file:
            file.write(content)
        os.chmod(temp, 0o644)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    m['files'][key] = {'sha256': digest(content), 'backup': backup_path}
    print(f'[ok] {path}')
    return True


def template_files(source: Path):
    '''Deploy upstream-derived, Fedora-compatible config, with exact tracked backups.'''
    binary = str(HOME / '.local/bin/kuhl').replace('\\', '\\\\').replace('"', '\\"')
    items = [
        ('day','Kuhl Day','Light palette','theme day','preferences-desktop-theme'),
        ('dusk','Kuhl Dusk','Warm charcoal palette','theme dusk','preferences-desktop-theme'),
        ('sevens','Kuhl Sevens','Source-inspired slate and blue','theme sevens','preferences-desktop-theme'),
        ('control','Kuhl Control Center','Kuhl desktop controls','menu --ui','preferences-system'),
        ('keys','Kuhl Keyboard Guide','Search Niri shortcuts','keys --ui','input-keyboard'),
        ('settings','Kuhl Settings','Desktop settings','settings','preferences-system'),
    ]
    files = {}
    for name,title,comment,args,icon in items:
        body = ('# KUHL-MANAGED\n[Desktop Entry]\nType=Application\n'
                f'Name={title}\nComment={comment}\nExec="{binary}" {args}\n'
                f'Icon={icon}\nTerminal=false\nCategories=Settings;\n')
        files[HOME/'.local/share/applications'/f'kuhl-{name}.desktop']=body.encode()
    for name in ('config.kdl','binds.kdl','output.kdl'):
        files[CONFIG/'niri'/name]=(source/'niri'/name).read_bytes()
    for folder,names in {
        'kitty':('kitty.conf',),
        'alacritty':('alacritty.toml',),
        'rofi':('config.rasi','kuhl.rasi','gallery.rasi','power.rasi'),
        'waybar':('upstream-style.css',),
    }.items():
        for name in names:
            files[CONFIG/folder/name]=(source/folder/name).read_bytes()
    return files


def theme_files(theme: str):
    '''Render live palette and Waybar controls without modifying upstream snapshots.'''
    from desktop import preferences, bar_files
    palettes=json.loads((DATA/'themes.json').read_text(encoding='utf-8'))
    if theme not in palettes: raise SystemExit('Unknown theme; try kuhl theme list')
    p=palettes[theme]
    scale=preferences()['ui_scale']
    # Use the original borderless/source layout; palette applies only a small overlay.
    niri=f'''// KUHL-MANAGED — theme {theme}
layout {{
    focus-ring {{
        width 0
        active-color "{p['accent']}"
    }}
}}
overview {{
    backdrop-color "{p['bg']}"
}}
'''
    kitty=f'''# KUHL-MANAGED colors; source Kitty configuration retained.
foreground {p['fg']}
background {p['terminal_bg']}
selection_foreground {p['bg']}
selection_background {p['accent']}
cursor {p['accent']}
color0 {p['bg']}
color1 #f38ba8
color2 {p['accent2']}
color3 #f9e2af
color4 {p['accent']}
color5 #cba6f7
color6 #94e2d5
color7 {p['fg']}
'''
    alacritty=f'''# KUHL-MANAGED — dynamic Alacritty palette
[colors.primary]
background = "{p['terminal_bg']}"
foreground = "{p['terminal_fg']}"
[colors.normal]
black = "{p['bg']}"
red = "#f38ba8"
green = "{p['accent2']}"
yellow = "#f9e2af"
blue = "{p['accent']}"
magenta = "#cba6f7"
cyan = "#94e2d5"
white = "{p['fg']}"
'''
    mako=f'''# KUHL-MANAGED — compact notifications
font=JetBrains Mono {round(11*scale)}
background-color={p['surface']}
text-color={p['fg']}
border-color={p['accent']}
border-size=2
border-radius=6
padding=12
margin=8
width=340
height=120
default-timeout=5500
'''
    fuzzel=f'''[main]
font=JetBrains Mono:size={round(13*scale)}
prompt=Kuhl ❯
lines=9
width=48
[colors]
background={p['bg'].lstrip('#')}ee
text={p['fg'].lstrip('#')}ff
selection={p['surface2'].lstrip('#')}ff
selection-text={p['fg'].lstrip('#')}ff
border={p['accent'].lstrip('#')}ff
'''
    rofi=f'''/* KUHL-MANAGED — colors for the MIT source launcher configuration */
* {{
    background: {p['bg']};
    foreground: {p['fg']};
    accent: {p['accent']};
    surface: {p['surface2']};
}}
'''
    # Synchronize fonts with the independently adjustable Kuhl UI scaling setting.
    kitty_config=(DATA/'templates/kitty/kitty.conf').read_text(encoding='utf-8')
    kitty_config=__import__('re').sub(r'(?m)^font_size\s+\S+',
                          f'font_size {round(12*scale,1)}',kitty_config)
    alacritty_config=(DATA/'templates/alacritty/alacritty.toml').read_text(encoding='utf-8')
    alacritty_config=__import__('re').sub(r'(?m)^size\s*=\s*[0-9.]+',
                          f'size = {round(12*scale,1)}',alacritty_config)
    rofi_config=(DATA/'templates/rofi/kuhl.rasi').read_text(encoding='utf-8')
    rofi_config=f'* {{ font: "JetBrains Mono {max(11,round(13*scale))}"; }}\n'+rofi_config
    waybar_config,waybar_css=bar_files(theme,p)
    colors='''/* KUHL-MANAGED — source Waybar CSS variables. */\n'''
    color_map={'background':p['bg'],'foreground':p['fg'],'cursor':p['accent'],
        'color0':p['surface2'],'color1':'#f38ba8','color2':p['accent2'],
        'color3':'#f9e2af','color4':p['accent'],'color5':'#cba6f7',
        'color6':'#94e2d5','color7':p['fg'],'color8':p['muted']}
    colors+=''.join(f'@define-color {k} {v};\n' for k,v in color_map.items())
    colors+=''.join(f'@define-color color{i} {color_map["color"+str(i-8)]};\n' for i in range(9,16))
    dark = theme != 'day'
    gtk=(f'[Settings]\ngtk-theme-name={"Adwaita-dark" if dark else "Adwaita"}\n'
         f'gtk-icon-theme-name={"Papirus-Dark" if dark else "Papirus"}\n'
         f'gtk-application-prefer-dark-theme={int(dark)}\n')
    vicinae='\n'.join(['# KUHL-MANAGED', '[meta]','version = 1',f'name = "Kuhl {theme}"',
        'description = "Kuhl OS color palette"',f'variant = "{"dark" if dark else "light"}"',
        f'inherits = "vicinae-{"dark" if dark else "light"}"',''])
    return {
        CONFIG/'niri/kuhl-theme.kdl':niri.encode(),
        CONFIG/'kitty/colors.conf':kitty.encode(),
        CONFIG/'kitty/kitty.conf':kitty_config.encode(),
        CONFIG/'alacritty/colors.toml':alacritty.encode(),
        CONFIG/'alacritty/alacritty.toml':alacritty_config.encode(),
        CONFIG/'mako/config':mako.encode(),
        CONFIG/'fuzzel/fuzzel.ini':fuzzel.encode(),
        CONFIG/'rofi/color.rasi':rofi.encode(),
        CONFIG/'rofi/kuhl.rasi':rofi_config.encode(),
        CONFIG/'waybar/config.jsonc':waybar_config,
        CONFIG/'waybar/style.css':waybar_css,
        CONFIG/'waybar/colors.css':colors.encode(),
        CONFIG/'gtk-3.0/settings.ini':gtk.encode(),
        CONFIG/'gtk-4.0/settings.ini':gtk.encode(),
        DATA.parent/'vicinae/themes'/f'kuhl-{theme}.toml':vicinae.encode(),
    }

def apply_theme(theme, m, replace=False):
    ok = 0
    for target, content in theme_files(theme).items():
        ok += put(target, content, m, replace=replace)
    if ok:
        STATE.mkdir(parents=True, exist_ok=True)
        (STATE / 'theme').write_text(theme + '\n', encoding='utf-8')
    manifest_save(m)
    return ok


def uninstall():
    m = manifest_load()
    for path, record in list(m['files'].items()):
        p = Path(path)
        if p.is_symlink():
            print(f'[kept] Symlink changed: {p}')
            continue
        if p.exists() and digest(p.read_bytes()) != record['sha256']:
            print(f'[kept] File edited by user: {p}')
            continue
        backup = record.get('backup')
        if backup and Path(backup).is_file():
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup, p)
            print(f'[restored] {p}')
        elif p.exists():
            p.unlink()
            print(f'[removed] {p}')
        del m['files'][path]
    manifest_save(m)
    if m['files']:
        print('[kuhl] Some configs were kept. Their manifest entries remain for review.')
    return len(m['files'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'theme', 'uninstall', 'status'])
    parser.add_argument('--theme', choices=['sevens', 'day', 'dusk'], default='sevens')
    parser.add_argument('--source', type=Path, default=DATA / 'templates')
    parser.add_argument('--replace-configs', action='store_true', help='backup and replace existing/edited files')
    args = parser.parse_args()
    if args.action == 'uninstall':
        return 1 if uninstall() else 0
    if args.action == 'status':
        m = manifest_load()
        for path, r in m['files'].items():
            p = Path(path)
            status = 'OK' if p.is_file() and not p.is_symlink() and digest(p.read_bytes()) == r['sha256'] else 'CHANGED/MISSING'
            print(f'{status:16} {path}')
        return 0
    m = manifest_load()
    if args.action == 'install':
        for p, content in template_files(args.source).items():
            put(p, content, m, replace=args.replace_configs)
        manifest_save(m)
    apply_theme(args.theme, m, replace=args.replace_configs)
    return 0


if __name__ == '__main__':
    sys.exit(main())
