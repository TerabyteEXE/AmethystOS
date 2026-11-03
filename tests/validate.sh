#!/usr/bin/env bash
# Static and isolated tests for the release candidate.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
for f in bootstrap.sh install.sh uninstall.sh bin/kuhl lib/common.sh tests/validate.sh; do bash -n "$f"; done
python3 -m py_compile scripts/menu.py scripts/render.py scripts/validate_niri.py scripts/sync_keys.py scripts/kuhl_ui.py scripts/desktop.py scripts/progress.py
python3 - <<'PY'
import json,re,struct,hashlib
from pathlib import Path
p=Path('.')
options=json.loads((p/'config/choices.json').read_text())['choices']
ids=[x['id'] for x in options]
assert len(ids)==len(set(ids))
assert {'core','theme','replace_existing','vicinae'}<=set(ids)
assert not next(x for x in options if x['id']=='replace_existing')['default']
assert not next(x for x in options if x['id']=='vicinae')['default']
assert all(x.get('description') for x in options)
assert set(json.loads((p/'config/themes.json').read_text()))=={'frontier','dyson','puncture','slowend','day','dusk'}
for image in (p/'assets/wallpapers').rglob('*.png'):
    data=image.read_bytes();assert data.startswith(b'\x89PNG\r\n\x1a\n'),image
for name in ('frontier','dyson','puncture','slowend'):
    assert (p/f'assets/wallpapers/third-party/{name}.gif').read_bytes()[:6] in (b'GIF87a',b'GIF89a')
    assert (p/f'assets/wallpapers/third-party/{name}-thumbnail.png').is_file()
    theme=('SlowEnd' if name=='slowend' else name.title())
    for f in ('niri.kdl','rofi.rasi','alacritty.toml','mako.config'):
        assert (p/f'configs/upstream/themes/{theme}/{f}').is_file()
conf=(p/'configs/niri/config.kdl').read_text()
for name in ('layout','autostart','output','binds','window-rules','kuhl-theme'):
    assert f'include "{name}.kdl"' in conf
assert 'custom-shader' in conf and 'geometry-corner-radius 20 0 40 0' in (p/'configs/niri/window-rules.kdl').read_text()
assert not re.search(r'(?m)^\s*include\s+"/etc/niri/',conf)
assert 'HDMI-A-1' not in (p/'configs/niri/output.kdl').read_text().replace('// KyleOS hardcoded HDMI-A-1 and DP-3 outputs, which would break other hardware.','')
bind=(p/'configs/niri/binds.kdl').read_text()
assert 'Ctrl+Super+K' in bind and 'Mod+Space' in bind
assert 'Mod+Ctrl+K     { move-window-up; }' not in bind
assert '/usr/share/scripts/' not in bind and 'yay -Sy' not in bind
assert 'Mod+Shift+K hotkey-overlay-title="Move window up"' in bind
for rel in ('root/etc/niri/config.kdl','root/etc/niri/binds.kdl','root/etc/xdg/waybar/config.jsonc', 'root/usr/share/rofi/themes/thematic.rasi'):
    assert (p/'third_party/KyleOS/original'/rel).is_file()
assert 'listview,' not in (p/'configs/rofi/kuhl.rasi').read_text()
assert 'listview,' not in (p/'configs/rofi/gallery.rasi').read_text()
assert 'listview,' not in (p/'configs/rofi/power.rasi').read_text()
assert '"modules-left": ["pulseaudio", "battery", "niri/language"]' in (p/'configs/waybar/config.jsonc').read_text()
assert 'font-size: 30px' in (p/'configs/waybar/style.css').read_text()
assert 'alacritty' in (p/'install.sh').read_text()
site=(p/'main.html').read_text()
for token in ('KyleOS','PrisonerCoin','AI-assisted','niri','Kuhl OS','copyInstall','bootstrap.sh','CC BY-NC-SA','GitHub'):
    assert token.lower() in site.lower(),token
assert (p/'main.html').read_bytes()==(p/'index.html').read_bytes()
assert 'MIT License' in (p/'third_party/KyleOS-MIT.txt').read_text()
assert 'CC BY-NC-SA' in (p/'docs/CREDITS.md').read_text()
print('[test] Direct KyleOS config port, images, website, license, manifest: OK')
PY
python3 scripts/sync_keys.py --check
python3 -m unittest discover -s tests -p 'test_*.py' -q
echo '[test] Bar, display safety and GTK restoration unit tests: OK'
python3 scripts/progress.py 6 'Finished' | grep -q '100%'
echo '[test] Updated shortcut guide and installer progress display: OK'
OUT="$(mktemp)"
python3 scripts/menu.py --config config/choices.json --output "$OUT" --defaults
python3 - "$OUT" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]));assert x['theme']=='frontier'; assert {'core','theme'}<=set(x['selected']); assert 'replace_existing' not in x['selected']
PY
rm -f "$OUT"
bash install.sh --dry-run >/dev/null
bash bootstrap.sh --help | grep -q 'one-command'
echo '[test] Installer options, dry-run, bootstrap help: OK'
TMP="$(mktemp -d -t kuhl-v1-test.XXXXXX)"
trap 'rm -rf -- "$TMP"' EXIT
export HOME="$TMP/home" XDG_CONFIG_HOME="$TMP/config" XDG_DATA_HOME="$TMP/data" XDG_STATE_HOME="$TMP/state"
mkdir -p "$HOME" "$XDG_DATA_HOME/kuhl/templates" "$XDG_CONFIG_HOME/niri"
cp config/themes.json "$XDG_DATA_HOME/kuhl/themes.json"
cp -R configs/. "$XDG_DATA_HOME/kuhl/templates/"
printf 'my own niri config\n' > "$XDG_CONFIG_HOME/niri/config.kdl"
python3 scripts/render.py install --source configs --theme frontier > "$TMP/install-output"
[[ "$(cat "$XDG_CONFIG_HOME/niri/config.kdl")" == 'my own niri config' ]]
for f in niri/{layout,autostart,output,binds,window-rules,kuhl-theme}.kdl waybar/{config.jsonc,style.css} alacritty/alacritty.toml rofi/{kuhl,gallery,power,color}.rasi mako/config kitty/{kitty.conf,colors.conf} gtk-3.0/settings.ini gtk-4.0/settings.ini; do
  [[ -f "$XDG_CONFIG_HOME/$f" ]] || { echo "Missing installed $f" >&2; exit 1; }
