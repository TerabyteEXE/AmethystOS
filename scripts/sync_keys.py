#!/usr/bin/env python3
"""Build Kuhl's Niri bind list and documentation from one owned manifest."""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'config/keys.json'
NIRI = ROOT / 'configs/niri/config.kdl'
DOC = ROOT / 'docs/KEYBINDS.md'
START = '    // BEGIN KUHL GENERATED KEYBINDS'
END = '    // END KUHL GENERATED KEYBINDS'

def generate():
    data = json.loads(SOURCE.read_text())
    lines = [START]
    seen = set()
    for section in data['sections']:
        lines.append(f'    // {section}')
        for b in [x for x in data['bindings'] if x['section'] == section]:
            if b['key'] in seen: raise ValueError(f'duplicate Niri binding: {b["key"]}')
            seen.add(b['key'])
            opts = (' repeat=false' if b.get('repeat') is False else '') + (' allow-when-locked=true' if b.get('locked') else '')
            lines.append(f'    {b["key"]}{opts} {{ {b["action"]} }}')
        lines.append('')
    lines.append(END)
    doc = ['# Kuhl OS — keyboard reference', '', 'Press **Ctrl + Super + K** in Niri for a searchable on-screen guide. This table and the Niri bindings are both generated from `config/keys.json`.','','**Super** is the Windows key on most keyboards. **Niri uses scrolling columns**, so focus and move are different actions.','','**Migration note:** the old Super + Ctrl + K (move up) is now the requested help shortcut; use **Super + Shift + K** to move up. Screen lock is **Super + Alt + L** so Shift + L stays available for moving columns.','']
    for sec in data['sections']:
        doc += [f'## {sec}', '', '| Key | Action |', '| --- | --- |']
        doc += [f'| {b["show"]} | {b["title"]} |' for b in data['bindings'] if b['section'] == sec]
        doc.append('')
    return '\n'.join(lines), '\n'.join(doc)+'\n'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    bindings, doc = generate()
    content=NIRI.read_text()
    if START not in content or END not in content: raise ValueError('missing bind markers')
    before,rest = content.split(START,1)
    _,after=rest.split(END,1)
    target=before+bindings+after
    if args.check:
        if target != content or DOC.read_text()!=doc:
            print('Kuhl generated keybindings are not synchronized.',file=sys.stderr);return 1
        print('[ok] Keybindings and keyboard guide are synchronized')
    else:
        NIRI.write_text(target);DOC.write_text(doc)
    return 0
if __name__=='__main__':sys.exit(main())
