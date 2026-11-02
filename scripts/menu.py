#!/usr/bin/env python3
"""Kuhl's dependency-free Python curses installer chooser.

Output is a JSON file consumed by install.sh; user input never executes as shell.
"""
import argparse
import curses
import json
import os
import sys
import textwrap
from pathlib import Path


def rows(config):
    source = json.loads(Path(config).read_text(encoding='utf-8'))
    items = source['choices']
    ids = [item['id'] for item in items]
    assert len(ids) == len(set(ids)), 'Duplicate option IDs'
    return items


def menu(screen, items):
    curses.curs_set(0)
    screen.keypad(True)
    selected = {row['id'] for row in items if row.get('default') or row.get('required')}
    cursor, offset = 0, 0
    theme = 'dusk'
    while True:
        screen.erase()
        height, width = screen.getmaxyx()
        if height < 14 or width < 55:
            screen.addnstr(0, 0, 'Resize terminal to at least 55 x 14 (q to quit)', max(1, width-1))
            screen.refresh()
            if screen.getch() in (ord('q'), 27):
                return None
            continue
        def write(row, text, bold=False):
            screen.addnstr(row, 2, text, width - 4, curses.A_BOLD if bold else 0)
        write(0, '✳  KUHL OS  /  SETUP', True)
        write(1, 'Space = toggle   ↑↓ = move   T = theme   Enter = review   Q = exit')
        write(2, f'Theme: {theme.upper()}     Selected: {len(selected)} options (base items are required)')
        screen.hline(3, 2, curses.ACS_HLINE, width - 4)
        visible = max(1, height - 12)
        if cursor < offset:
            offset = cursor
        if cursor >= offset + visible:
            offset = cursor - visible + 1
        for screenrow, index in enumerate(range(offset, min(len(items), offset + visible)), 4):
            item = items[index]
            tick = 'x' if item['id'] in selected else ' '
            locked = ' • base' if item.get('required') else ''
            line = f"{'›' if cursor == index else ' '} [{tick}] {item['title']}{locked}"
            flags = curses.A_REVERSE if cursor == index else 0
            screen.addnstr(screenrow, 2, line, width-4, flags)
        current = items[cursor]
        screen.hline(height-7, 2, curses.ACS_HLINE, width - 4)
        write(height-6, f"{current['section']} · {current['title']}", True)
        desc = textwrap.wrap(current['description'], width - 4)
        for n, line in enumerate(desc[:3]):
            write(height-5+n, line)
        write(height-1, f'{cursor+1}/{len(items)}    Review with Enter  •  Nothing installs before approval')
        screen.refresh()
        key = screen.getch()
        if key in (curses.KEY_DOWN, ord('j')):
            cursor = min(len(items) - 1, cursor + 1)
        elif key in (curses.KEY_UP, ord('k')):
            cursor = max(0, cursor - 1)
        elif key in (ord(' '),):
            item = items[cursor]
            if not item.get('required'):
                if item['id'] in selected:
                    selected.remove(item['id'])
                else:
                    selected.add(item['id'])
        elif key in (ord('t'), ord('T')):
            theme = 'day' if theme == 'dusk' else 'dusk'
        elif key in (ord('q'), ord('Q'), 27):
            return None
        elif key in (10, 13, curses.KEY_ENTER):
            screen.erase()
            write(1, 'READY TO INSTALL KUHL OS', True)
            write(3, f'Theme: {theme.upper()}')
            write(4, f'Selected: {len(selected)} options including essential desktop tools')
            write(6, 'Fedora packages, Flathub apps and compatible GNOME extensions')
            write(7, 'may be installed. Your GNOME preferences are backed up first.')
            write(9, 'Continue?    Y = begin installation    N = return    Q = quit', True)
            screen.refresh()
            while True:
                answer = screen.getch()
                if answer in (ord('y'), ord('Y')):
                    return {'theme': theme, 'selected': sorted(selected)}
                if answer in (ord('q'), ord('Q'), 27):
                    return None
                if answer in (ord('n'), ord('N'), 10, 13):
                    break


def plain(items):
    selected = {row['id'] for row in items if row.get('default') or row.get('required')}
    print('\n✳ KUHL OS — simple text installer (fallback)')
    for i, item in enumerate(items, 1):
        status = 'x' if item['id'] in selected else ' '
        locked = ' (required)' if item.get('required') else ''
        print(f'{i:2}. [{status}] {item["title"]}{locked}\n    {item["description"]}')
    print('Type option numbers separated by commas to toggle, or press Enter to keep defaults.')
    answer = input('Options to toggle: ').strip()
    for part in answer.split(','):
        if not part.strip():
            continue
        pos = int(part) - 1
        item = items[pos]
        if not item.get('required'):
            if item['id'] in selected:
                selected.remove(item['id'])
            else:
                selected.add(item['id'])
    theme = input('Choose wallpaper theme: [dusk]/day: ').strip().lower() or 'dusk'
    if theme not in ('day', 'dusk'):
        raise ValueError('Unknown theme')
    answer = input(f'Install {len(selected)} options now? [y/N] ').strip().lower()
    return {'theme': theme, 'selected': sorted(selected)} if answer == 'y' else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--defaults', action='store_true')
    args = parser.parse_args()
    items = rows(args.config)
    if args.defaults:
        result = {'theme': 'dusk', 'selected': sorted(row['id'] for row in items if row.get('default') or row.get('required'))}
    else:
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise RuntimeError('Interactive setup needs a terminal. Use --defaults for unattended selection.')
        try:
            result = curses.wrapper(menu, items)
        except curses.error:
            result = plain(items)
    if result is None:
        return 2
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'Kuhl plan saved: {len(result["selected"])} choices, {result["theme"]} theme.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, IndexError, RuntimeError, OSError) as exc:
        print(f'Kuhl installer: {exc}', file=sys.stderr)
        sys.exit(1)
