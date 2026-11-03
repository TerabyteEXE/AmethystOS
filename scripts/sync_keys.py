#!/usr/bin/env python3
"""Verify Kuhl guide against the actual MIT-licensed KyleOS-derived bindings."""
import argparse, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
BIND_FILE=ROOT/'configs/niri/binds.kdl'
MANIFEST=ROOT/'config/keys.json'
DOC=ROOT/'docs/KEYBINDS.md'

def make_doc(data):
    lines=['# Kuhl OS — complete keyboard reference', '',
           'Based on the KyleOS Niri keybindings (MIT, Rosenkranz / Person-008).',
           'Kuhl integration adds **Ctrl + Super + K** for the searchable guide.',
           'The exact bindings are in `configs/niri/binds.kdl`; this guide is checked against that file.', '']
    for section in data['sections']:
        lines.extend([f'## {section}', '', '| Shortcut | Action |', '| --- | --- |'])
        for b in data['bindings']:
            if b['section']==section:
                lines.append(f'| {b["show"]} | {b["title"]} |')
        lines.append('')
    return '\n'.join(lines)+'\n'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    data=json.loads(MANIFEST.read_text());content=BIND_FILE.read_text();seen=set()
    for b in data['bindings']:
        key=b['key'];action=b['action']
        if key in seen: raise ValueError(f'duplicate manifest shortcut: {key}')
        seen.add(key)
        matcher=r'^\s*'+re.escape(key)+r'(?:\s+[^{}]*)?\s*\{\s*'+re.escape(action)+r'\s*\}\s*$'
        if not re.search(matcher,content,re.M):
            print(f'Missing or altered Niri binding: {key} -> {action}',file=sys.stderr)
            return 1
    # Catch unlisted active binds, not only missing listed binds.
    active=re.findall(r'^\s*([A-Za-z0-9_+]+)(?:\s+[^{}]*)?\s*\{\s*.*?\s*\}\s*$',content,re.M)
    for k in active:
        if k not in seen:
            print(f'Unlisted Niri binding: {k}',file=sys.stderr);return 1
    doc=make_doc(data)
    if args.check:
        if DOC.read_text()!=doc:
            print('Keyboard documentation is out of date.',file=sys.stderr);return 1
        print(f'[ok] {len(seen)} KyleOS / Kuhl shortcuts and guide synchronized')
    else:
        DOC.write_text(doc)
    return 0
if __name__=='__main__':sys.exit(main())
