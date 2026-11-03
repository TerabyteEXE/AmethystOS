#!/usr/bin/env python3
"""Kuhl's original lightweight terminal UI: searchable shortcuts & control center.

Uses only Python's standard library. Adaptations and artwork credited in docs/CREDITS.md.
"""
import argparse
import curses
import json
import os
from pathlib import Path
import subprocess
import sys

KUHL_BIN = str(Path.home()/'.local/bin/kuhl')
DATA = Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share'))/'kuhl'
STATE = Path(os.environ.get('XDG_STATE_HOME', Path.home()/'.local/state'))/'kuhl'
KEYS = DATA/'keys.json'

MENU = {
    'main': [
        ('Appearance', 'themes', 'Change palette or background'),
        ('Keyboard guide', 'keys', 'Search shortcuts by name or key'),
        ('Settings and diagnostics', 'doctor', 'Check the Kuhl session'),
        ('File manager', 'files', 'Browse your files'),
        ('Network settings', 'network', 'Connections and Wi-Fi'),
        ('Volume settings', 'audio', 'Microphone and output levels'),
        ('Power / session', 'power', 'Lock, log out or shut down'),
    ],
    'themes': [
        ('Frontier · default', 'frontier', 'Gold & olive · PrisonerCoin artwork'),
        ('Dyson', 'dyson', 'Electric blue · PrisonerCoin artwork'),
        ('Puncture', 'puncture', 'Neon green · PrisonerCoin artwork'),
        ('Slow End', 'slowend', 'Rose & violet · PrisonerCoin artwork'),
        ('Kuhl Dusk', 'dusk', 'Original charcoal / muted gold'),
        ('Kuhl Day', 'day', 'Warm cream / muted olive'),
        ('Custom wallpaper path', 'wallpaper', 'Use your own JPG, PNG or WebP'),
        ('Solid background', 'solid', 'Use a clean color until you add artwork'),
        ('Existing Kuhl wallpapers', 'legacy', 'Select original bundled art'),
    ],
    'legacy': [
        ('Original Day image', 'legacy-day', 'Your previous image, kept optional'),
        ('Original Dusk image', 'legacy-dusk', 'Your previous image, kept optional'),
        ('Original default image', 'legacy-default', 'Your previous image, kept optional'),
    ],
    'power': [
        ('Lock', 'lock', 'Require a password to unlock'),
        ('Log out of Niri', 'logout', 'Niri will ask for confirmation'),
        ('Suspend', 'suspend', 'Sleep until you wake the computer'),
        ('Restart', 'reboot', 'Confirmation required'),
        ('Shut down', 'poweroff', 'Confirmation required'),
    ],
}


def action(item):
    actions = {
        'day': [KUHL_BIN,'theme','day'], 'dusk':[KUHL_BIN,'theme','dusk'],
        'frontier':[KUHL_BIN,'theme','frontier'], 'dyson':[KUHL_BIN,'theme','dyson'],
        'puncture':[KUHL_BIN,'theme','puncture'], 'slowend':[KUHL_BIN,'theme','slowend'],
        'solid':[KUHL_BIN,'wallpaper','reset'],
        'legacy-day':[KUHL_BIN,'wallpaper','day'], 'legacy-dusk':[KUHL_BIN,'wallpaper','dusk'],
        'legacy-default':[KUHL_BIN,'wallpaper','default'], 'doctor':[KUHL_BIN,'doctor'],
        'files':['thunar'], 'network':['nm-connection-editor'], 'audio':['pavucontrol'],
        'lock':['swaylock','-f','-c','1c1b1a'], 'logout':['niri','msg','action','quit'],
        'suspend':['systemctl','suspend'], 'reboot':['systemctl','reboot'],
        'poweroff':['systemctl','poweroff'],
    }
    if item not in actions: return
    if item in ('reboot','poweroff'):
        answer = input(f'\nConfirm {item.upper()}? Type YES to continue: ')
        if answer != 'YES': return
    try:
        subprocess.run(actions[item], check=False)
    except FileNotFoundError:
        print(f'Not installed: {actions[item][0]}')
    if item in ('doctor','network','audio'):
        input('\nPress Enter to close...')


