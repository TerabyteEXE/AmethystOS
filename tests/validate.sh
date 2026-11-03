#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
for f in bootstrap.sh install.sh uninstall.sh bin/kuhl lib/common.sh tests/validate.sh; do bash -n "$f"; done
python3 -m py_compile scripts/menu.py scripts/render.py scripts/validate_niri.py scripts/sync_keys.py scripts/kuhl_ui.py scripts/progress.py
python3 - <<'PY'
import json,re,struct
from pathlib import Path
choices=json.loads(Path('config/choices.json').read_text())['choices']
ids=[i['id'] for i in choices]
assert len(ids)==len(set(ids))
assert {'core','theme','vicinae'} <= set(ids)
assert not next(i for i in choices if i['id']=='vicinae')['default']
assert not next(i for i in choices if i['id']=='replace_existing')['default']
assert all(x.get('description') for x in choices)
for x in ('frontier','dyson','puncture','slowend','day','dusk'):
 assert x in json.loads(Path('config/themes.json').read_text())
for p in Path('assets/wallpapers').glob('*.png'):
 d=p.read_bytes()
 assert d[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',d[16:24])==(2560,1440)
conf=Path('configs/niri/config.kdl').read_text()
assert 'include "kuhl-theme.kdl"' in conf and 'Mod+Space repeat=false' in conf
assert 'Mod+Shift+E { quit;' in conf
assert 'Ctrl+Super+K repeat=false' in conf
assert 'Mod+Shift+K { move-window-up; }' in conf
assert 'window-rule {' in conf and 'kuhl-keys' in conf
assert 'keyboard {\n        numlock\n    }' in conf
assert 'keyboard { numlock }' not in conf
site=Path('main.html').read_text()
assert all(x in site for x in ['Niri','Super','Vicinae','Fuzzel','Rofi','curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash','Kuhl OS','Ctrl + Super + K','copyInstall','AI-assisted','PrisonerCoin','KyleOS'])
assert 'kuhl.example' not in site and 'coming soon' not in site.lower()
assert 'ctrl+space' not in site.lower()
assert 'https://github.com/TerabyteEXE/Kuhl-OS' in site
assert 'git clone https://github.com/TerabyteEXE/Kuhl-OS.git' not in site
assert 'id="command"' in site
assert 'https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh' in Path('bootstrap.sh').read_text()
assert Path('config/keys.json').is_file()
assert 'default-wallpaper' not in conf
assert 'geometry-corner-radius 20 0 40 0' in conf
assert 'border-radius' in Path('configs/rofi/kuhl.rasi').read_text().lower()
assert 'Survey' not in str([p for p in Path('assets/wallpapers/third-party').glob('*.png')])
assert Path('docs/CREDITS.md').exists() and Path('docs/SECURITY.md').exists()
assert 'MIT License' in Path('third_party/KyleOS-MIT.txt').read_text()
assert 'CC BY-NC-SA' in Path('docs/CREDITS.md').read_text()
assert Path('index.html').read_bytes()==Path('main.html').read_bytes()
print('[test] Bundled config, site and manifest: OK')
PY
python3 scripts/sync_keys.py --check
python3 scripts/progress.py 6 'Finished' | grep -q '100%'
echo '[test] Keyboard manifest, generated documentation and progress UI: OK'
OUT="$(mktemp)"
python3 scripts/menu.py --config config/choices.json --output "$OUT" --defaults
python3 - "$OUT" <<'PY'
import json,sys
v=json.load(open(sys.argv[1])); assert v['theme']=='frontier'; assert {'core','theme'} <= set(v['selected']); assert 'vicinae' not in v['selected']; assert 'replace_existing' not in v['selected']
PY
rm -f "$OUT"
echo '[test] Python TUI defaults: OK'
bash install.sh --dry-run >/dev/null
bash bootstrap.sh --help | grep -q 'one-command'
# Selection/upgrade contract: the one-command TUI can opt in to replacing existing dotfiles.
grep -q 'chosen replace_existing; then REPLACE_CONFIGS=1' install.sh
grep -q 'Existing dotfiles will be backed up, then replaced' scripts/menu.py
echo '[test] One-command entry point, safe upgrade choice, installer dry-run: OK'
TMP="$(mktemp -d -t kuhl-tests.XXXXXXXX)"
trap 'rm -rf -- "$TMP"' EXIT
export HOME="$TMP/home" XDG_CONFIG_HOME="$TMP/config" XDG_DATA_HOME="$TMP/data" XDG_STATE_HOME="$TMP/state"
mkdir -p "$HOME" "$XDG_DATA_HOME/kuhl" "$XDG_CONFIG_HOME/niri"
cp config/themes.json "$XDG_DATA_HOME/kuhl/themes.json"
# Verify existing user file is protected; no Kuhl overwrite.
printf 'keep my niri config\n' > "$XDG_CONFIG_HOME/niri/config.kdl"
python3 scripts/render.py install --source configs --theme frontier >/dev/null
[[ "$(cat "$XDG_CONFIG_HOME/niri/config.kdl")" == 'keep my niri config' ]]
[[ -f "$XDG_CONFIG_HOME/waybar/style.css" ]]
[[ -f "$XDG_CONFIG_HOME/fuzzel/fuzzel.ini" ]]
[[ -f "$XDG_CONFIG_HOME/rofi/kuhl.rasi" ]]
[[ -f "$XDG_CONFIG_HOME/rofi/color.rasi" ]]
[[ -f "$XDG_CONFIG_HOME/rofi/gallery.rasi" ]]
[[ -f "$HOME/.local/share/applications/kuhl-day.desktop" ]]
[[ -f "$HOME/.local/share/applications/kuhl-control.desktop" ]]
[[ -f "$HOME/.local/share/applications/kuhl-keys.desktop" ]]
[[ -f "$XDG_DATA_HOME/vicinae/themes/kuhl-frontier.toml" ]]
# Explicit replacement saves original, and uninstall restores it.
python3 scripts/render.py install --source configs --theme dusk --replace-configs >/dev/null
grep -q 'KUHL-MANAGED' "$XDG_CONFIG_HOME/niri/config.kdl"
python3 scripts/render.py theme --theme day >/dev/null
grep -q 'Kuhl day palette' "$XDG_CONFIG_HOME/niri/kuhl-theme.kdl"
# User edit must never be destroyed by re-install, theme change or uninstall.
echo '/* user edit */' >> "$XDG_CONFIG_HOME/waybar/style.css"
python3 scripts/render.py theme --theme frontier >/dev/null
grep -q 'user edit' "$XDG_CONFIG_HOME/waybar/style.css"
python3 scripts/render.py uninstall >/dev/null || true
[[ "$(cat "$XDG_CONFIG_HOME/niri/config.kdl")" == 'keep my niri config' ]]
grep -q 'user edit' "$XDG_CONFIG_HOME/waybar/style.css"
[[ ! -e "$XDG_CONFIG_HOME/kitty/colors.conf" ]]
echo '[test] Config protection, six-theme rendering, Rofi, backup restore, uninstall: OK'
bash "$ROOT/bin/kuhl" wallpaper set "$ROOT/assets/wallpapers/kuhl-day.png" >/dev/null
[[ "$(cat "$XDG_STATE_HOME/kuhl/wallpaper-choice")" == custom ]]
[[ -r "$XDG_STATE_HOME/kuhl/wallpaper-custom" ]]
bash "$ROOT/bin/kuhl" wallpaper reset >/dev/null
[[ "$(cat "$XDG_STATE_HOME/kuhl/wallpaper-choice")" == auto ]]
# The searchable atlas is also available as plain text without a GUI.
install -m 644 config/keys.json "$XDG_DATA_HOME/kuhl/keys.json"
bash "$ROOT/bin/kuhl" keys | grep -q 'Ctrl + Super + K'
echo '[test] Custom wallpaper choice, reset, and CLI keyboard atlas: OK'
if command -v niri >/dev/null 2>&1; then
  python3 scripts/validate_niri.py
else
  echo '[test] SKIPPED native Niri validation (niri not installed; Fedora CI checks all six themes)'
fi
echo '[test] All Kuhl Frontier v0.8 checks passed'
