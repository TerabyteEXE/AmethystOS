#!/usr/bin/env python3
"""Rebuild searchable web + plain text keybinding docs from the installed Niri module."""
import argparse, html, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KEYS=ROOT/'payload/niri/modules/keybinds.kdl'
HTML=ROOT/'wiki/keybinds.html'
TXT=ROOT/'docs/KEYBINDINGS.txt'
PAT=re.compile(r'^\s*([A-Za-z0-9_+]+)\s+[^{}]*\{\s*([^{}]+?)\s*\}\s*$')
GROUPS=['Applications & shell','Workspaces','Window management','Media & hardware','System']

def describe(a):
    if 'panel-toggle launcher' in a: return 'Toggle application launcher'
    if 'panel-toggle clipboard' in a: return 'Open clipboard history'
    if 'panel-toggle session' in a: return 'Power and session menu'
    if 'panel-toggle notifications' in a: return 'Notification panel'
    if 'settings-toggle' in a: return 'Open desktop settings'
    if 'panel-toggle wallpaper' in a: return 'Choose wallpaper'
    if 'panel-toggle control-center' in a: return 'Open control center'
    if 'notifications toggleHistory' in a: return 'Show notification history'
    if 'launcher clipboard' in a: return 'Clipboard history'
    if 'launcher emoji' in a: return 'Emoji picker'
    if 'session lock' in a: return 'Lock screen'
    if 'sessionMenu' in a: return 'Power and session menu'
    if 'amethyst-keys' in a: return 'Open searchable keybinding guide'
    if 'amethyst-browser' in a: return 'Open browser'
    if 'nautilus' in a: return 'Open Files'
    if 'kitty' in a: return 'Open Kitty terminal'
    if 'gnome-text-editor' in a: return 'Open text editor'
    if 'celluloid' in a: return 'Open video player'
    if 'close-window' in a: return 'Close active window'
    if 'toggle-overview' in a: return 'Toggle overview'
    if 'focus-workspace' in a: return 'Focus workspace '+a.rsplit(' ',1)[-1].strip('";')
    if 'move-column-to-workspace' in a: return 'Move column to workspace '+a.rsplit(' ',1)[-1].strip('";')
    if 'screenshot' in a: return 'Take screenshot'
    if 'brightnessctl' in a: return 'Adjust brightness'
    if 'wpctl set-' in a: return 'Adjust volume or microphone'
    if 'playerctl' in a: return 'Media playback control'
    return a.split('{',1)[0].replace('"','').replace('-', ' ').strip().capitalize()

def parse():
    keys=[]
    for line in KEYS.read_text().splitlines():
        if line.lstrip().startswith('//'): continue
        m=PAT.match(line)
        if not m: continue
        combo,action=m.group(1),m.group(2).strip().rstrip(';')
        if combo=='binds': continue
        if combo.startswith('XF86'): group='Media & hardware'
        elif 'workspace' in action: group='Workspaces'
        elif action.startswith('spawn') or 'noctalia msg ' in action: group='Applications & shell'
        elif any(x in action for x in ('window','column','monitor','focus','fullscreen','floating')): group='Window management'
        else: group='System'
        keys.append((combo.replace('Super','Super').replace('_',' '),describe(action),group))
    return keys

def build():
    keys=parse()
    if len(keys)<40: raise RuntimeError('Niri binding parser found too few shortcuts')
    old=HTML.read_text()
    start=old.split('<article class="doc-content">')[0]
    end=old.split('</article></div></div></main>',1)[1]
    out=['<p>Shortcuts generated from the installed <code>payload/niri/modules/keybinds.kdl</code>. This release uses AmethystOS Niri configuration and Noctalia v5. Search by action or key.</p>',
         '<input class="key-search" type="search" placeholder="Search shortcuts…" aria-label="Search keyboard shortcuts" data-key-search>',
         '<div class="key-controls">'+''.join('<button class="filter-btn" type="button" data-filter="'+html.escape(c,quote=True)+'" aria-pressed="'+('true' if i==0 else 'false')+'">'+html.escape(c)+'</button>' for i,c in enumerate(['all']+GROUPS))+'</div>',
         '<p data-result-count></p>']
    for group in GROUPS:
        part=[(k,a) for k,a,g in keys if g==group]
        if not part:continue
        out.append('<section class="key-group" data-key-group><h2>'+html.escape(group)+'</h2><table class="key-table"><tbody>')
        for k,a in part:
            out.append('<tr data-key-row data-category="'+html.escape(group,quote=True)+'"><td><span class="kbd">'+html.escape(k)+'</span></td><td>'+html.escape(a)+'</td></tr>')
        out.append('</tbody></table></section>')
    out.append('<p class="no-results" data-no-results>No shortcuts matched your search.</p>')
    text=start+'<article class="doc-content">'+'\n'.join(out)+'</article></div></div></main>'+end
    plain='# AMETHYSTOS · NIRI / NOCTALIA v5 KEYBINDINGS\n\n'+'\n'.join(f'{k:<28} {a}' for k,a,g in keys)+'\n'
    return text,plain

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true');a=ap.parse_args()
    h,t=build()
    if a.check:
        if HTML.read_text()!=h or TXT.read_text()!=t: raise SystemExit('Generated keybind docs outdated: run python3 scripts/build_site.py')
        print('[ok] keybinding docs up to date')
    else:
        HTML.write_text(h); TXT.write_text(t); print('Generated',len(parse()),'shortcuts')
if __name__=='__main__':main()