def ui(screen, mode, firstpage):
    curses.curs_set(0)
    screen.keypad(True)
    curses.start_color()
    try: curses.use_default_colors()
    except curses.error: pass
    curses.init_pair(1,curses.COLOR_YELLOW,-1)
    curses.init_pair(2,curses.COLOR_CYAN,-1)
    curses.init_pair(3,curses.COLOR_BLACK,curses.COLOR_YELLOW)
    curses.init_pair(4,curses.COLOR_WHITE,-1)
    gold=curses.color_pair(1)|curses.A_BOLD
    soft=curses.color_pair(2)
    selected=curses.color_pair(3)|curses.A_BOLD
    normal=curses.color_pair(4)
    bindings = json.loads(KEYS.read_text(encoding='utf-8'))
    categories = ['All'] + bindings['sections']
    cat=0
    page=firstpage if firstpage in MENU else 'main'
    cursor=0
    offset=0
    search=''
    search_mode=False
    chosen=None

    def put(y,x,s,color=0):
        h,w=screen.getmaxyx()
        if 0<=y<h and 0<=x<w-1:
            try:screen.addnstr(y,x,str(s),max(0,w-1-x),color)
            except curses.error: pass

    def line(y,x,n):
        h,w=screen.getmaxyx()
        if 0<=y<h and n>0:
            put(y,x,'─'*min(n,max(0,w-x-2)),soft)

    def contents():
        if mode=='keys':
            options=[(b['show'],b['title'],b['section']) for b in bindings['bindings'] if (cat==0 or b['section']==categories[cat]) and (search.lower() in (b['show']+' '+b['title']+' '+b['section']).lower())]
            return options
        return MENU[page]

    while True:
        screen.erase()
        h,w=screen.getmaxyx()
        if h<18 or w<54:
            put(1,2,'KUHL  /  RESIZE TO AT LEAST 54 x 18',gold)
            put(3,2,'Q or ESC exits.'); screen.refresh()
            ch=screen.getch()
            if ch in (ord('q'),27):break
            continue
        width=min(w-6,90)
        x=max(2,(w-width)//2)
        put(1,x,'✳  K U H L   /   O S',gold)
        put(2,x,'N I R I   D E S K T O P    ·    F E D O R A',soft)
        put(4,x,'KEYBOARD ATLAS' if mode=='keys' else 'CONTROL CENTER  /  '+page.upper(),gold)
        if mode=='keys':
            put(5,x, f'SECTION  {categories[cat]}    ·    TAB cycles sections',soft)
            put(6,x,('SEARCH  / '+search+('█' if search_mode else '')).ljust(min(width,75)),normal)
        else:
            put(5,x,'One place for your entire desktop. No hidden settings.',soft)
            put(6,x,'Super + Space: search    ·    Ctrl + Super + K: shortcuts',soft)
        line(7,x,width)
        opts=contents()
        visible=max(1,h-14)
        cursor=min(cursor,max(0,len(opts)-1))
        offset=min(offset,max(0,len(opts)-visible))
        if cursor<offset:offset=cursor
        if cursor>=offset+visible:offset=cursor-visible+1
        for position in range(offset,min(len(opts),offset+visible)):
            row=8+position-offset
            a,b,c=opts[position]
            prefix='▸' if position==cursor else ' '
            if mode=='keys':
                left=f'{prefix} {a:<25} {b}'
            else:
                left=f'{prefix} {a:<29} {c}'
            put(row,x+1,left[:width-3],selected if position==cursor else normal)
        if not opts:put(9,x+1,'No matches. Try a different term.',soft)
        line(h-5,x,width)
        if mode=='keys':
            put(h-4,x,f'{len(opts)} shortcuts  ·  / search  ·  TAB category  ·  ↑↓ scroll  ·  Q close',soft)
        else:
            put(h-4,x,'↑↓ choose  ·  ENTER select  ·  BACKSPACE back  ·  Q close',soft)
        put(h-2,x,'Kuhl OS  /  quiet by design',gold)
        screen.refresh()
        ch=screen.getch()
        if mode=='keys' and search_mode:
            if ch in (27,10,13):search_mode=False
            elif ch in (curses.KEY_BACKSPACE,127,8):search=search[:-1];cursor=offset=0
            elif 32<=ch<=126:search+=chr(ch);cursor=offset=0
            continue
        if ch in (ord('q'),27):break
        if ch in (curses.KEY_UP,ord('k')): cursor=max(0,cursor-1)
        elif ch in (curses.KEY_DOWN,ord('j')):cursor=min(len(opts)-1,cursor+1)
        elif mode=='keys':
            if ch==ord('/'):
                search_mode=True
            elif ch==9:
                cat=(cat+1)%len(categories);cursor=offset=0
        else:
            if ch in (curses.KEY_BACKSPACE,127,8):
                page='main';cursor=offset=0
            elif ch in (10,13,curses.KEY_ENTER) and opts:
                target=opts[cursor][1]
                if target in MENU:
                    page=target;cursor=offset=0
                else:
                    chosen=target;break
    return chosen


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('mode',choices=['keys','menu'])
    ap.add_argument('--page',default='main')
    args=ap.parse_args()
    if args.mode=='keys':
        if not KEYS.is_file():raise SystemExit(f'Missing {KEYS}')
    chosen=curses.wrapper(ui,args.mode,args.page)
    if chosen=='wallpaper':
        path=input('\nFull path to your wallpaper file (blank cancels): ').strip()
        if path:action_args=[KUHL_BIN,'wallpaper','set',path];subprocess.run(action_args,check=False)
    elif chosen=='keys':
        subprocess.run([KUHL_BIN,'keys','--ui'],check=False)
    elif chosen:action(chosen)
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except KeyboardInterrupt:sys.exit(130)
