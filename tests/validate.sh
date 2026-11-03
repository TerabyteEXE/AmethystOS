#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo '[test] Repository and license'
test -s LICENSE.upstream
test -s LICENSE
test -s README.md
test -s payload/niri/config.kdl
test -s payload/waybar/config.jsonc
test ! -e index.html
for script in install.sh uninstall.sh bootstrap.sh; do bash -n "$script"; done
find payload -name '*.sh' -type f -print0 | while IFS= read -r -d '' shfile; do
  if head -n1 "$shfile" | grep -q python; then python3 -m py_compile "$shfile"; else bash -n "$shfile"; fi
done
find payload/local-bin -type f -print0 | while IFS= read -r -d '' shfile; do bash -n "$shfile"; done
python3 -m py_compile scripts/deploy.py

echo '[test] Direct upstream config and safety checks'
python3 - <<'PY'
from pathlib import Path
p=Path('payload')
assert 'include "keybinds.kdl"' in (p/'niri/config.kdl').read_text()
assert 'include "basicsettings.kdl"' in (p/'niri/config.kdl').read_text()
assert 'spawn "fuzzel"' in (p/'niri/keybinds.kdl').read_text()
assert 'close-window' in (p/'niri/keybinds.kdl').read_text()
assert not (p/'gtk-4.0/assets').exists()
assert 'pkill -f xdg-desktop-portal-gnome' not in (p/'niri/autostart.sh').read_text()
assert 'gtklock' in (p/'niri-lock/lock.sh').read_text()
assert not list(p.glob('**/*.jpg')) and not list(p.glob('**/*.png'))
for path in ['waybar/scripts/powermenu.sh','local-bin/powermenu']:
    assert 'niri-lock\n' not in (p/path).read_text()
print('  Upstream visuals retained, dangerous startup removed')
PY

echo '[test] Dry-run installer'
bash install.sh --dry-run >/dev/null

echo '[test] Config staging, replacement, rollback and modification protection'
TMP=$(mktemp -d)
trap 'rm -rf -- "$TMP"' EXIT
HOMECASE="$TMP/home"
mkdir -p "$HOMECASE/.config/niri"
printf '%s\n' 'original user niri' > "$HOMECASE/.config/niri/config.kdl"
python3 scripts/deploy.py install --dry-run --home "$HOMECASE" --replace
[[ $(cat "$HOMECASE/.config/niri/config.kdl") == 'original user niri' ]]
if python3 scripts/deploy.py install --home "$HOMECASE" >"$TMP/err" 2>&1; then
  echo 'ERROR: installer replaced existing settings without opt-in' >&2; exit 1
fi
python3 scripts/deploy.py install --home "$HOMECASE" --replace
[[ -f "$HOMECASE/.local/state/kuhl-base-v1/state.json" ]]
[[ -f "$HOMECASE/.config/niri/autostart.sh" ]]
[[ -f "$HOMECASE/.config/waybar/config.jsonc" ]]
[[ -x "$HOMECASE/.local/bin/powermenu" ]]
[[ ! -e "$HOMECASE/.config/gtk-4.0/assets" ]]
grep -q "$HOMECASE" "$HOMECASE/.config/niri-lock/config.ini"

# Reject modification instead of deleting it during restore.
printf '# user adjustment\n' >> "$HOMECASE/.config/niri/keybinds.kdl"
if python3 scripts/deploy.py restore --home "$HOMECASE" >"$TMP/err" 2>&1; then
  echo 'ERROR: modified user files were not protected' >&2; exit 1
fi
sed -i '$d' "$HOMECASE/.config/niri/keybinds.kdl"
python3 scripts/deploy.py restore --home "$HOMECASE"
[[ $(cat "$HOMECASE/.config/niri/config.kdl") == 'original user niri' ]]
[[ ! -e "$HOMECASE/.config/waybar" ]]

echo '[test] Native Niri validation if installed'
if command -v niri >/dev/null 2>&1; then
  python3 scripts/deploy.py install --dry-run --home "$HOMECASE" --replace --require-niri
else
  echo '  Skipped: Niri is not installed in this environment'
fi

echo 'All portable Kuhl OS base tests passed.'
