#!/usr/bin/env bash
set -Eeuo pipefail
trap 'code=$?; echo "[test] FAILED line $LINENO: $BASH_COMMAND (exit $code)" >&2' ERR
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
echo '[test] License and required files'
for f in LICENSE LICENSE.gigi third_party/gigis-rice/LICENSE README.md \
  payload/niri/config.kdl payload/niri/modules/keybinds.kdl payload/noctalia/settings.json \
  payload/noctalia/plugins.json assets/wallpapers/AmethystDark.png \
  assets/wallpapers/AmethystLight.png index.html install.html wiki/index.html wiki/keybinds.html; do
  test -s "$f" || { echo "missing $f" >&2; exit 1; }
done
for f in install.sh bootstrap.sh uninstall.sh scripts/packages.sh; do bash -n "$f"; done
find payload/local-bin -type f -print0 | while IFS= read -r -d '' p; do bash -n "$p"; done
python3 -m py_compile scripts/deploy.py scripts/setup_ui.py scripts/build_site.py scripts/wallpapers.py scripts/system_update.py
python3 scripts/build_site.py --check
python3 - <<'PYCODE'
import json,pathlib
for p in pathlib.Path('payload/noctalia').rglob('*.json'):
 try: json.loads(p.read_text())
 except Exception as exc: raise AssertionError(f'Invalid JSON: {p}') from exc
print('[ok] All Noctalia JSON files parse')
PYCODE
python3 tests/test_gigi.py
bash install.sh --dry-run >/dev/null
echo '[test] Dry-run installer: OK'
if command -v niri >/dev/null 2>&1; then
  tmp=$(mktemp -d)
  trap 'rm -rf -- "$tmp"' EXIT
  python3 scripts/deploy.py install --dry-run --replace --home "$tmp" --require-niri
else
  echo '[test] Native Niri validation skipped (not installed here)'
fi
echo 'All portable AmethystOS Gigi rebase tests passed.'
