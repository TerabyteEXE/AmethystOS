#!/usr/bin/env bash
# Kuhl OS 0.3. Installer for regular Fedora Workstation (GNOME), not an OS replacement.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

DEFAULTS=0
DRY_RUN=0
NO_REBOOT=0
usage() {
  cat <<'TXT'
Kuhl OS v0.3 — interactive Fedora desktop installer
Usage: bash install.sh [--defaults] [--dry-run] [--no-reboot]
  (no flags)  Full-screen text UI: pick extensions, apps and system options.
  --defaults  Use recommended selections without a menu (still prompts before reboot).
  --dry-run   Preview recommended selection; do not install anything.
  --no-reboot Never reboot, even if selected in the menu.
Run as your logged-in normal user in Fedora Workstation GNOME, NOT sudo.
TXT
}
while (($#)); do
  case "$1" in
    --defaults) DEFAULTS=1;;
    --dry-run) DRY_RUN=1; DEFAULTS=1; NO_REBOOT=1;;
    --no-reboot) NO_REBOOT=1;;
    -h|--help) usage; exit 0;;
    *) printf 'Unknown flag: %s\n' "$1" >&2; usage; exit 2;;
  esac
  shift
done
[[ $(id -u) -ne 0 ]] || { echo 'Do NOT run the whole script as root. Sudo is used only when required.' >&2; exit 1; }
[[ $(uname -m) == x86_64 ]] || { echo 'Kuhl currently supports x86_64 systems.' >&2; exit 1; }
[[ -f /etc/os-release ]] || { echo 'Cannot read /etc/os-release.' >&2; exit 1; }
# shellcheck disable=SC1091
source /etc/os-release
[[ ${ID:-} == fedora ]] || { echo 'Regular Fedora Workstation is required.' >&2; exit 1; }
[[ ! -e /run/ostree-booted ]] || { echo 'Fedora Silverblue/Kinoite use rpm-ostree, not this installer.' >&2; exit 1; }
if (( ! DRY_RUN )); then
  [[ ${XDG_CURRENT_DESKTOP:-} == *GNOME* ]] || { echo 'Log into Fedora GNOME before installing.' >&2; exit 1; }
  command -v gsettings >/dev/null || { echo 'gsettings is missing.' >&2; exit 1; }
  command -v dnf >/dev/null || { echo 'dnf is missing.' >&2; exit 1; }
fi
[[ -f "$ROOT/config/choices.json" && -f "$ROOT/scripts/menu.py" ]] || { echo 'Incomplete repository checkout. Get the full ZIP.' >&2; exit 1; }
[[ -f "$ROOT/assets/wallpapers/kuhl-day.png" && -f "$ROOT/assets/wallpapers/kuhl-dusk.png" ]] || { echo 'Required wallpapers missing.' >&2; exit 1; }
command -v python3 >/dev/null || { echo 'Python 3 required.' >&2; exit 1; }

TMP="$(mktemp -d -t kuhl-install.XXXXXXXX)"
trap 'rm -rf -- "$TMP"' EXIT
if (( DEFAULTS )); then
  python3 "$ROOT/scripts/menu.py" --config "$ROOT/config/choices.json" --output "$TMP/choices.json" --defaults
else
  python3 "$ROOT/scripts/menu.py" --config "$ROOT/config/choices.json" --output "$TMP/choices.json" || { echo 'Installer cancelled. No changes made.'; exit 2; }
