#!/usr/bin/env python3
"""Kuhl OS's dependency-free, keyboard-driven terminal installer selector.

This produces a reviewed JSON choice plan, never shell code. Installation is
handled by install.sh only after the user approves this screen.
"""
import argparse
import curses
import json
import sys
import textwrap
from pathlib import Path


def rows(config):
    items = json.loads(Path(config).read_text(encoding='utf-8'))['choices']
    ids = [item['id'] for item in items]
    if len(ids) != len(set(ids)) or not all(i.get('description') for i in items):
        raise ValueError('Invalid or duplicate option IDs')
    return items


def menu(screen, items):
    curses.curs_set(0)
    screen.keypad(True)
    if curses.has_colors():
        curses.start_color()
        try:
            curses.use_default_colors()
        except curses.error:
            pass
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(4, curses.COLOR_GREEN, -1)
    accent = curses.color_pair(1) if curses.has_colors() else curses.A_BOLD
    muted = curses.color_pair(2) if curses.has_colors() else 0
    active = curses.color_pair(3) | curses.A_BOLD if curses.has_colors() else curses.A_REVERSE
    good = curses.color_pair(4) if curses.has_colors() else curses.A_BOLD

    selected = {r['id'] for r in items if r.get('default') or r.get('required')}
    cursor = 0
    offset = 0
    theme = 'dusk'

    def paint(row, col, content, style=0):
        height, width = screen.getmaxyx()
        if 0 <= row < height and col < width:
            screen.addnstr(row, col, content, max(0, width-col-1), style)

    def review():
        while True:
            screen.erase()
            height, width = screen.getmaxyx()
            if height >= 18 and width >= 62: screen.border()
            paint(1, 3, '✳  KUHL OS   /   FINAL REVIEW', accent | curses.A_BOLD)
            paint(3, 3, f'PALETTE  {theme.upper()}   /   {len(selected)} COMPONENTS', good)
            paint(4, 3, 'INSTALLATION   [━━━━━━━━━━━━━━━━━━━━]  02/02 REVIEW', accent)
            start = 5
            selected_items = [i for i in items if i['id'] in selected]
            for index, item in enumerate(selected_items[:max(0, height - 12)]):
                paint(start + index, 4, f'• {item["title"]}')
            warning_line = min(height - 6, start + len(selected_items) + 1)
            paint(warning_line, 3, ('Existing dotfiles will be backed up, then replaced.' if 'replace_existing' in selected else 'Existing dotfiles are preserved.') + ' GNOME stays.', muted)
            if 'vicinae' in selected:
                paint(warning_line + 1, 3, 'Vicinae requires separate COPR consent in the installer.', accent)
            paint(height - 3, 3, 'Y  Install    N  Back to choices    Q  Cancel', curses.A_BOLD)
            screen.refresh()
            key = screen.getch()
            if key in (ord('y'), ord('Y')):
                return {'theme': theme, 'selected': sorted(selected)}
            if key in (ord('q'), ord('Q'), 27):
                return None
            if key in (ord('n'), ord('N'), 10, 13):
                return 'back'

    while True:
        screen.erase()
        height, width = screen.getmaxyx()
        if height < 19 or width < 66:
            paint(0, 0, 'Resize terminal to at least 66 x 19 (Q to exit).')
            screen.refresh()
            if screen.getch() in (ord('q'), ord('Q'), 27):
                return None
            continue
        screen.border()
        paint(1, 3, '✳  K U H L    /    O S', accent | curses.A_BOLD)
        paint(2, 3, 'S T U D I O    E D I T I O N   /   F E D O R A   +   N I R I', muted)
        paint(4, 3, '✳  Build your Kuhl desktop. Your existing files stay safe.', curses.A_BOLD)
        paint(5, 3, 'UP/DOWN  navigate    SPACE  select    T  Day/Dusk    ENTER  review', muted)
        paint(6, 3, 'INSTALLATION   [━━━━━━━━━━··········]  01/02 CHOICES', accent)
        paint(7, 3, f'PALETTE {theme.upper():<6}     COMPONENTS {len(selected):02}/{len(items):02}   /   USER-CONTROLLED', good)
        screen.hline(8, 3, curses.ACS_HLINE, width-6)
        visible = max(1, height - 18)
        if cursor < offset:
            offset = cursor
        if cursor >= offset + visible:
            offset = cursor-visible+1
        for row, index in enumerate(range(offset, min(len(items), offset+visible)), start=9):
            item = items[index]
            tick = '●' if item['id'] in selected else '○'
            lock = '  [required]' if item.get('required') else ''
            line = f' {tick}  {item["title"]}{lock}'
            paint(row, 3, line, active if index == cursor else good if item['id'] in selected else 0)
        detail_y = height - 8
        screen.hline(detail_y, 3, curses.ACS_HLINE, width-6)
        current = items[cursor]
        paint(detail_y+1, 3, f'{current["section"].upper()}  /  {current["title"]}', accent | curses.A_BOLD)
        for row, part in enumerate(textwrap.wrap(current['description'], max(30, width - 10))[:3], start=detail_y+2):
            paint(row, 3, part)
        paint(height-2, 3, f'{cursor+1:02}/{len(items):02}   ·   KUHL STUDIO 0.7.2   ·   Q / ESC to cancel', muted)
        screen.refresh()
        key = screen.getch()
        if key in (curses.KEY_DOWN, ord('j')):
            cursor = min(len(items)-1, cursor+1)
        elif key in (curses.KEY_UP, ord('k')):
            cursor = max(0, cursor-1)
        elif key == ord(' '):
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
            answer = review()
            if answer != 'back':
                return answer


