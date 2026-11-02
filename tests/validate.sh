#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
for script in install.sh uninstall.sh bin/kuhl lib/common.sh tests/validate.sh; do
  bash -n "$script"
done
python3 -m py_compile scripts/patch-site.py scripts/generate-wallpapers.py scripts/extensions.py
python3 - <<'PY'
from pathlib import Path
from scripts.extensions import profile_items
import struct
for name in ('kuhl-day.png', 'kuhl-dusk.png'):
    p = Path('assets/wallpapers') / name
    data = p.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II', data[16:24]) == (2560,1440)
assert len(profile_items('balanced', Path('config'))) == 5
assert len(profile_items('full', Path('config'))) == 7
assert (Path('assets/themes/Kuhl-Day/gnome-shell/gnome-shell.css').is_file())
assert (Path('assets/themes/Kuhl-Dusk/gnome-shell/gnome-shell.css').is_file())
print('[test] Wallpapers, shell themes, extension profiles: OK')
PY

tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
mkdir -p "$tmp/mockbin" "$tmp/home/.local/bin" "$tmp/data/kuhl/wallpapers"
cp tests/mock-gsettings "$tmp/mockbin/gsettings"
cp lib/common.sh "$tmp/data/kuhl/common.sh"
cp bin/kuhl "$tmp/home/.local/bin/kuhl"
cp assets/wallpapers/kuhl-day.png assets/wallpapers/kuhl-dusk.png "$tmp/data/kuhl/wallpapers/"
chmod +x "$tmp/mockbin/gsettings" "$tmp/home/.local/bin/kuhl"
export KUHL_TEST_STATE="$tmp/mock-values.tsv"
export HOME="$tmp/home" XDG_DATA_HOME="$tmp/data" XDG_STATE_HOME="$tmp/state"
export PATH="$tmp/mockbin:$PATH"
# Emulate an earlier installer change; original user preference should survive
# multiple theme switches, and uninstall should restore that first value.
source "$ROOT/lib/common.sh"
kuhl_set org.gnome.desktop.interface color-scheme "'prefer-dark'"
"$HOME/.local/bin/kuhl" theme day
[[ "$(gsettings get org.gnome.desktop.interface color-scheme)" == "'prefer-light'" ]]
"$HOME/.local/bin/kuhl" theme dusk
[[ "$(gsettings get org.gnome.desktop.interface color-scheme)" == "'prefer-dark'" ]]
"$HOME/.local/bin/kuhl" uninstall
[[ "$(gsettings get org.gnome.desktop.interface color-scheme)" == "'default'" ]]
[[ ! -e "$HOME/.local/bin/kuhl" ]]
[[ -f "$KUHL_SETTINGS" ]]
echo '[test] GSettings save/switch/restore using mock GNOME: OK'
echo '[test] All checks passed'