fi
# Parse ONLY IDs present in the repository manifest; no user-entered shell code.
mapfile -t SELECTED < <(python3 - "$TMP/choices.json" "$ROOT/config/choices.json" <<'PY'
import json, sys
r=json.load(open(sys.argv[1])); options=json.load(open(sys.argv[2]))['choices']
valid={p['id'] for p in options}; chosen=set(r['selected'])
if not chosen <= valid: raise SystemExit('Unknown menu choice')
if not all(p['id'] in chosen for p in options if p.get('required')): raise SystemExit('Missing required choice')
for x in sorted(chosen): print(x)
PY
)
THEME="$(python3 - "$TMP/choices.json" <<'PY'
import json,sys
s=json.load(open(sys.argv[1]))['theme']
assert s in ('day','dusk')
print(s)
PY
)"
chosen() { local name="$1" i; for i in "${SELECTED[@]}"; do [[ "$i" != "$name" ]] || return 0; done; return 1; }
if (( DRY_RUN )); then
  printf '\nDRY RUN — Kuhl OS install: %s theme\n' "$THEME"
  printf '  %s\n' "${SELECTED[@]}"
  printf 'Nothing changed. Run without --dry-run to launch the text UI.\n'
  exit 0
fi

mkdir -p "$KUHL_STATE" "$KUHL_DATA" "$HOME/.local/bin"
LOG="$KUHL_STATE/install.log"
# Save a log, but keep output visible. No passwords, tokens or personal environment dumps.
exec > >(tee -a "$LOG") 2>&1
printf '\n✳ KUHL OS 0.3 — APPLYING YOUR SETUP\n'
printf 'Fedora %s — theme %s — %d options\n' "${VERSION_ID:-unknown}" "$THEME" "${#SELECTED[@]}"
if [[ -r /proc/meminfo ]]; then
  mem_kib="$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)"
  (( mem_kib >= 7*1024*1024 )) || kuhl_warn 'Below the recommended ~8 GB RAM. Visual effects might feel sluggish.'
fi
printf '\n[1/6] Installing Fedora base packages...\n'
# GNOME User Themes is a Fedora RPM, no third-party shell patches.
sudo -v
sudo dnf install -y \
  flatpak gnome-tweaks gnome-extensions-app gnome-shell-extension-user-theme \
  papirus-icon-theme papirus-icon-theme-dark papirus-icon-theme-light \
  adw-gtk3-theme google-noto-sans-fonts jetbrains-mono-fonts

printf '\n[2/6] Installing Extension Manager and optional applications...\n'
# Flathub addition is disclosed in TUI and only affects the current user.
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
# Packages are from the local checked-out manifest, not arbitrary menu text.
mapfile -t FLATPAKS < <(python3 - "$ROOT/config/choices.json" "$TMP/choices.json" <<'PY'
import json,sys
items=json.load(open(sys.argv[1]))['choices']; selection=set(json.load(open(sys.argv[2]))['selected'])
for p in items:
 if p['id'] in selection and p['type']=='flatpak': print(p['value'])
PY
)
ISSUES=0
for app in "${FLATPAKS[@]}"; do
  if flatpak info --user "$app" >/dev/null 2>&1; then
    printf 'Already installed: %s\n' "$app"
  elif ! flatpak install --user --noninteractive -y flathub "$app"; then
    printf 'FAILED Flatpak: %s (see %s)\n' "$app" "$LOG"
    ISSUES=$((ISSUES+1))
  fi
done

printf '\n[3/6] Applying Kuhl wallpapers, shell theme and settings...\n'
mkdir -p "$KUHL_DATA/wallpapers" "$KUHL_DATA/config" "$KUHL_APPS" "$HOME/.themes"
install -m 644 "$ROOT/assets/wallpapers/kuhl-day.png" "$KUHL_DATA/wallpapers/kuhl-day.png"
install -m 644 "$ROOT/assets/wallpapers/kuhl-dusk.png" "$KUHL_DATA/wallpapers/kuhl-dusk.png"
install -m 644 "$ROOT/lib/common.sh" "$KUHL_DATA/common.sh"
install -m 755 "$ROOT/bin/kuhl" "$KUHL_BIN"
install -m 755 "$ROOT/scripts/extensions.py" "$KUHL_DATA/extensions.py"
install -m 755 "$ROOT/scripts/gdm-brand.sh" "$KUHL_DATA/gdm-brand.sh"
install -m 644 "$ROOT/config/extensions.tsv" "$KUHL_DATA/config/extensions.tsv"
install -m 644 "$ROOT/config/effects.tsv" "$KUHL_DATA/config/effects.tsv"
install -m 644 "$ROOT/config/choices.json" "$KUHL_DATA/config/choices.json"
for name in Day Dusk; do
  target="$HOME/.themes/Kuhl-$name"
  if [[ -d "$target" && ! -f "$target/.kuhl-owned" ]]; then
    kuhl_warn "A preexisting theme at $target was not replaced."
    continue
  fi
  mkdir -p "$target/gnome-shell"
  install -m 644 "$ROOT/assets/themes/Kuhl-$name/gnome-shell/gnome-shell.css" "$target/gnome-shell/gnome-shell.css"
  touch "$target/.kuhl-owned"
