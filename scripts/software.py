#!/usr/bin/env python3
"""Curated AmethystOS install/remove/update menu.

Package IDs are fixed in source; user input can only select known options.
DNF actions remain interactive so Fedora shows the transaction for approval.
Flathub is added only after the user deliberately selects a Flatpak app.
"""
from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# title, provider, Fedora package or Flatpak app ID
APPS = {
    'firefox':('Firefox','dnf','firefox'),
    'chromium':('Chromium','dnf','chromium'),
    'thunderbird':('Thunderbird','dnf','thunderbird'),
    'libreoffice':('LibreOffice','dnf','libreoffice-writer libreoffice-calc'),
    'gimp':('GIMP','dnf','gimp'),
    'krita':('Krita','dnf','krita'),
    'inkscape':('Inkscape','dnf','inkscape'),
    'kdenlive':('Kdenlive','dnf','kdenlive'),
    'audacity':('Audacity','dnf','audacity'),
    'git':('Git','dnf','git'),
    'neovim':('Neovim','dnf','neovim'),
    'btop':('Btop','dnf','btop'),
    'celluloid':('Celluloid','dnf','celluloid'),
    'lutris':('Lutris','dnf','lutris'),
    'steam':('Steam (Flathub)','flatpak','com.valvesoftware.Steam'),
    'obs':('OBS Studio (Flathub)','flatpak','com.obsproject.Studio'),
    'discord':('Discord (Flathub)','flatpak','com.discordapp.Discord'),
    'flatseal':('Flatseal (Flathub)','flatpak','com.github.tchx84.Flatseal'),
}

def choose(items:list[str],prompt:str)->str|None:
    if not shutil.which('fuzzel'):
        print('Fuzzel not available. Run --list and specify an app name in the terminal.',file=sys.stderr)
        return None
    result=subprocess.run(['fuzzel','--dmenu','--prompt',prompt,'--lines','14','--width','43'],input='\n'.join(items)+'\n',text=True,capture_output=True)
    return result.stdout.strip() if result.returncode==0 else None

def command(action:str,key:str):
    if key not in APPS:raise ValueError('Unknown application')
    _,provider,package=APPS[key]
    if provider=='dnf':return ['sudo','dnf',action,*package.split()]
    if action=='install':return ['flatpak','install','--user','flathub',package]
    return ['flatpak','uninstall','--user',package]

def execute(action:str,key:str):
    title,provider,_=APPS[key]
    print(f'\nAmethystOS · {action.title()} {title}\n')
    if provider=='flatpak':
        print('This is a third-party Flatpak from Flathub, not an official Fedora RPM.')
        if not shutil.which('flatpak'):
            print('Flatpak is not available; install it first using Fedora DNF.');return 1
        if action=='install':
            confirmation=input('Allow the Flathub user repository to be added if needed? [y/N] ').lower().strip()
            if confirmation not in ('y','yes'):return 0
            if subprocess.call(['flatpak','remote-add','--user','--if-not-exists','flathub','https://flathub.org/repo/flathub.flatpakrepo']):return 1
    print('Review the transaction details before confirming.\n')
    return subprocess.call(command(action,key))

def update():
    print('AmethystOS — update the underlying Fedora system')
    status=subprocess.call(['sudo','dnf','upgrade','--refresh'])
    if shutil.which('flatpak'):
        print('\nOptional user Flatpaks:')
        subprocess.call(['flatpak','update','--user'])
    return status

def pause():
    if sys.stdin.isatty():
        try:input('\nPress Enter to close...')
        except EOFError:pass

def main():
    ap=argparse.ArgumentParser(description='Curated AmethystOS software tools')
    ap.add_argument('action',choices=('install','remove','update','list','execute'))
    ap.add_argument('key',nargs='?')
    ap.add_argument('--operation',choices=('install','remove'),default='install')
    ap.add_argument('--dry-run',action='store_true')
    args=ap.parse_args()
    if args.action=='list':
        for k,(name,provider,_) in APPS.items():print(f'{k:14} {name:27} {provider}')
        return 0
    if args.action=='execute':
        if args.key not in APPS:return 2
        if args.dry_run:print(' '.join(command(args.operation,args.key)));return 0
        try:
            ret=execute(args.operation,args.key)
        finally:pause()
        return ret
    if args.action=='update':
        if args.dry_run:print('sudo dnf upgrade --refresh; flatpak update --user');return 0
        return spawn_terminal('update','')
    if args.key is not None and args.key not in APPS:
        print('Unknown application: '+args.key,file=sys.stderr);return 2
    key=args.key
    if not key:
        labels=[f'{name}  ·  {provider}' for _,(name,provider,_) in APPS.items()]
        selected=choose(labels,f'{args.action.title()} an app › ')
        if not selected:return 0
        try:index=labels.index(selected)
        except ValueError:return 2
        key=list(APPS)[index]
    if args.dry_run:print(' '.join(command(args.action,key)));return 0
    return spawn_terminal(args.action,key)

def spawn_terminal(action:str,key:str):
    args=[sys.executable,str(Path(__file__).resolve()),'execute',key,'--operation',action]
    if action=='update':
        # Separate internal action to avoid recursion when spawning terminal.
        args=[sys.executable,str(Path(__file__).resolve()),'run-update']
    if shutil.which('alacritty'):
        return subprocess.call(['alacritty','-e',*args])
    if shutil.which('kitty'):
        return subprocess.call(['kitty',*args])
    print('A terminal emulator is required for interactive package transactions.',file=sys.stderr)
    return 1

if __name__=='__main__':
    if len(sys.argv)>=2 and sys.argv[1]=='run-update':
        try:sys.exit(update())
        finally:pause()
    sys.exit(main())
