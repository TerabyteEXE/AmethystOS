#!/usr/bin/env bash
set -Eeuo pipefail
trap 'code=$?; echo "[test] FAILED line $LINENO: $BASH_COMMAND (exit $code)" >&2' ERR
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
echo '[test] Repository, website and licensing'
for f in LICENSE LICENSE.gigi README.md \
  payload/niri/config.kdl payload/niri/modules/keybinds.kdl \
  payload/noctalia/config.toml payload/noctalia/palettes/Amethyst.json \
  assets/wallpapers/AmethystDark.png assets/wallpapers/AmethystLight.png \
  index.html install.html about.html wiki/index.html wiki/keybinds.html; do
  test -s "$f" || { echo "missing $f" >&2; exit 1; }
done
for f in install.sh bootstrap.sh uninstall.sh scripts/packages.sh scripts/greeter.sh tests/test_packages.sh; do bash -n "$f"; done
find payload/local-bin -type f ! -name amethyst-welcome ! -name '*.pyc' -print0 | while IFS= read -r -d '' p; do bash -n "$p"; done
python3 -m py_compile scripts/*.py payload/local-bin/amethyst-welcome tests/test_desktop.py
python3 scripts/build_site.py --check
python3 - <<'PYTOML'
import pathlib,tomllib,json
p=pathlib.Path('payload/noctalia')
tomllib.loads((p/'config.toml').read_text())
json.loads((p/'palettes/Amethyst.json').read_text())
print('[ok] Noctalia v5 TOML and palette parse')
PYTOML
bash tests/test_packages.sh
python3 tests/test_setup_ui_pty.py
python3 tests/test_desktop.py
bash scripts/greeter.sh --help >/dev/null
python3 - <<'PYGREETER'
import pathlib
s = pathlib.Path('scripts/greeter.sh').read_text()
for token in ('systemctl disable "$active"', 'systemctl enable greetd.service',
              'systemctl enable "$prior"', '--setup-system', 'amethyst-dark.png'):
    assert token in s, token
assert pathlib.Path('docs/GREETER.md').is_file()
print('[ok] Opt-in Noctalia Greeter and restore controls')
PYGREETER
bash install.sh --dry-run >/dev/null
echo '[ok] Installer dry-run'
if command -v niri >/dev/null 2>&1; then
  tmp=$(mktemp -d)
  trap 'rm -rf -- "$tmp"' EXIT
  python3 scripts/deploy.py install --dry-run --replace --home "$tmp" --require-niri
else
  echo '[test] Native Niri parser skipped (not installed here)'
fi
echo '[ok] Portable AmethystOS RC4 tests passed'
