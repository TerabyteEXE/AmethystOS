#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
for script in bootstrap.sh install.sh uninstall.sh bin/kuhl lib/common.sh scripts/gdm-brand.sh tests/validate.sh; do
  bash -n "$script"
done
python3 -m py_compile scripts/extensions.py scripts/menu.py scripts/capture.py
python3 - <<'PY'
from pathlib import Path
from scripts.extensions import profile_items
import re
version_pattern = r'GNOME\s+Shell\s+(\d+)(?:\.\d+)*'
for ver,expected in [('GNOME Shell 50', '50'),('GNOME Shell 50.5','50'), ('GNOME Shell 50.3.1','50')]:
    assert re.search(version_pattern,ver,re.I).group(1) == expected
import struct
for name in ('kuhl-default.png','kuhl-day.png', 'kuhl-dusk.png'):
    p = Path('assets/wallpapers') / name
    data = p.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II', data[16:24]) == (2560,1440)
assert len(profile_items('balanced', Path('config'))) == 8
assert len(profile_items('full', Path('config'))) == 9
assert 'ArcMenu' in Path('config/extensions.tsv').read_text()
assert 'Blur my Shell' in Path('config/extensions.tsv').read_text()
assert 'gnome-shell-extension-background-logo' in Path('install.sh').read_text()
assert 'Spotlight launcher' in Path('config/extensions.tsv').read_text()
assert 'spotlight@nin' in Path('config/choices.json').read_text()
assert "['<Super>space']" in Path('install.sh').read_text()
assert (Path('assets/themes/Kuhl-Day/gnome-shell/gnome-shell.css').is_file())
assert (Path('assets/themes/Kuhl-Dusk/gnome-shell/gnome-shell.css').is_file())
from json import loads
choices = loads(Path('config/choices.json').read_text())['choices']
ids = {item['id'] for item in choices}
assert len(ids) == len(choices)
assert {'extension_manager','kuhl_look','gnome_tweaks','reboot','brand_gdm','spotlight','arcmenu','background_logo'} <= ids
assert all(item.get('description') for item in choices)
print('[test] Wallpapers, shell themes, extension profiles and TUI manifest: OK')
PY

choice_file="$(mktemp)"
python3 scripts/menu.py --config config/choices.json --output "$choice_file" --defaults
python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["theme"] == "dusk"; assert "extension_manager" in r["selected"]; assert "brand_gdm" not in r["selected"]' "$choice_file"
rm -f "$choice_file"
echo '[test] Default menu selection serialization: OK'
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
mkdir -p "$tmp/mockbin" "$tmp/home/.local/bin" "$tmp/data/kuhl/wallpapers"
cp tests/mock-gsettings "$tmp/mockbin/gsettings"
cp lib/common.sh "$tmp/data/kuhl/common.sh"
cp bin/kuhl "$tmp/home/.local/bin/kuhl"
cp assets/wallpapers/kuhl-default.png assets/wallpapers/kuhl-day.png assets/wallpapers/kuhl-dusk.png "$tmp/data/kuhl/wallpapers/"
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
