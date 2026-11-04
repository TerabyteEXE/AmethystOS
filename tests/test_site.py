#!/usr/bin/env python3
"""Verify the static GitHub Pages site uses valid relative paths and source-derived docs."""
from html.parser import HTMLParser
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        for attribute in ('href','src'):
            if attribute in values:self.links.append(values[attribute])
files=list(ROOT.glob('*.html'))+list((ROOT/'wiki').glob('*.html'))
required={
    'index.html', 'about.html', 'install.html', 'wiki/index.html',
    'wiki/keybinds.html', 'wiki/customization.html', 'wiki/troubleshooting.html'
}
actual={str(f.relative_to(ROOT)) for f in files}
missing=required-actual
assert not missing, f'Missing required site pages: {sorted(missing)}'
assert len(actual)==len(files), 'Duplicated site page in discovery'

for source in files:
    scanner=Links(); scanner.feed(source.read_text())
    for link in scanner.links:
        if link.startswith(('#','http://','https://','mailto:','tel:')):continue
        location=(source.parent/link.split('#',1)[0]).resolve()
        assert location.is_relative_to(ROOT) and location.is_file(),f'{source.name}: missing or unsafe link {link}'
assert (ROOT/'assets/wallpapers/AmethystDark.png').is_file()
assert (ROOT/'assets/wallpapers/AmethystLight.png').is_file()
assert (ROOT/'assets/branding/amethyst-logo.png').is_file()
assert (ROOT/'assets/branding/amethyst-logo-original.png').is_file()
assert (ROOT/'assets/favicon.png').is_file()
assert (ROOT/'assets/apple-touch-icon.png').is_file()
for f in files:
    assert 'AmethystOS' in f.read_text(), f'{f.name}: brand missing'
    assert 'assets/branding/amethyst-logo.png' in f.read_text(), f'{f.name}: official logo missing'
assert 'TerabyteEXE/AmethystOS' in (ROOT/'bootstrap.sh').read_text()
print(f'[test] {len(files)} website pages and all local links: OK')