done

# Fedora package may not appear in GNOME's process until fresh login; pre-register enabled UUID.
user_uuid='user-theme@gnome-shell-extensions.gcampax.github.com'
if ! gnome-extensions list --enabled 2>/dev/null | grep -Fxq "$user_uuid"; then
  if gnome-extensions enable "$user_uuid" 2>/dev/null; then
    printf '%s\n' "$user_uuid" > "$KUHL_STATE/enabled-user-theme.txt"
  else
    kuhl_warn 'User Themes may not activate until reboot.'
  fi
fi
kuhl_set org.gnome.desktop.background picture-uri "$(kuhl_quote "file://$KUHL_DATA/wallpapers/kuhl-day.png")"
kuhl_set org.gnome.desktop.background picture-uri-dark "$(kuhl_quote "file://$KUHL_DATA/wallpapers/kuhl-dusk.png")"
kuhl_set org.gnome.desktop.interface accent-color "'orange'"
kuhl_set org.gnome.desktop.interface cursor-theme "'Adwaita'"
kuhl_set org.gnome.desktop.interface font-name "'Noto Sans 11'"
kuhl_set org.gnome.desktop.interface document-font-name "'Noto Sans 11'"
kuhl_set org.gnome.desktop.interface monospace-font-name "'JetBrains Mono 11'"
kuhl_set org.gnome.desktop.wm.preferences titlebar-font "'Noto Sans Bold 11'"
if kuhl_key_exists org.gnome.shell.keybindings toggle-overview; then
  existing="$(gsettings get org.gnome.shell.keybindings toggle-overview)"
  extra="$(python3 - "$existing" <<'PY'
import ast,sys
s=sys.argv[1]
if s.startswith('@as '): s=s[4:]
keys=ast.literal_eval(s)
if '<Control>space' not in keys: keys.insert(0, '<Control>space')
print(repr(keys))
PY
)"
  kuhl_set org.gnome.shell.keybindings toggle-overview "$extra"
fi
kuhl_theme "$THEME"
for theme in day dusk; do
  cat > "$KUHL_APPS/kuhl-$theme.desktop" <<ENTRY
[Desktop Entry]
Type=Application
Name=Kuhl ${theme^}
Comment=Switch to the Kuhl ${theme^} color palette
Exec=$KUHL_BIN theme $theme
Icon=preferences-desktop-theme
Terminal=false
Categories=Settings;DesktopSettings;
ENTRY
done

printf '\n[4/6] Installing GNOME Shell extensions...\n'
# Only selected extension UUIDs from the reviewed project catalog are installed.
mkdir -p "$TMP/extension-config"
python3 - "$ROOT/config" "$ROOT/config/choices.json" "$TMP/choices.json" "$TMP/extension-config/extensions.tsv" <<'PY'
import json,sys
from pathlib import Path
source=Path(sys.argv[1]); meta=json.load(open(sys.argv[2]))['choices']; selected=set(json.load(open(sys.argv[3]))['selected'])
ids={x['value'] for x in meta if x['type']=='extension' and x['id'] in selected}
records=[]
for file in ('extensions.tsv','effects.tsv'):
 for line in (source/file).read_text().splitlines():
  if line and not line.startswith('#') and line.split('\t')[1] in ids: records.append(line)
