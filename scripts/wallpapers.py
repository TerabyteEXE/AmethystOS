#!/usr/bin/env python3
"""Install official wallpapers without replacing user images or a saved selection."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('AmethystDark.png', 'AmethystLight.png')

def install_wallpapers(home: Path, source: Path = ROOT / 'assets/wallpapers') -> dict:
    destination = home / 'Pictures/wallpapers'
    destination.mkdir(parents=True, exist_ok=True)
    new = []
    for name in NAMES:
        src = source / name
        if not src.is_file():
            raise FileNotFoundError(f'Missing official wallpaper: {src}')
        dst = destination / name
        if not dst.exists():
            shutil.copy2(src, dst)
            new.append(name)
    selection = home / '.local/state/amethystos-base-v1/wallpaper'
    # Don't replace a saved selection or a manually chosen image.
    # On a fresh install, choose the official dark wallpaper explicitly.
    existing = [f for f in destination.iterdir() if f.suffix.lower() in ('.png','.jpeg','.jpg','.webp') and f.name not in NAMES]
    if not selection.exists() and not existing:
        selection.parent.mkdir(parents=True, exist_ok=True)
        selection.write_text(str(destination / NAMES[0]) + '\n', encoding='utf-8')
        selected = True
    else:
        selected = False
    return {'copied': new, 'selected_dark': selected}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--home', type=Path, default=Path.home())
    opts = ap.parse_args()
    result = install_wallpapers(opts.home)
    print('Amethyst wallpapers ready: ' + ', '.join(NAMES))
    print('Selected Amethyst Dark as first-use wallpaper' if result['selected_dark'] else 'Preserved your existing wallpaper choice')
