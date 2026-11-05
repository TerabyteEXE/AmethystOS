#!/usr/bin/env python3
"""AmethystOS terminal checklist. Arrow keys + Space, with TTY owned by the user.

Noninteractive flags are deliberately available for automated installs and CI.
"""
from __future__ import annotations
import argparse
import curses
import json
import os
from pathlib import Path
import sys

# One app per row. Keys are shared with scripts/packages.sh.
GROUPS = [
    ('firefox', 'Firefox', 'Web', 'Fedora browser'),
    ('chromium', 'Chromium', 'Web', 'Alternative web browser'),
    ('thunderbird', 'Thunderbird', 'Web', 'Mail'),
    ('libreoffice', 'LibreOffice', 'Office', 'Writer and Calc'),
    ('gimp', 'GIMP', 'Creative', 'Photo editor'),
    ('krita', 'Krita', 'Creative', 'Painting and drawing'),
    ('inkscape', 'Inkscape', 'Creative', 'Vector graphics'),
    ('kdenlive', 'Kdenlive', 'Creative', 'Video editor'),
    ('audacity', 'Audacity', 'Creative', 'Audio editor'),
    ('obs', 'OBS Studio', 'Creative', 'Screen recording · Flathub'),
    ('steam', 'Steam', 'Gaming', 'Games · Flathub'),
    ('lutris', 'Lutris', 'Gaming', 'Game launcher'),
    ('discord', 'Discord', 'Gaming', 'Chat · Flathub'),
    ('celluloid', 'Celluloid', 'Media', 'Video player'),
    ('rhythmbox', 'Rhythmbox', 'Media', 'Music player'),
    ('btop', 'btop', 'Utilities', 'System monitor'),
    ('flatseal', 'Flatseal', 'Utilities', 'Flatpak permissions · Flathub'),
    ('calculator', 'Calculator', 'Utilities', 'GNOME Calculator'),
    ('archive', 'Archive Manager', 'Utilities', 'Compressed files'),
    ('git', 'Git', 'Development', 'Version control'),
    ('neovim', 'Neovim', 'Development', 'Terminal editor'),
    ('micro', 'Micro', 'Development', 'Simple terminal editor'),
    ('vscode', 'VSCodium', 'Development', 'Free code editor · Flathub'),
]
# Existing scripted installs can retain old group names; the TUI shows only individual apps.
LEGACY = {'essentials','office','creative','dev','media','gaming'}
DEFAULTS: set[str] = set()


def create_plan(selected, replace=False, appearance=True, theme='dark'):
    valid={key for key,*_ in GROUPS} | LEGACY
    unknown=set(selected)-valid
    if unknown:
        raise ValueError('Unknown optional apps: '+', '.join(sorted(unknown)))
    return {'groups': sorted(set(selected)), 'replace':bool(replace),
            'apply_dark':bool(appearance), 'theme':theme, 'schema':2}


