#!/usr/bin/env python3
"""Dependency-free, terminal-owned AmethystOS setup / removal prompts.

Never prints an untrusted shell command; the installer consumes only a JSON plan.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

GROUPS = [
    ('firefox', 'Firefox browser', 'Standard web browser'),
    ('chromium', 'Chromium browser', 'Alternative web browser'),
    ('essentials', 'Everyday apps', 'Calculator, text editor, archive manager and image viewer'),
    ('office', 'Office & mail', 'LibreOffice Writer and Thunderbird'),
    ('creative', 'Creative tools', 'GIMP, Inkscape and Krita'),
    ('dev', 'Development', 'Git, Micro, Neovim and Python tooling'),
    ('media', 'Music & video', 'Celluloid and Rhythmbox'),
    ('gaming', 'Gaming tools', 'Lutris, GameMode and MangoHud'),
    ('steam', 'Steam (Flatpak)', 'Flathub — third-party source, opt-in'),
    ('obs', 'OBS Studio (Flatpak)', 'Flathub — streaming and recording'),
    ('discord', 'Discord (Flatpak)', 'Flathub — voice and chat'),
    ('flatseal', 'Flatseal (Flatpak)', 'Flathub permission manager'),
    ('libreoffice', 'LibreOffice', 'Writer and Calc'),
    ('thunderbird', 'Thunderbird', 'Email'),
    ('gimp', 'GIMP', 'Image editor'),
    ('krita', 'Krita', 'Digital painting'),
    ('inkscape', 'Inkscape', 'Vector graphics'),
    ('kdenlive', 'Kdenlive', 'Video editor'),
    ('audacity', 'Audacity', 'Audio editor'),
    ('neovim', 'Neovim', 'Editor'),
    ('lutris', 'Lutris', 'Linux gaming launcher'),
]
DEFAULTS = {'firefox', 'essentials'}
PURPLE='\033[38;5;141m'; CYAN='\033[38;5;116m'; DIM='\033[2m'; RESET='\033[0m'; BOLD='\033[1m'


def create_plan(selected: list[str], replace: bool = False, appearance: bool = True) -> dict:
    valid = {key for key, _, _ in GROUPS}
    unknown = set(selected) - valid
    if unknown:
        raise ValueError('Unknown application groups: ' + ', '.join(sorted(unknown)))
    return {'groups': sorted(set(selected)), 'replace': bool(replace), 'apply_dark': bool(appearance), 'schema': 1}


def draw(writer, selected, replace, appearance, theme, page=0):
    writer.write('\033[2J\033[H')
    writer.write(f'{PURPLE}◆ AMETHYSTOS{RESET}  ·  FEDORA / NIRI  ·  SETUP\n')
    writer.write(f'{DIM}Select optional apps by number; Enter proceeds. Niri + Noctalia v4 are required.\n')
    writer.write(f'Steam, OBS, Discord, and Flatseal use Flathub only when chosen.{RESET}\n\n')
    page_size=10
    start=page*page_size
    writer.write(f'  Software page {page+1}/{(len(GROUPS)+page_size-1)//page_size} — use n/p to navigate\n')
    for n in range(start,min(start+page_size,len(GROUPS))):
        key, title, info = GROUPS[n]
        n=n+1
        mark = f'{CYAN}✓{RESET}' if key in selected else ' '
        writer.write(f'{n:>2}. [{mark}] {title:<25} {DIM}{info}{RESET}\n')
    base = len(GROUPS)
    writer.write(f'\n {base+1:>2}. [{"✓" if replace else " "}] Back up and replace existing configs\n')
    writer.write(f' {base+2:>2}. [{"✓" if appearance else " "}] Coordinate Noctalia dark/light appearance\n')
    writer.write(f' {base+3:>2}. [{"✓" if theme == "light" else " "}] Start with Amethyst Light (otherwise Dark)\n')
    writer.write(f'\n{DIM}n = next page, p = previous page, Enter = continue{RESET}\n')
    writer.write(f'{PURPLE}amethystos › {RESET}')
    writer.flush()


def interactive_plan() -> dict:
    selected = set(DEFAULTS)
    replace = False
    appearance = True
    theme = "dark"
    page=0
    # Never open a terminal in 'r+' mode: Python's text I/O can seek between
    # writes and reads, but terminal devices are not seekable. The installer
    # runs with stdin owned by curl, so open /dev/tty for each direction.
    with (open('/dev/tty', 'r', encoding='utf-8') as tty_in,
          open('/dev/tty', 'w', encoding='utf-8', buffering=1) as tty_out):
        while True:
            draw(tty_out, selected, replace, appearance, theme, page)
            answer = tty_in.readline()
            if not answer:
                raise RuntimeError('The setup terminal was closed')
            choice = answer.strip().lower()
            if choice in ('', 'i', 'install', 'done'):
                break
            if choice in ('q', 'quit', 'cancel'):
                raise KeyboardInterrupt
            if choice == 'n':
                page=min(page+1,(len(GROUPS)-1)//10)
                continue
            if choice == 'p':
                page=max(0,page-1)
                continue
            if choice == str(len(GROUPS) + 1):
                replace = not replace
            elif choice == str(len(GROUPS) + 2):
                appearance = not appearance
            elif choice == str(len(GROUPS) + 3):
                theme = 'light' if theme == 'dark' else 'dark'
            elif choice.isdigit() and 1 <= int(choice) <= len(GROUPS):
                key = GROUPS[int(choice) - 1][0]
                page=(int(choice)-1)//10
                if key in selected: selected.remove(key)
                else: selected.add(key)
        tty_out.write('\033[2J\033[H')
        tty_out.write(f'{BOLD}{PURPLE}◆ AMETHYSTOS{RESET}  Your choices\n\n')
        tty_out.write('  Optional apps: ' + (', '.join(sorted(selected)) or '(none)') + '\n')
        tty_out.write('  Existing configs: ' + ('back up and replace' if replace else 'preserve') + '\n')
        tty_out.write('  Appearance: ' + (theme if appearance else 'preserve preferences') + '\n')
        tty_out.write('  Fedora boot configuration: unchanged\n\n')
        tty_out.write('  Continue with Fedora package installation? [y/N] ')
        tty_out.flush()
        if tty_in.readline().strip().lower() not in ('y', 'yes'):
            raise KeyboardInterrupt
    plan=create_plan(list(selected), replace, appearance)
    plan.update(theme=theme)
    return plan


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--non-interactive', action='store_true')
    parser.add_argument('--replace', action='store_true')
    parser.add_argument('--no-theme', action='store_true')
    parser.add_argument('--theme', choices=('dark','light'), default='dark')
    parser.add_argument('--groups', default=None, help='comma-separated selection')
    args = parser.parse_args()
    try:
        if args.non_interactive or args.groups is not None:
            chosen = (args.groups.split(',') if args.groups else []) if args.groups is not None else sorted(DEFAULTS)
            plan = create_plan(chosen, args.replace, not args.no_theme)
            plan.update(theme=args.theme)
        else:
            plan = interactive_plan()
            if args.replace: plan['replace'] = True
            if args.no_theme: plan['apply_dark'] = False
    except (KeyboardInterrupt, EOFError):
        print('\nSetup canceled. Nothing has been installed.', file=sys.stderr)
        return 130
    except OSError as exc:
        print(f'Unable to use the interactive terminal: {exc}\n'
              'Run from a terminal window, or use --non-interactive.', file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
    return 0

if __name__ == '__main__':
    sys.exit(main())
