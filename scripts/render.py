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
    # Desktop entries make theme switching discoverable in either Fuzzel or Vicinae.
    # The quoted executable handles home directory names containing spaces.
    binary = str(HOME / '.local/bin/kuhl').replace('\\', '\\\\').replace('"', '\\"')
    launchers = {}
    for theme in ('day', 'dusk'):
        label = theme.title()
        content = (f"# KUHL-MANAGED\n[Desktop Entry]\nType=Application\n"
                   f"Name=Kuhl {label}\nComment=Switch to Kuhl {label} appearance\n"
                   f'Exec="{binary}" theme {theme}\n'
                   f"Icon=preferences-desktop-theme\nTerminal=false\nCategories=Settings;\n")
        launchers[HOME / '.local/share/applications' / f'kuhl-{theme}.desktop'] = content.encode()
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
  shadow {{ on; softness 26; spread 3; offset x=0 y=6; color "{p['shadow']}"; }}
}}
overview {{ backdrop-color "{p['bg']}"; }}
'''
    css = f'''/* KUHL-MANAGED — generated {theme} palette */
* {{ border: none; border-radius: 0; font-family: "Noto Sans", sans-serif; font-size: 12px; min-height: 0; }}
window#waybar {{ background: transparent; color: {p['fg']}; }}
.modules-left, .modules-center, .modules-right {{ margin: 0 5px; }}
#custom-kuhl, #workspaces, #window, #clock, #pulseaudio, #network, #battery, #tray, #custom-lock {{
  background: {p['surface']}; color: {p['fg']}; border: 1px solid {p['border']};
  border-radius: 14px; padding: 5px 14px; margin: 0 3px;
}}
#custom-kuhl {{ background: {p['accent']}; color: {p['bg']}; font-weight: 800; }}
#workspaces {{ padding: 3px 7px; }}
#workspaces button {{ padding: 2px 10px; margin: 0 2px; border-radius: 9px; color: {p['muted']}; }}
#workspaces button.active {{ background: {p['surface2']}; color: {p['accent']}; }}
#workspaces button:hover {{ background: {p['surface2']}; box-shadow: none; }}
#window {{ color: {p['muted']}; }}
#clock {{ color: {p['accent']}; font-weight: 700; }}
#tray {{ padding: 5px 10px; }}
#custom-lock {{ color: {p['muted']}; }}
#battery.warning, #battery.critical {{ color: #d9827c; }}
'''
    kitty = f'''# KUHL-MANAGED — generated {theme} palette
foreground {p['terminal_fg']}
background {p['terminal_bg']}
selection_foreground {p['terminal_bg']}
selection_background {p['accent']}
cursor {p['accent']}
cursor_text_color {p['terminal_bg']}
color0 {p['terminal_bg']}
color1 #d98b85
color2 {p['accent2']}
color3 {p['accent']}
color4 #93b5c3
color5 #c4a3bd
color6 #9dc8ba
color7 {p['terminal_fg']}
color8 {p['muted']}
color9 #e5a09b
color10 {p['accent2']}
color11 {p['accent']}
color12 #b7d3de
color13 #d3b8d1
color14 #afd8c9
color15 {p['fg']}
'''
    # Fedora-packaged Fuzzel is Kuhl's dependable, themed search fallback.
    rgba = lambda color: color.lstrip('#') + 'ff'
    fuzzel = f'''# KUHL-MANAGED — generated {theme} palette
[main]
font=JetBrains Mono:size=12
prompt=  Search >
icon-theme=Papirus
lines=8
width=48
horizontal-pad=22
vertical-pad=14
inner-pad=8
layer=overlay
[colors]
background={rgba(p['surface'])}
text={rgba(p['fg'])}
match={rgba(p['accent'])}
selection={rgba(p['surface2'])}
selection-text={rgba(p['fg'])}
selection-match={rgba(p['accent'])}
border={rgba(p['accent'])}
[border]
width=2
radius=15
selection-radius=9
'''
    mako = f'''# KUHL-MANAGED — generated {theme} palette
font=Noto Sans 11
background-color={p['surface']}
text-color={p['fg']}
border-color={p['accent']}
border-size=2
border-radius=12
padding=15
margin=12
default-timeout=5500
icons=1
'''
    # Optional Vicinae can reuse the same palette; files are not activated by default.
    vicinae = '\n'.join([
        f'# KUHL-MANAGED — {theme} Vicinae theme',
        '[meta]',
        'version = 1',
        f'name = "Kuhl {theme.title()}"',
        'description = "Warm Kuhl OS search palette"',
        f'variant = "{"dark" if theme == "dusk" else "light"}"',
        f'inherits = "vicinae-{"dark" if theme == "dusk" else "light"}"',
        '[colors.core]',
        f'background = "{p["surface"]}"',
        f'foreground = "{p["fg"]}"',
        f'secondary_background = "{p["bg"]}"',
        f'border = "{p["border"]}"',
        f'accent = "{p["accent"]}"',
        ''
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
