#!/usr/bin/env python3
"""Validate Kuhl's six Niri configs with the installed Niri binary.

This check only writes to a temporary folder; it NEVER modifies ~/.config/niri.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    if shutil.which('niri') is None:
        print('[error] niri executable is required for native KDL validation.', file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix='kuhl-niri-preflight-') as td:
        root = Path(td)
        os.environ['HOME'] = str(root / 'home')
        os.environ['XDG_CONFIG_HOME'] = str(root / 'config')
        os.environ['XDG_DATA_HOME'] = str(root / 'share')
        os.environ['XDG_STATE_HOME'] = str(root / 'state')
        palettes = root / 'share/kuhl/themes.json'
        palettes.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / 'config/themes.json', palettes)
        shutil.copytree(ROOT / 'configs/upstream', root / 'share/kuhl/templates/upstream')
        # Import only after changing XDG_*, as render.py defines its paths at import time.
        import render
        for theme in __import__('json').loads((ROOT / 'config/themes.json').read_text()):
            folder = root / theme
            folder.mkdir(parents=True)
            config = folder / 'config.kdl'
            for part in ROOT.glob('configs/niri/*.kdl'):
                if part.name != 'kuhl-theme.kdl':
                    shutil.copy2(part, folder / part.name)
            generated = render.theme_files(theme)
            theme_path = next((p for p in generated if p.name == 'kuhl-theme.kdl'), None)
            if theme_path is None:
                raise RuntimeError(f'Missing generated KDL for {theme}')
            (folder / 'kuhl-theme.kdl').write_bytes(generated[theme_path])
            result = subprocess.run(['niri', 'validate', '--config', str(config)], check=False)
            if result.returncode:
                print(f'[error] {theme.title()} configuration failed native Niri validation.', file=sys.stderr)
                return 1
            print(f'[ok] Native Niri validation: Kuhl {theme.title()}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
