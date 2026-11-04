#!/usr/bin/env python3
"""Apply reversible GTK appearance preferences using GNOME GSettings.

This affects GTK/libadwaita apps even in a Niri session. On restore we only
write a value back if it's still the one AmethystOS wrote; we never replace a
preference changed outside AmethystOS. No sudo or global configuration.
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path
import sys

SCHEMA = 'org.gnome.desktop.interface'
KEYS = {
    'color-scheme': {'dark': 'prefer-dark', 'light': 'prefer-light'},
    'gtk-theme': {'dark': 'adw-gtk3-dark', 'light': 'adw-gtk3'},
    'icon-theme': {'dark': 'Papirus-Dark', 'light': 'Papirus'},
}

def run(args):
    return subprocess.run(['gsettings', *args], capture_output=True, text=True, check=True).stdout.strip()

def get(key):
    # GSettings returns a quoted GVariant string; keep only the unquoted value.
    raw = run(['get', SCHEMA, key])
    return raw[1:-1] if len(raw) >= 2 and raw[0] == raw[-1] == "'" else raw

def set_value(key, value):
    run(['set', SCHEMA, key, value])

def apply(home: Path, mode: str, dry_run: bool = False):
    file = home / '.local/state/amethystos-base-v1/theme-prefs.json'
    current = {key: get(key) for key in KEYS}
    if file.exists():
        state = json.loads(file.read_text())
    else:
        state = {'original': current, 'written': {}}
    target = {key: values[mode] for key, values in KEYS.items()}
    if dry_run:
        print('Would set GTK appearance:', mode, '(previous values are backed up)')
        return
    for key, value in target.items():
        set_value(key, value)
    state['written'] = target
    state['mode'] = mode
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(state, indent=2)+'\n', encoding='utf-8')
    print('GTK and libadwaita appearance selected:', mode)

def restore(home: Path, dry_run: bool = False):
    file = home / '.local/state/amethystos-base-v1/theme-prefs.json'
    if not file.is_file():
        print('No managed GTK preferences to restore')
        return
    state = json.loads(file.read_text())
    for key, old in state['original'].items():
        if get(key) == state['written'].get(key):
            if not dry_run: set_value(key, old)
            print(('Would restore' if dry_run else 'Restored'), key)
        else:
            print('Preserving manually changed', key)
    if not dry_run: file.unlink()

if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('mode', choices=('dark','light','restore'))
    ap.add_argument('--home', type=Path, default=Path.home())
    ap.add_argument('--dry-run', action='store_true')
    opts=ap.parse_args()
    try:
        if opts.mode == 'restore': restore(opts.home, opts.dry_run)
        else: apply(opts.home, opts.mode, opts.dry_run)
    except (OSError, subprocess.SubprocessError) as exc:
        print('Appearance preferences were not changed: '+str(exc), file=sys.stderr)
        sys.exit(1)
