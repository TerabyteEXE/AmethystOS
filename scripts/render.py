#!/usr/bin/env python3
"""Kuhl's safe, standard-library-only Niri configuration deployment.

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
    """Original desktop templates plus launcher entries for discoverable Kuhl tools."""
    binary = str(HOME / '.local/bin/kuhl').replace('\\', '\\\\').replace('"', '\\"')
    launchers = {}
    for name, title, comment, arguments, icon in (
        ('day', 'Kuhl Day', 'Use the Kuhl Day palette', 'theme day', 'preferences-desktop-theme'),
        ('dusk', 'Kuhl Dusk', 'Use the Kuhl Dusk palette', 'theme dusk', 'preferences-desktop-theme'),
        ('control', 'Kuhl Control Center', 'Themes, wallpaper, system and settings', 'menu --ui', 'preferences-system'),
        ('keys', 'Kuhl Keyboard Guide', 'Search all Kuhl shortcuts', 'keys --ui', 'input-keyboard'),
    ):
        content = (f'# KUHL-MANAGED\n[Desktop Entry]\nType=Application\n'
                   f'Name={title}\nComment={comment}\n'
                   f'Exec="{binary}" {arguments}\n'
                   f'Icon={icon}\nTerminal=false\nCategories=Settings;\n')
        launchers[HOME / '.local/share/applications' / f'kuhl-{name}.desktop'] = content.encode()
    return {
        **launchers,
        CONFIG / 'niri/config.kdl': (source / 'niri/config.kdl').read_bytes(),
        CONFIG / 'waybar/config.jsonc': (source / 'waybar/config.jsonc').read_bytes(),
        CONFIG / 'kitty/kitty.conf': (source / 'kitty/kitty.conf').read_bytes(),
    }


def theme_files(theme: str):
    palettes = json.loads((DATA / 'themes.json').read_text(encoding='utf-8'))
    if theme not in palettes:
        raise SystemExit('Theme must be day or dusk')
    p = palettes[theme]
    niri = f'''// KUHL-MANAGED — automatically generated Kuhl {theme} palette
layout {{
  focus-ring {{ active-color "{p['accent']}"; inactive-color "{p['border']}"; }}
  shadow {{ on; softness 20; spread 2; offset x=0 y=5; color "{p['shadow']}"; }}
}}
overview {{ backdrop-color "{p['bg']}"; }}
'''
    css = f'''/* KUHL-MANAGED — original Kuhl Studio {theme} palette */
* {{ border: 0; border-radius: 0; font-family: "JetBrains Mono", monospace; font-size: 11px; min-height: 0; }}
window#waybar {{
  background: {p['surface']}; color: {p['fg']};
  border: 1px solid {p['border']}; border-radius: 22px;
}}
.modules-center {{ margin: 0 7px; }}
#custom-kuhl, #workspaces, #clock, #custom-theme, #pulseaudio,
#network, #battery, #tray, #custom-keys, #custom-power {{
  color: {p['muted']}; padding: 0 6px; margin: 0 1px;
}}
#custom-kuhl {{ font-size: 18px; font-weight: 900; padding: 0 8px; color: {p['accent']}; }}
#clock {{ color: {p['fg']}; font-weight: 700; padding: 0 8px; }}
#workspaces {{ padding: 0 0 0 3px; }}
#workspaces button {{ padding: 0 5px; margin: 4px 1px; color: {p['muted']}; border-radius: 8px; }}
#workspaces button.active {{ background: {p['surface2']}; color: {p['accent']}; font-weight: 800; }}
#workspaces button:hover {{ background: {p['surface2']}; color: {p['fg']}; box-shadow: none; }}
#custom-theme {{ color: {p['accent']}; font-size: 17px; }}
#tray {{ padding: 0 5px; }}
#custom-keys {{ color: {p['accent']}; font-weight: 700; }}
#custom-power {{ color: #e5a69e; padding-right: 12px; font-size: 15px; }}
#battery.warning {{ color: {p['accent']}; }}
#battery.critical {{ color: #e5a69e; }}
tooltip {{ background-color: {p['surface']}; color: {p['fg']}; border: 1px solid {p['border']}; border-radius: 10px; }}
'''
    kitty = f'''# KUHL-MANAGED — generated {theme} terminal palette
foreground {p['terminal_fg']}
background {p['terminal_bg']}
selection_foreground {p['terminal_bg']}
selection_background {p['accent']}
cursor {p['accent']}
cursor_text_color {p['terminal_bg']}
color0 {p['terminal_bg']}
color1 #c77e7e
color2 {p['accent2']}
color3 {p['accent']}
color4 #9aaebd
color5 #c2a7b8
color6 #a0b8b4
color7 {p['terminal_fg']}
color8 {p['muted']}
color9 #e5a09b
color10 {p['accent2']}
color11 {p['accent']}
color12 #c2d6df
color13 #d3b8d1
color14 #afd8c9
color15 {p['fg']}
'''
    rgba = lambda color: color.lstrip('#') + 'ff'
    fuzzel = f'''# KUHL-MANAGED — generated {theme} launcher palette
[main]
font=JetBrains Mono:size=12
prompt=  Search  ›
icon-theme=Papirus
lines=8
width=48
horizontal-pad=22
vertical-pad=16
inner-pad=9
layer=overlay
[colors]
background={rgba(p['surface'])}
text={rgba(p['fg'])}
match={rgba(p['accent'])}
selection={rgba(p['surface2'])}
selection-text={rgba(p['fg'])}
selection-match={rgba(p['accent'])}
border={rgba(p['border'])}
[border]
width=1
radius=16
selection-radius=8
'''
    mako = f'''# KUHL-MANAGED — generated {theme} notification palette
font=JetBrains Mono 10
background-color={p['surface']}
text-color={p['fg']}
border-color={p['border']}
border-size=1
border-radius=13
padding=14
margin=12
default-timeout=5000
icons=1
'''
    # Optional Vicinae stays opt-in. Kuhl does not configure its telemetry policy.
    vicinae = '\n'.join([
        f'# KUHL-MANAGED — {theme} Vicinae theme', '[meta]', 'version = 1',
        f'name = "Kuhl {theme.title()}"', 'description = "Kuhl Studio palette"',
        f'variant = "{"dark" if theme == "dusk" else "light"}"',
        f'inherits = "vicinae-{"dark" if theme == "dusk" else "light"}"',
        '[colors.core]',
        f'background = "{p["surface"]}"', f'foreground = "{p["fg"]}"',
        f'secondary_background = "{p["bg"]}"',
        f'border = "{p["border"]}"', f'accent = "{p["accent"]}"', ''
    ])
    return {
        CONFIG / 'niri/kuhl-theme.kdl': niri.encode(),
        CONFIG / 'waybar/style.css': css.encode(),
        CONFIG / 'kitty/colors.conf': kitty.encode(),
        CONFIG / 'mako/config': mako.encode(),
        CONFIG / 'fuzzel/fuzzel.ini': fuzzel.encode(),
        DATA.parent / 'vicinae/themes' / f'kuhl-{theme}.toml': vicinae.encode(),
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
    parser.add_argument('--theme', choices=['day', 'dusk'], default='dusk')
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
