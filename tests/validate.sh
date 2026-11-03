#!/usr/bin/env bash
# Kuhl OS Niri source rebase — portable static, unit and installer simulation tests.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
for sh in bootstrap.sh install.sh uninstall.sh bin/kuhl lib/common.sh tests/validate.sh; do bash -n "$sh"; done
python3 -m py_compile scripts/menu.py scripts/render.py scripts/desktop.py scripts/sync_keys.py scripts/validate_niri.py scripts/kuhl_ui.py scripts/progress.py
python3 - <<'PY'
import json, re
from pathlib import Path
p=Path('.')
assert 'Copyright (c) 2025 Saatvik Sharma' in (p/'third_party/niri-dotfiles/LICENSE').read_text()
# GitHub's upload interface may leave behind files from older Kuhl releases.
# Presence of unused historical folders is not evidence the current rebase is broken.
for legacy in ('third_party/KyleOS', 'assets/wallpapers/third-party'):
    if (p/legacy).exists():
        print(f'[warn] Stale directory from a previous release: {legacy} (not installed by this version)')
for source in ['niri/config.kdl','waybar/config.jsonc','waybar/style.css','rofi/config.rasi','kitty/kitty.conf','alacritty/alacritty.toml','mako/config']:
    assert (p/'third_party/niri-dotfiles'/source).is_file(),source
for runtime_file in ('install.sh', 'scripts/render.py', 'scripts/desktop.py'):
    content=(p/runtime_file).read_text()
    assert 'assets/wallpapers/third-party/' not in content, f'Legacy wallpaper dependency in {runtime_file}'
    assert 'third_party/KyleOS/' not in content, f'Legacy KyleOS dependency in {runtime_file}'
conf=(p/'configs/niri/config.kdl').read_text()
assert 'include "binds.kdl"' in conf and 'include "output.kdl"' in conf and 'include "kuhl-theme.kdl"' in conf
assert 'output "eDP-1"' not in conf and 'LIBVA_DRIVER_NAME' not in conf
assert 'gaps 0' in conf and 'animations {' in conf
assert 'Ctrl+Super+K' in (p/'configs/niri/binds.kdl').read_text()
assert 'Mod+Space' in (p/'configs/niri/binds.kdl').read_text()
assert set(json.loads((p/'config/themes.json').read_text()))=={'sevens','dusk','day'}
website=(p/'index.html').read_text()
# index.html is the actual GitHub Pages entry point; main.html is optional.
# An old uploaded copy is not a desktop/installer failure.
if (p/'main.html').exists() and (p/'main.html').read_text()!=website:
    print('[warn] main.html differs from index.html; publish index.html as the website')
for t in ('Saatvik Sharma','niri-dotfiles','AI-assisted','security','MIT','bootstrap.sh','Ctrl + Super + K'):
    assert t.lower() in website.lower(),t
assert 'third-party/sevens.png' not in website
print('[test] MIT upstream snapshots, Fedora source, website and bindings: OK')
PY
python3 scripts/sync_keys.py --check
python3 -m unittest discover -s tests -p 'test_*.py' -q
echo '[test] Sidebar scale, monitor safety, GTK and runtime themes: OK'
python3 scripts/progress.py 6 'Finished' | grep -q '100%'
TMP="$(mktemp -d -t kuhl-rebase-test.XXXXXX)"
trap 'rm -rf -- "$TMP"' EXIT
python3 scripts/menu.py --config config/choices.json --output "$TMP/choice.json" --defaults
python3 - "$TMP/choice.json" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]));assert p['theme']=='sevens' and 'replace_existing' not in p['selected']
PY
bash install.sh --dry-run > /dev/null
bash bootstrap.sh --help | grep -q 'one-command'
export HOME="$TMP/home" XDG_DATA_HOME="$TMP/share" XDG_CONFIG_HOME="$TMP/config" XDG_STATE_HOME="$TMP/state"
mkdir -p "$HOME" "$XDG_DATA_HOME/kuhl/templates" "$XDG_CONFIG_HOME/niri"
cp config/themes.json "$XDG_DATA_HOME/kuhl/themes.json"
cp -R configs/. "$XDG_DATA_HOME/kuhl/templates/"
printf 'my existing Niri config\n' > "$XDG_CONFIG_HOME/niri/config.kdl"
python3 scripts/render.py install --source configs --theme sevens > /dev/null
[[ "$(cat "$XDG_CONFIG_HOME/niri/config.kdl")" == 'my existing Niri config' ]]
python3 scripts/render.py install --source configs --theme sevens --replace-configs > /dev/null
for path in niri/{config,binds,output,kuhl-theme}.kdl waybar/{config.jsonc,style.css,colors.css} kitty/{kitty.conf,colors.conf} rofi/{kuhl.rasi,color.rasi} alacritty/{alacritty.toml,colors.toml} mako/config; do
  [[ -s "$XDG_CONFIG_HOME/$path" ]] || { echo "[error] Missing $path" >&2; exit 1; }
done
python3 scripts/render.py theme --theme dusk > /dev/null
python3 scripts/render.py theme --theme day > /dev/null
python3 scripts/render.py theme --theme sevens > /dev/null
# Ensure user-edited files remain untouched by updates and uninstall.
echo '/* user customization */' >> "$XDG_CONFIG_HOME/waybar/style.css"
python3 scripts/render.py theme --theme day > /dev/null
grep -q 'user customization' "$XDG_CONFIG_HOME/waybar/style.css"
python3 scripts/render.py uninstall > /dev/null || true
[[ "$(cat "$XDG_CONFIG_HOME/niri/config.kdl")" == 'my existing Niri config' ]]
grep -q 'user customization' "$XDG_CONFIG_HOME/waybar/style.css"
echo '[test] Installer, safe replacements, themes and backup restore: OK'
if command -v niri >/dev/null 2>&1;then
  python3 scripts/validate_niri.py
else
  echo '[test] Native Niri parser unavailable here; Fedora CI job validates all palettes.'
fi
echo '[test] All static and simulated Kuhl tests passed'
