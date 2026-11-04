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
    ('gaming', 'Gaming tools', 'Lutris, GameMode and MangoHud (if available)'),
]
DEFAULTS = {'firefox', 'essentials'}
PURPLE='\033[38;5;141m'; CYAN='\033[38;5;116m'; DIM='\033[2m'; RESET='\033[0m'; BOLD='\033[1m'


def create_plan(selected: list[str], replace: bool = False, appearance: bool = True) -> dict:
    valid = {key for key, _, _ in GROUPS}
    unknown = set(selected) - valid
    if unknown:
        raise ValueError('Unknown application groups: ' + ', '.join(sorted(unknown)))
    return {'groups': sorted(set(selected)), 'replace': bool(replace), 'apply_dark': bool(appearance), 'schema': 1}


def draw(writer, selected, replace, appearance):
    writer.write('\033[2J\033[H')
    writer.write(f'{PURPLE}╭────────────────────────────────────────────────────────╮{RESET}\n')
    writer.write(f'{PURPLE}│{RESET} {BOLD}◆  AMETHYSTOS{RESET}    SETUP / FEDORA + NIRI                   {PURPLE}│{RESET}\n')
    writer.write(f'{PURPLE}╰────────────────────────────────────────────────────────╯{RESET}\n\n')
    writer.write(f'{DIM}Niri, its system controls and required fonts are included.{RESET}\n')
    writer.write('Choose optional software (a missing extra will be skipped).\n\n')
    for n, (key, title, info) in enumerate(GROUPS, 1):
        mark = f'{CYAN}✓{RESET}' if key in selected else ' '
        writer.write(f'  {n}. [{mark}] {title:<22} {DIM}{info}{RESET}\n')
    writer.write(f'\n  9. [{CYAN if replace else ""}{"✓" if replace else " "}{RESET}] Back up and replace existing dotfiles\n')
    writer.write(f' 10. [{CYAN if appearance else ""}{"✓" if appearance else " "}{RESET}] Coordinate GTK dark appearance (affects GNOME too)\n')
    writer.write('\n  Enter a number to toggle, or press Enter to install.\n')
    writer.write(f'  {DIM}No existing desktop configuration will be replaced silently.{RESET}\n\n')
    writer.write(f'{PURPLE}amethystos › {RESET}')
    writer.flush()


def interactive_plan() -> dict:
    selected = set(DEFAULTS)
    replace = False
    appearance = True
    # Never open a terminal in 'r+' mode: Python's text I/O can seek between
    # writes and reads, but terminal devices are not seekable. The installer
    # runs with stdin owned by curl, so open /dev/tty for each direction.
    with (open('/dev/tty', 'r', encoding='utf-8') as tty_in,
          open('/dev/tty', 'w', encoding='utf-8', buffering=1) as tty_out):
        while True:
            draw(tty_out, selected, replace, appearance)
            answer = tty_in.readline()
            if not answer:
                raise RuntimeError('The setup terminal was closed')
            choice = answer.strip().lower()
            if choice in ('', 'i', 'install', 'done'):
                break
            if choice in ('q', 'quit', 'cancel'):
                raise KeyboardInterrupt
            if choice == '9':
                replace = not replace
            elif choice == '10':
                appearance = not appearance
            elif choice.isdigit() and 1 <= int(choice) <= len(GROUPS):
                key = GROUPS[int(choice) - 1][0]
                if key in selected: selected.remove(key)
                else: selected.add(key)
        tty_out.write('\033[2J\033[H')
        tty_out.write(f'{BOLD}{PURPLE}◆ AMETHYSTOS{RESET}  Your choices\n\n')
        tty_out.write('  Optional apps: ' + (', '.join(sorted(selected)) or '(none)') + '\n')
        tty_out.write('  Existing configs: ' + ('back up and replace' if replace else 'preserve') + '\n')
        tty_out.write('  GTK appearance: ' + ('apply coordinated dark preference' if appearance else 'leave unchanged') + '\n\n')
        tty_out.write('  Continue with Fedora package installation? [y/N] ')
        tty_out.flush()
        if tty_in.readline().strip().lower() not in ('y', 'yes'):
            raise KeyboardInterrupt
    return create_plan(list(selected), replace, appearance)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--non-interactive', action='store_true')
    parser.add_argument('--replace', action='store_true')
    parser.add_argument('--no-theme', action='store_true')
    parser.add_argument('--groups', default=None, help='comma-separated selection')
    args = parser.parse_args()
    try:
        if args.non_interactive or args.groups is not None:
            chosen = (args.groups.split(',') if args.groups else []) if args.groups is not None else sorted(DEFAULTS)
            plan = create_plan(chosen, args.replace, not args.no_theme)
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