def plain(items):
    selected = {r['id'] for r in items if r.get('default') or r.get('required')}
    print('\n✳ KUHL OS 0.7.2  /  FEDORA + NIRI  /  TEXT MODE')
    for index, item in enumerate(items, 1):
        marker = 'x' if item['id'] in selected else ' '
        lock = ' [required]' if item.get('required') else ''
        print(f'{index:2}. [{marker}] {item["title"]}{lock}\n    {item["description"]}')
    print('\nToggle options by number, separated by commas, or press Enter for defaults.')
    answer = input('Numbers: ').strip()
    for part in answer.split(','):
        if not part.strip():
            continue
        pos = int(part)-1
        if not 0 <= pos < len(items):
            raise ValueError('Invalid option number')
        item = items[pos]
        if not item.get('required'):
            if item['id'] in selected:
                selected.remove(item['id'])
            else:
                selected.add(item['id'])
    theme = input('Palette: [dusk]/day: ').strip().lower() or 'dusk'
    if theme not in ('day', 'dusk'):
        raise ValueError('Unknown palette')
    print('GNOME is retained. ' + ('Existing configs will be backed up and replaced with REPLACE confirmation.' if 'replace_existing' in selected else 'Existing personal configurations are preserved.'))
    if 'vicinae' in selected:
        print('Vicinae requires separate third-party COPR consent.')
    answer = input(f'Apply Kuhl {theme.upper()} with {len(selected)} components? [y/N] ').strip().lower()
    return {'theme': theme, 'selected': sorted(selected)} if answer == 'y' else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--defaults', action='store_true')
    args = parser.parse_args()
    items = rows(args.config)
    if args.defaults:
        result = {'theme': 'dusk', 'selected': sorted(r['id'] for r in items if r.get('default') or r.get('required'))}
    else:
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise RuntimeError('Interactive installation requires a terminal. Use --defaults for automation.')
        try:
            result = curses.wrapper(menu, items)
        except curses.error:
            result = plain(items)
    if result is None:
        return 2
    Path(args.output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(f'Kuhl plan saved: {len(result["selected"])} choices, {result["theme"]} theme.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, IndexError, RuntimeError, OSError) as exc:
        print(f'Kuhl installer: {exc}', file=sys.stderr)
        sys.exit(1)
