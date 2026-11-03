#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
for f in bootstrap.sh install.sh uninstall.sh bin/kuhl lib/common.sh tests/validate.sh; do bash -n "$f"; done
python3 -m py_compile scripts/menu.py scripts/render.py scripts/validate_niri.py
python3 - <<'PY'
import json,re,struct
from pathlib import Path
choices=json.loads(Path('config/choices.json').read_text())['choices']
ids=[i['id'] for i in choices]
assert len(ids)==len(set(ids))
assert {'core','theme','vicinae'} <= set(ids)
assert not next(i for i in choices if i['id']=='vicinae')['default']
assert all(x.get('description') for x in choices)
for x in ('day','dusk'):
 assert x in json.loads(Path('config/themes.json').read_text())
for p in Path('assets/wallpapers').glob('*.png'):
 d=p.read_bytes()
 assert d[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',d[16:24])==(2560,1440)
conf=Path('configs/niri/config.kdl').read_text()
assert 'include "kuhl-theme.kdl"' in conf and 'Mod+Space repeat=false' in conf
assert 'Mod+Shift+E { quit;' in conf
assert 'keyboard {\n        numlock\n    }' in conf
assert 'keyboard { numlock }' not in conf
site=Path('main.html').read_text()
assert all(x in site for x in ['Niri','Super','Vicinae','Fuzzel','bash install.sh','Kuhl OS'])
assert 'kuhl.example' not in site and 'coming soon' not in site.lower()
assert 'ctrl+space' not in site.lower()
assert 'https://github.com/TerabyteEXE/Kuhl-OS.git' in site
print('[test] Bundled config, site and manifest: OK')
PY
OUT="$(mktemp)"
python3 scripts/menu.py --config config/choices.json --output "$OUT" --defaults
python3 - "$OUT" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['theme']=='dusk'; assert {'core','theme'} <= set(v['selected']); assert 'vicinae' not in v['selected']
PY
rm -f "$OUT"
echo '[test] Python TUI defaults: OK'
bash install.sh --dry-run >/dev/null
echo '[test] Installer dry-run: OK'
TMP="$(mktemp -d -t kuhl-tests.XXXXXXXX)"
trap 'rm -rf -- "$TMP"' EXIT
export HOME="$TMP/home" XDG_CONFIG_HOME="$TMP/config" XDG_DATA_HOME="$TMP/data" XDG_STATE_HOME="$TMP/state"
mkdir -p "$HOME" "$XDG_DATA_HOME/kuhl" "$XDG_CONFIG_HOME/niri"
cp config/themes.json "$XDG_DATA_HOME/kuhl/themes.json"
# Verify existing user file is protected; no Kuhl overwrite.
printf 'keep my niri config\n' > "$XDG_CONFIG_HOME/niri/config.kdl"
python3 scripts/render.py install --source configs --theme dusk >/dev/null
[[ "$(cat "$XDG_CONFIG_HOME/niri/config.kdl")" == 'keep my niri config' ]]
[[ -f "$XDG_CONFIG_HOME/waybar/style.css" ]]
[[ -f "$XDG_CONFIG_HOME/fuzzel/fuzzel.ini" ]]
[[ -f "$HOME/.local/share/applications/kuhl-day.desktop" ]]
[[ -f "$XDG_DATA_HOME/vicinae/themes/kuhl-dusk.toml" ]]
# Explicit replacement saves original, and uninstall restores it.
python3 scripts/render.py install --source configs --theme dusk --replace-configs >/dev/null
grep -q 'KUHL-MANAGED' "$XDG_CONFIG_HOME/niri/config.kdl"
python3 scripts/render.py theme --theme day >/dev/null
grep -q 'Kuhl day palette' "$XDG_CONFIG_HOME/niri/kuhl-theme.kdl"
# User edit must never be destroyed by re-install, theme change or uninstall.
echo '/* user edit */' >> "$XDG_CONFIG_HOME/waybar/style.css"
python3 scripts/render.py theme --theme dusk >/dev/null
grep -q 'user edit' "$XDG_CONFIG_HOME/waybar/style.css"
python3 scripts/render.py uninstall >/dev/null || true
[[ "$(cat "$XDG_CONFIG_HOME/niri/config.kdl")" == 'keep my niri config' ]]
grep -q 'user edit' "$XDG_CONFIG_HOME/waybar/style.css"
[[ ! -e "$XDG_CONFIG_HOME/kitty/colors.conf" ]]
echo '[test] Config protection, theme, backup restore, uninstall: OK'
if command -v niri >/dev/null 2>&1; then
  python3 scripts/validate_niri.py
else
  echo '[test] SKIPPED native Niri validation (niri not installed; Fedora CI checks both themes)'
fi
echo '[test] All checks passed'