done
# KyleOS themes are the base; Kuhl safely overrides fonts and system integration.
grep -q 'JetBrains Mono' "$XDG_CONFIG_HOME/alacritty/alacritty.toml"
grep -q 'size = 12' "$XDG_CONFIG_HOME/alacritty/alacritty.toml"
diff -u <(sed 's/urgent-color "ff0000"/urgent-color "#ff0000"/' configs/upstream/themes/Frontier/niri.kdl) "$XDG_CONFIG_HOME/niri/kuhl-theme.kdl"
cmp -s "$XDG_CONFIG_HOME/rofi/color.rasi" configs/upstream/themes/Frontier/rofi.rasi
cmp -s "$XDG_CONFIG_HOME/mako/config" configs/upstream/themes/Frontier/mako.config
python3 scripts/render.py install --source configs --theme dusk --replace-configs >/dev/null
[[ "$(head -1 "$XDG_CONFIG_HOME/niri/config.kdl")" == *KUHL-MANAGED* ]]
python3 scripts/render.py theme --theme dyson >/dev/null
diff -u <(sed 's/urgent-color "ff0000"/urgent-color "#ff0000"/' configs/upstream/themes/Dyson/niri.kdl) "$XDG_CONFIG_HOME/niri/kuhl-theme.kdl"
grep -q 'JetBrains Mono' "$XDG_CONFIG_HOME/alacritty/alacritty.toml"
# Appearance must now change the Waybar, GTK, terminal, and launcher together.
python3 - "$XDG_CONFIG_HOME/waybar/config.jsonc" <<'PYBAR'
import json,sys
p=json.load(open(sys.argv[1]))
assert 'custom/close' in p['modules-right']
assert 'custom/settings' in p['modules-right']
assert p['height']==34 and p['position']=='top'
assert p['custom/close']['on-click']=='niri msg action close-window'
PYBAR
grep -q 'Adwaita-dark' "$XDG_CONFIG_HOME/gtk-3.0/settings.ini"
grep -q '#73eff7' "$XDG_CONFIG_HOME/waybar/style.css"
# Functional interface/bar scaling, position, module and display controls.
python3 scripts/desktop.py bar scale 125 >/dev/null
python3 scripts/desktop.py bar position bottom >/dev/null
python3 scripts/desktop.py bar module close off >/dev/null
python3 scripts/desktop.py ui scale 150 >/dev/null
python3 - "$XDG_CONFIG_HOME/waybar/config.jsonc" "$XDG_CONFIG_HOME/alacritty/alacritty.toml" <<'PYBAR'
import json,sys
p=json.load(open(sys.argv[1]))
assert p['height']==42 and p['position']=='bottom'
assert 'custom/close' not in p['modules-right']
assert 'size = 18' in open(sys.argv[2]).read()
PYBAR
python3 scripts/desktop.py bar reset >/dev/null
python3 scripts/desktop.py ui reset >/dev/null
python3 scripts/desktop.py display scale HDMI-A-1 1.25 >/dev/null
grep -q 'scale 1.25' "$XDG_CONFIG_HOME/niri/output.kdl"
python3 scripts/desktop.py display reset >/dev/null
! grep -q 'scale 1.25' "$XDG_CONFIG_HOME/niri/output.kdl"
# Never overwrite user manual edits, even on theme change.
echo '/* custom user edit */' >> "$XDG_CONFIG_HOME/waybar/style.css"
python3 scripts/render.py theme --theme slowend >/dev/null
grep -q 'custom user edit' "$XDG_CONFIG_HOME/waybar/style.css"
python3 scripts/render.py uninstall >/dev/null || true
[[ "$(cat "$XDG_CONFIG_HOME/niri/config.kdl")" == 'my own niri config' ]]
grep -q 'custom user edit' "$XDG_CONFIG_HOME/waybar/style.css"
echo '[test] Six themes, original source equivalence, backup/restore, user edits: OK'
install -m 644 config/keys.json "$XDG_DATA_HOME/kuhl/keys.json"
bash "$ROOT/bin/kuhl" wallpaper set "$ROOT/assets/wallpapers/kuhl-day.png" >/dev/null
[[ "$(cat "$XDG_STATE_HOME/kuhl/wallpaper-choice")" == custom ]]
bash "$ROOT/bin/kuhl" wallpaper reset >/dev/null
[[ "$(cat "$XDG_STATE_HOME/kuhl/wallpaper-choice")" == auto ]]
bash "$ROOT/bin/kuhl" keys | grep -q 'Ctrl + Super + K'
echo '[test] Wallpaper CLI and keyboard guide: OK'
if command -v niri >/dev/null 2>&1; then
 python3 scripts/validate_niri.py
else
 echo '[test] SKIPPED native Fedora/Niri parser validation (niri unavailable on this test host)'
fi
echo '[test] All Kuhl OS v1 RC checks passed'