def checklist(stdscr, selected, flags):
    curses.curs_set(0)
    stdscr.keypad(True)
    try: curses.use_default_colors(); curses.start_color(); curses.init_pair(1, curses.COLOR_MAGENTA, -1); curses.init_pair(2, curses.COLOR_CYAN, -1)
    except curses.error: pass
    items=[(key,title,category,description) for key,title,category,description in GROUPS]
    # The final options are selectable in the same checklist.
    items += [('_replace','Back up and replace existing configs','Setup','Required for an upgrade'),
              ('_preserve','Preserve current appearance','Setup','Do not reset existing theme'),
              ('_light','Start in Amethyst Light','Setup','Otherwise use Dark')]
    focus=0; top=0
    while True:
        height,width=stdscr.getmaxyx()
        if height<12 or width<52:
            stdscr.erase()
            stdscr.addnstr(0,0,'Resize terminal to at least 52 x 12.',max(0,width-1))
            stdscr.refresh()
            key=stdscr.getch()
            if key in (27,ord('q')): raise KeyboardInterrupt
            continue
        visible=max(1,height-8)
        top=min(max(top,focus-visible+1),focus)
        stdscr.erase()
        def text(y,x,s,attr=0):
            if 0<=y<height and x<width:
                try:stdscr.addnstr(y,x,s,max(0,width-x-1),attr)
                except curses.error: pass
        text(1,2,'◆ AMETHYSTOS  /  DESKTOP SETUP',curses.A_BOLD | curses.color_pair(1))
        text(2,2,'↑ ↓ navigate    Space choose    Enter continue    Q cancel')
        text(3,2,'Optional software — one app per line; Flathub items are opt-in.')
        for row in range(visible):
            idx=top+row
            if idx>=len(items): break
            code,name,category,helptext=items[idx]
            checked = (code in selected if not code.startswith('_') else flags[code])
            prefix='[x]' if checked else '[ ]'
            value=f' {prefix}  {name:<19} {category:<12} {helptext}'
            text(row+4,2,value,curses.A_REVERSE if idx==focus else 0)
        text(height-3,2,f'Selected: {len(selected)}  ·  Appearance: {"Light" if flags["_light"] else "Dark"}  ·  {'replace' if flags['_replace'] else 'preserve'}')
        text(height-2,2,'This installer keeps Fedora and GNOME. Backups are saved before replacement.',curses.A_DIM)
        stdscr.refresh()
        key=stdscr.getch()
        if key in (curses.KEY_DOWN,ord('j')): focus=min(len(items)-1,focus+1)
        elif key in (curses.KEY_UP,ord('k')): focus=max(0,focus-1)
        elif key in (curses.KEY_NPAGE,): focus=min(len(items)-1,focus+visible)
        elif key in (curses.KEY_PPAGE,): focus=max(0,focus-visible)
        elif key in (ord(' '),):
            code=items[focus][0]
            if code.startswith('_'): flags[code]=not flags[code]
            elif code in selected: selected.remove(code)
            else:selected.add(code)
        elif key in (10,13,curses.KEY_ENTER): break
        elif key in (27,ord('q')): raise KeyboardInterrupt
    return selected,flags


def interactive_plan():
    selected=set(DEFAULTS)
    flags={'_replace':False,'_preserve':False,'_light':False}
    # With curl|bash, stdin is the downloaded script. Reattach our own stdin
    # and stdout to the controlling terminal in this *child* process.
    tty=os.open('/dev/tty',os.O_RDWR)
    try:
        os.dup2(tty,0)
        os.dup2(tty,1)
        selected,flags=curses.wrapper(checklist,selected,flags)
        with open('/dev/tty','w',encoding='utf-8') as output:
            output.write('\n◆ AMETHYSTOS  Your installation plan\n\n')
            output.write('  Optional apps: '+(', '.join(sorted(selected)) or '(none)')+'\n')
            output.write('  Existing configs: '+('back up and replace' if flags['_replace'] else 'preserve')+'\n')
            output.write('  Appearance: '+('preserve' if flags['_preserve'] else ('light' if flags['_light'] else 'dark'))+'\n')
            output.write('  Continue? [y/N] ');output.flush()
        with open('/dev/tty','r',encoding='utf-8') as answer:
            if answer.readline().strip().lower() not in ('y','yes'):
                raise KeyboardInterrupt
    finally:
        os.close(tty)
    return create_plan(selected,flags['_replace'],not flags['_preserve'],'light' if flags['_light'] else 'dark')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--non-interactive',action='store_true')
    parser.add_argument('--replace',action='store_true')
    parser.add_argument('--no-theme',action='store_true')
    parser.add_argument('--theme',choices=('dark','light'),default='dark')
    parser.add_argument('--groups',default=None,help='comma-separated individual app keys')
    args=parser.parse_args()
    try:
        if args.non_interactive or args.groups is not None:
            groups=([x for x in args.groups.split(',') if x] if args.groups is not None else sorted(DEFAULTS))
            plan=create_plan(groups,args.replace,not args.no_theme,args.theme)
        else:
            plan=interactive_plan()
            if args.replace:plan['replace']=True
            if args.no_theme:plan['apply_dark']=False
    except (KeyboardInterrupt,EOFError):
        print('\nSetup canceled. No desktop files were installed.',file=sys.stderr)
        return 130
    except (OSError,curses.error) as exc:
        print(f'Interactive checklist failed: {exc}. Use a real terminal or --non-interactive.',file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(plan,indent=2)+'\n')
    return 0

if __name__=='__main__':raise SystemExit(main())
