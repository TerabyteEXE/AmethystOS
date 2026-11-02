#!/usr/bin/env python3
"""Capture a local Kuhl/GNOME setup for review before distro packaging.

Avoid collecting secrets, GNOME accounts, cookies, documents, history or user paths.
Extensions' own preferences are NOT included by default because some may
contain API tokens, remote URLs, personal file paths or other private values.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
from pathlib import Path

BASE_EXTENSIONS = {
    'user-theme@gnome-shell-extensions.gcampax.github.com',
    'background-logo@fedorahosted.org',
    'arcmenu@arcmenu.com',
    'dash-to-dock@micxgx.gmail.com',
    'just-perfection-desktop@just-perfection',
    'appindicatorsupport@rgcjonas.gmail.com',
    'tiling-assistant@leleat-on-github',
    'caffeine@patapon.info',
    'blur-my-shell@aunetx',
    'rounded-window-corners@fxgn',
    'spotlight@nin',
}
CORE_APPS = {'com.mattjakeman.ExtensionManager'}
KEYS = [
    ('org.gnome.desktop.interface', 'color-scheme'),
    ('org.gnome.desktop.interface', 'gtk-theme'),
    ('org.gnome.desktop.interface', 'icon-theme'),
    ('org.gnome.desktop.interface', 'cursor-theme'),
    ('org.gnome.desktop.interface', 'accent-color'),
    ('org.gnome.desktop.interface', 'font-name'),
    ('org.gnome.desktop.interface', 'monospace-font-name'),
    ('org.gnome.desktop.wm.preferences', 'button-layout'),
    ('org.gnome.desktop.wm.keybindings', 'switch-input-source'),
    ('org.gnome.shell.extensions.user-theme', 'name'),
]


def command(*args: str) -> str:
    try:
        output = subprocess.run(args, capture_output=True, check=False,
                                text=True, timeout=12)
        return output.stdout.strip() if output.returncode == 0 else ''
    except (OSError, subprocess.TimeoutExpired):
        return ''


def lines(*args: str) -> list[str]:
    return [s.strip() for s in command(*args).splitlines() if s.strip()]


def main() -> None:
    ap = argparse.ArgumentParser(description='Capture your working GNOME setup without personal files.')
    ap.add_argument('--output', default=str(Path.home() / 'kuhl-capture.json'),
                    help='Where to write the reviewable JSON (default: ~/kuhl-capture.json)')
    ap.add_argument('--with-extension-prefs', action='store_true',
                    help='Additionally export extension settings to a PRIVATE .dconf text file; review before sharing')
    ap.add_argument('--overwrite', action='store_true', help='Replace prior capture file')
    args = ap.parse_args()
    out = Path(args.output).expanduser().resolve()
    if out.exists() and not args.overwrite:
        ap.error(f'{out} already exists; choose --output or use --overwrite')
    out.parent.mkdir(parents=True, exist_ok=True)
    enabled = sorted(set(lines('gnome-extensions', 'list', '--enabled')))
    installed = sorted(set(lines('gnome-extensions', 'list')))
    app_ids = sorted(set(lines('flatpak', 'list', '--app', '--columns=application')))
    # dnf5 returns explicitly installed RPM names on Fedora Workstation.
    # Optional inventory; no package changes are made.
    rpm_names = sorted(set(lines('dnf', 'repoquery', '--userinstalled', '--queryformat', '%{name}')))
    settings = {}
    for schema, key in KEYS:
        val = command('gsettings', 'get', schema, key)
        if val:
            settings[f'{schema} {key}'] = val
    data = {
        'format': 'kuhl-capture-v1',
        'captured_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
        'gnome_version': command('gnome-shell', '--version'),
        'os_name': next((line.split('=',1)[1].strip().strip('"') for line in
                         Path('/etc/os-release').read_text().splitlines() if line.startswith('PRETTY_NAME=')), 'unknown')
                        if Path('/etc/os-release').is_file() else 'unknown',
        'enabled_extensions': enabled,
        'all_installed_extensions': installed,
        'extra_enabled_extensions': sorted(set(enabled) - BASE_EXTENSIONS),
        'flatpak_app_ids': app_ids,
        'extra_flatpak_app_ids': sorted(set(app_ids) - CORE_APPS),
        'explicitly_installed_rpm_names': rpm_names,
        'selected_public_desktop_settings': settings,
        'note': 'Review before sharing. Exact extension-specific preferences require a separate manual export.',
    }
    if not enabled and not installed:
        print('Warning: no extensions found; run from your logged-in GNOME desktop session.')
    # Prevent leaking content through a permissive umask or public directory.
    descriptor = os.open(out, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write('\n')
    print(f'Wrote {out}')
    print(f'Enabled extensions: {len(enabled)} ({len(data["extra_enabled_extensions"])} outside Kuhl defaults)')
    print(f'Flatpak apps: {len(app_ids)}; explicitly installed RPM packages: {len(rpm_names)}')
    if data['extra_enabled_extensions']:
        print('Extra enabled GNOME extensions:')
        for item in data['extra_enabled_extensions']:
            print(f'  {item}')
    if args.with_extension_prefs:
        if not command('dconf', 'dump', '/org/gnome/shell/extensions/'):
            print('No dconf extension settings found (or dconf not installed).')
        else:
            prefs_path = out.with_suffix('.extensions.dconf')
            if prefs_path.exists() and not args.overwrite:
                ap.error(f'{prefs_path} already exists. Use --overwrite or a different --output.')
            dconf = command('dconf', 'dump', '/org/gnome/shell/extensions/')
            descriptor = os.open(prefs_path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
            with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
                handle.write(dconf + '\n')
            print(f'PRIVATE extension preferences: {prefs_path}')
            print('CAUTION: May contain usernames, tokens, URLs and personal paths. Inspect before sharing.')


if __name__ == '__main__':
    main()
