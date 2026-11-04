#!/usr/bin/env python3
"""AmethystOS Waybar preferences, kept separate from Light/Dark themes.

User changes are written only after verifying the deployed managed files.
Theme changes reapply these preferences, so the bar never resets unexpectedly.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

DEFAULTS = {'position':'top', 'density':'normal', 'modules':{'cpu':True,'memory':True,'battery':True,'player':True,'bluetooth':True,'clipboard':True,'tray':True}}
ALLOWED = tuple(DEFAULTS['modules'])
RIGHT = ['cpu','memory','battery','pulseaudio','network','bluetooth','custom/clipboard','custom/notifications','custom/settings','tray','custom/power']


def pref_path(home: Path): return home/'.local/state/amethystos-base-v1/bar.json'


def load(home: Path) -> dict:
    p=pref_path(home)
    data=json.loads(p.read_text()) if p.exists() else {}
    modules={k: bool(data.get('modules',{}).get(k,v)) for k,v in DEFAULTS['modules'].items()}
    pos=data.get('position',DEFAULTS['position'])
    density=data.get('density',DEFAULTS['density'])
    if pos not in ('top','bottom') or density not in ('compact','normal','roomy'):
        raise ValueError('Invalid saved bar settings')
    return {'position':pos,'density':density,'modules':modules}


def render(config: str, style: str, prefs: dict) -> tuple[str,str]:
    position=prefs['position']
    density=prefs['density']
    enabled=prefs['modules']
    # Preserve the upstream module definitions and include files; only replace
    # the top-level arrays (not their individual module settings).
    config,count=re.subn(r'("position"\s*:\s*)"(?:top|bottom)"',lambda m:m[1]+json.dumps(position),config,count=1)
    if count!=1:raise ValueError('Waybar position entry not found')
    rows=[x for x in RIGHT if enabled.get(x.split('/')[-1],True)]
    config,count=re.subn(r'"modules-right"\s*:\s*\[[^\]]*\]', '"modules-right": '+json.dumps(rows),config,count=1,flags=re.S)
    if count!=1:raise ValueError('Waybar right-side module list not found')
    middle=['clock']
    if enabled['player']:middle.insert(0,'custom/player')
    config,count=re.subn(r'"modules-center"\s*:\s*\[[^\]]*\]', '"modules-center": '+json.dumps(middle),config,count=1,flags=re.S)
    if count!=1:raise ValueError('Waybar center module list not found')
    sizes={'compact':('11px','1px 5px','3px'),'normal':('13px','2px 8px','6px'),'roomy':('15px','4px 11px','8px')}
    font,padding,gap=sizes[density]
    style += ('\n/* AmethystOS bar preferences: generated, do not edit here. */\n'
              f'window#waybar {{ font-size: {font}; }}\n'
              f'window#waybar #clock, window#waybar #custom-settings, window#waybar #custom-logo, '
              f'window#waybar #custom-power {{ padding: {padding}; }}\n'
              f'window#waybar .modules-right > widget {{ margin-left: {gap}; }}\n')
    return config,style


def change(home: Path, *, position=None,density=None,toggle=None, reload=True):
    home=home.resolve()
    prefs=load(home)
    if position is not None:
        if position not in ('top','bottom'):raise ValueError('Choose top or bottom')
        prefs['position']=position
    if density is not None:
        if density not in ('compact','normal','roomy'):raise ValueError('Choose compact, normal or roomy')
        prefs['density']=density
    if toggle is not None:
        if toggle not in ALLOWED:raise ValueError('Unknown bar module: '+toggle)
        prefs['modules'][toggle]=not prefs['modules'][toggle]
    # Validate all managed files BEFORE writing preferences; appearance.apply
    # checks for manual edits and updates rollback hashes on success.
    from appearance import managed_preflight,apply
    managed_preflight(home)
    target=pref_path(home);target.parent.mkdir(parents=True,exist_ok=True)
    before=target.read_bytes() if target.exists() else None
    target.write_text(json.dumps(prefs,indent=2)+'\n',encoding='utf-8')
    try:
        apply(home,gtk=False,reload=reload)
    except Exception:
        if before is None:target.unlink(missing_ok=True)
        else:target.write_bytes(before)
        raise
    return prefs


def main():
    ap=argparse.ArgumentParser(description='AmethystOS bar preferences')
    ap.add_argument('action',choices=('status','position','density','toggle'))
    ap.add_argument('value',nargs='?')
    ap.add_argument('--home',type=Path,default=Path.home())
    ap.add_argument('--no-reload',action='store_true')
    args=ap.parse_args()
    try:
        if args.action=='status':
            print(json.dumps(load(args.home),indent=2));return 0
        if args.value is None:raise ValueError('Value required')
        opts={args.action:args.value}
        print(json.dumps(change(args.home,reload=not args.no_reload,**opts),indent=2))
        return 0
    except (OSError,ValueError,RuntimeError) as exc:
        print('Amethyst bar: '+str(exc),file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