if len(records)!=len(ids): raise SystemExit('Missing extension definition for selected extension')
Path(sys.argv[4]).write_text('\n'.join(records)+'\n')
PY
: > "$TMP/extension-config/effects.tsv"
if [[ -s "$TMP/extension-config/extensions.tsv" ]]; then
  if ! python3 "$KUHL_DATA/extensions.py" install --profile balanced --config "$TMP/extension-config"; then
    ISSUES=$((ISSUES+1))
    kuhl_warn 'The extension installer reported an error; check Extension Manager after reboot.'
  fi
fi
# Installing a ZIP on running Wayland GNOME may not activate it right away.
# Request activation in persistent GNOME settings for the next login.
mapfile -t ADDED < <(python3 - "$ROOT/config/choices.json" "$TMP/choices.json" <<'PY'
import json,sys
items=json.load(open(sys.argv[1]))['choices']; selected=set(json.load(open(sys.argv[2]))['selected'])
for p in items:
 if p['id'] in selected and p['type']=='extension': print(p['value'])
PY
)
# Only include installed extensions, never unsupported ones that failed to download.
PRESENT=( "$user_uuid" )
for uuid in "${ADDED[@]}"; do
  if [[ -d "$HOME/.local/share/gnome-shell/extensions/$uuid" ]] || gnome-extensions info "$uuid" >/dev/null 2>&1; then
    PRESENT+=("$uuid")
  fi
done
if kuhl_key_exists org.gnome.shell enabled-extensions; then
  current="$(gsettings get org.gnome.shell enabled-extensions)"
  merged="$(python3 - "$current" "${PRESENT[@]}" <<'PY'
import ast,sys
value=sys.argv[1]
if value.startswith('@as '): value=value[4:]
a=ast.literal_eval(value)
if not isinstance(a,list): raise ValueError('Expected GNOME extension list')
for uuid in sys.argv[2:]:
 if uuid not in a:a.append(uuid)
print(repr(a))
PY
)"
  kuhl_set org.gnome.shell enabled-extensions "$merged"
fi

printf '\n[5/6] Applying optional GDM login branding...\n'
if chosen brand_gdm; then
  if ! bash "$ROOT/scripts/gdm-brand.sh" install "$ROOT/assets/branding/kuhl-logo.svg"; then
    ISSUES=$((ISSUES+1))
    kuhl_warn 'GDM logo could not be applied; this does not block GNOME login.'
  fi
else
  printf 'Login logo not selected. GDM configuration unchanged.\n'
fi

printf '\n[6/6] Finalizing and checking...\n'
cp -f "$TMP/choices.json" "$KUHL_STATE/last-selection.json"
chmod 600 "$KUHL_STATE/last-selection.json"
# Do not treat optional missing extensions as proof of a successful complete desktop.
"$KUHL_BIN" doctor || kuhl_warn 'A doctor check needs attention; inspect the log and Extension Manager.'
printf '\nKuhl OS setup finished. Issues reported: %d\n' "$ISSUES"
printf 'Log: %s\n' "$LOG"
printf 'Desktop configuration takes effect fully after sign-out/reboot.\n'
printf 'Manage extensions using Extension Manager after the next login.\n'
if (( ISSUES > 0 )); then
  printf 'Some optional installations failed. Review the log; reboot is not automatic when failures occurred.\n'
  exit 1
fi
if chosen reboot && (( ! NO_REBOOT )); then
  if [[ -t 0 ]]; then
    printf '\nReboot now to finish Kuhl setup? [Y/n] '
    IFS= read -r answer || answer='n'
    if [[ -z "$answer" || "$answer" == y || "$answer" == Y ]]; then
      printf 'Rebooting... save any work first (Ctrl+C to stop within 5 seconds).\n'
      sleep 5
      systemctl reboot || kuhl_warn 'Could not trigger reboot. Please reboot manually.'
    else
      printf 'Reboot postponed. Restart your computer when convenient.\n'
    fi
  else
    printf 'No interactive terminal; please reboot manually.\n'
  fi
else
  printf 'Reboot disabled in this run; restart later to load the installed extensions.\n'
fi
