#!/usr/bin/env bash
# KUHL-MANAGED — Kuhl OS 0.8, Fedora + Niri edition (not a Linux distro/ISO).
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"
DEFAULTS=0
DRY_RUN=0
REPLACE_CONFIGS=0
NO_REBOOT=1
usage() {
  cat <<'TXT'
Kuhl OS 0.8 — Fedora Workstation + Niri
Recommended: curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
Internal/advanced: bash install.sh [--defaults] [--dry-run] [--replace-configs] [--no-reboot]
  --defaults         Use default choices without opening the text UI.
  --dry-run          Preview choices; never installs anything (works on any OS).
  --replace-configs  Advanced override: back up and replace desktop configurations.
                     For normal use, select this option in the terminal menu instead.
  --no-reboot        Retained for compatibility. Kuhl no longer reboots for you.

Run as your normal Fedora user, not with sudo. GNOME is kept as a fallback.
Vicinae uses the third-party quadratech188/vicinae COPR and is off by default.
TXT
}
while (($#)); do
  case "$1" in
    --defaults) DEFAULTS=1;;
    --dry-run) DRY_RUN=1; DEFAULTS=1;;
    --replace-configs) REPLACE_CONFIGS=1;;
    --no-reboot) NO_REBOOT=1;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown option: $1" >&2; usage; exit 2;;
  esac
  shift
done
for f in config/choices.json config/themes.json scripts/menu.py scripts/render.py scripts/kuhl_ui.py scripts/progress.py config/keys.json configs/niri/config.kdl assets/wallpapers/kuhl-default.png; do
  [[ -f "$ROOT/$f" ]] || { echo "Missing repository file: $f" >&2; exit 1; }
done
command -v python3 >/dev/null || { echo 'Python 3 required.' >&2; exit 1; }
TMP="$(mktemp -d -t kuhl-install.XXXXXXXX)"
trap 'rm -rf -- "$TMP"' EXIT
if (( DEFAULTS )); then
  python3 "$ROOT/scripts/menu.py" --config "$ROOT/config/choices.json" --output "$TMP/choices.json" --defaults
else
  python3 "$ROOT/scripts/menu.py" --config "$ROOT/config/choices.json" --output "$TMP/choices.json" || { echo 'Cancelled without applying changes.'; exit 2; }
fi
# Validate IDs and get trusted values from the bundled repository manifest only.
mapfile -t SELECTED < <(python3 - "$TMP/choices.json" "$ROOT/config/choices.json" <<'PY'
import json,sys
choice=json.load(open(sys.argv[1])); options=json.load(open(sys.argv[2]))['choices']
valid={item['id'] for item in options}
selected=set(choice['selected'])
if not selected <= valid: raise SystemExit('Unknown selected option')
if not {p['id'] for p in options if p.get('required')} <= selected: raise SystemExit('Required option missing')
for item in sorted(selected): print(item)
PY
)
THEME="$(python3 - "$TMP/choices.json" "$ROOT/config/themes.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1]))['theme']
assert v in json.load(open(sys.argv[2]))
print(v)
PY
)"
chosen() { local x; for x in "${SELECTED[@]}"; do [[ "$x" != "$1" ]] || return 0; done; return 1; }
# A single public command launches this menu; upgrades can be selected here, no extra flags needed.
if chosen replace_existing; then REPLACE_CONFIGS=1; fi
if (( DRY_RUN )); then
  echo 'KUHL OS — DRY RUN (nothing changed)'
  echo "  Theme: $THEME"
  printf '  Option: %s\n' "${SELECTED[@]}"
  (( REPLACE_CONFIGS == 0 )) || echo '  Replace existing configs: yes, after backups'
  echo '  Fedora Niri + Rofi/Fuzzel/Waybar/Kitty/Mako: required'
  chosen vicinae && echo '  Third-party COPR: selected (requires explicit review)' || echo '  Third-party COPR: disabled'
  exit 0
fi
[[ $(id -u) -ne 0 ]] || { echo 'Run as the normal user, NEVER sudo bash install.sh.' >&2; exit 1; }
[[ -r /etc/os-release ]] || { echo 'Fedora /etc/os-release missing' >&2; exit 1; }
# shellcheck source=/dev/null
source /etc/os-release
[[ "${ID:-}" == fedora ]] || { echo 'Regular Fedora Workstation is required (not Debian or Fedora derivatives).' >&2; exit 1; }
[[ ! -e /run/ostree-booted ]] || { echo 'Unsupported: Fedora Atomic/rpm-ostree installation.' >&2; exit 1; }
[[ "$(uname -m)" == x86_64 ]] || { echo 'Kuhl currently supports x86_64 only.' >&2; exit 1; }
(( ${VERSION_ID%%.*} >= 43 )) || { echo 'Requires Fedora 43 or newer (Niri include support).' >&2; exit 1; }
command -v dnf >/dev/null || { echo 'DNF is missing' >&2; exit 1; }
if (( REPLACE_CONFIGS )); then
  echo 'CAUTION: --replace-configs will back up then replace Niri/Waybar/Kitty/Rofi/Mako/Fuzzel dotfiles.'
  [[ -r /dev/tty ]] || { echo 'Interactive confirmation needed to replace dotfiles.' >&2; exit 1; }
  read -r -p 'Type REPLACE to continue: ' reply </dev/tty
  [[ "$reply" == REPLACE ]] || { echo 'Cancelled.'; exit 2; }
fi
if chosen vicinae; then
  echo
  echo 'Vicinae is not from Fedora official repositories.'
  echo 'It requires enabling the third-party COPR repository quadratech188/vicinae.'
  echo 'This COPR can distribute future package updates. Review it before trusting it.'
  [[ -r /dev/tty ]] || { echo 'Cannot request third-party repository consent in a noninteractive run.' >&2; exit 1; }
  read -r -p 'Type VICINAE to authorize this COPR: ' reply </dev/tty
  [[ "$reply" == VICINAE ]] || { echo 'Cancelled before installation.'; exit 2; }
fi
mkdir -p "$KUHL_STATE" "$KUHL_DATA" "$HOME/.local/bin"
LOG="$KUHL_STATE/install.log"
exec > >(tee -a "$LOG") 2>&1
printf '\n✳ KUHL OS 0.8 — FEDORA + NIRI\n'
printf 'Fedora %s / Kuhl %s\n' "${VERSION_ID:-unknown}" "$THEME"
echo 'AI-assisted community scripts can contain security errors. Review bootstrap.sh, install.sh, and package sources before continuing.'
[[ $(awk '/MemTotal:/ {print $2}' /proc/meminfo) -ge 7340032 ]] || kuhl_warn '8 GB RAM recommended, but not required.'
# Avoid letting DNF fail at transaction commit on a small VM root partition.
AVAILABLE_KB="$(df -Pk / | awk 'NR==2 {print $4}')"
if [[ "$AVAILABLE_KB" =~ ^[0-9]+$ ]] && (( AVAILABLE_KB < 716800 )); then
  kuhl_warn "Only $((AVAILABLE_KB/1024)) MiB free on /. Free at least 700 MiB before installing."
  kuhl_warn 'Try: sudo dnf clean all ; df -h /'
  [[ "${KUHL_ALLOW_LOW_DISK:-0}" == 1 ]] || exit 1
elif [[ "$AVAILABLE_KB" =~ ^[0-9]+$ ]] && (( AVAILABLE_KB < 2097152 )); then
  kuhl_warn 'Below 2 GiB free on /; consider resizing your VM disk for future Fedora updates.'
fi
python3 "$ROOT/scripts/progress.py" 0 'Verifying Fedora and preparing installation' 
printf '\n[1/6] Official Fedora desktop components\n'
sudo -v
sudo dnf install -y \
  niri xwayland-satellite xdg-desktop-portal-gnome xdg-desktop-portal-gtk \
  waybar rofi fuzzel kitty mako swaybg swaylock swayidle thunar \
  wl-clipboard papirus-icon-theme jetbrains-mono-fonts
if chosen desktop_helpers; then
  sudo dnf install -y network-manager-applet blueman pavucontrol brightnessctl playerctl
fi
ISSUES=0
python3 "$ROOT/scripts/progress.py" 1 'Official Fedora components installed'
printf '\n[2/6] Preflight: validate every Kuhl Niri theme before any user config changes\n'
python3 "$ROOT/scripts/validate_niri.py" || { kuhl_warn 'Bundled Niri config failed validation. Nothing in your personal config was changed.'; exit 1; }
python3 "$ROOT/scripts/progress.py" 2 'All Kuhl themes passed Niri validation'
printf '\n[3/6] Optional software and launcher\n'
if chosen vicinae; then
  if sudo dnf copr enable -y quadratech188/vicinae && sudo dnf install -y vicinae; then
    kuhl_info 'Vicinae installed (Super+Space will prefer it)'
  else
    kuhl_warn 'Could not install Vicinae: themed Rofi remains the default; Fuzzel is fallback.'
    ISSUES=$((ISSUES+1))
  fi
fi
mapfile -t FLATPAKS < <(python3 - "$ROOT/config/choices.json" "$TMP/choices.json" <<'PY'
import json,sys
items=json.load(open(sys.argv[1]))['choices']; selected=set(json.load(open(sys.argv[2]))['selected'])
for p in items:
 if p['id'] in selected and p['type']=='flatpak': print(p['value'])
PY
)
if (( ${#FLATPAKS[@]} )); then
  sudo dnf install -y flatpak
  flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
  for app in "${FLATPAKS[@]}"; do
    if ! flatpak install --user --noninteractive -y flathub "$app"; then
      kuhl_warn "Couldn't install optional app: $app"; ISSUES=$((ISSUES+1))
    fi
  done
fi
python3 "$ROOT/scripts/progress.py" 3 'Optional desktop features prepared'
printf '\n[4/6] Kuhl Frontier assets, keyboard guide and management tools\n'
mkdir -p "$KUHL_DATA/wallpapers" "$KUHL_DATA/templates" "$KUHL_DATA/branding"
for image in kuhl-day.png kuhl-dusk.png kuhl-default.png; do
  install -m 644 "$ROOT/assets/wallpapers/$image" "$KUHL_DATA/wallpapers/$image"
done
mkdir -p "$KUHL_DATA/wallpapers/third-party"
for image in frontier dyson puncture slowend; do
  install -m 644 "$ROOT/assets/wallpapers/third-party/$image.png" "$KUHL_DATA/wallpapers/third-party/$image.png"
done
install -m 644 "$ROOT/assets/branding/kuhl-logo.svg" "$KUHL_DATA/branding/kuhl-logo.svg"
install -m 644 "$ROOT/config/themes.json" "$KUHL_DATA/themes.json"
install -m 755 "$ROOT/scripts/render.py" "$KUHL_DATA/render.py"
install -m 755 "$ROOT/scripts/kuhl_ui.py" "$KUHL_DATA/kuhl_ui.py"
install -m 644 "$ROOT/config/keys.json" "$KUHL_DATA/keys.json"
cp -R "$ROOT/configs/." "$KUHL_DATA/templates/"
# Do not clobber an unrelated command in the user's personal bin.
if [[ -f "$KUHL_BIN" ]] && ! grep -q -E 'KUHL-MANAGED|Kuhl OS' "$KUHL_BIN"; then
  kuhl_warn "Unrelated command already exists: $KUHL_BIN; not overwriting."
  kuhl_warn 'Kuhl session launcher cannot work until this naming conflict is resolved.'
  exit 1
fi
install -m 755 "$ROOT/bin/kuhl" "$KUHL_BIN"
python3 "$ROOT/scripts/progress.py" 4 'Kuhl assets and applications registered'
printf '\n[5/6] Applying Kuhl Niri / Waybar / Kitty / Rofi / Mako / Fuzzel rice\n'
OPTIONS=(install --source "$KUHL_DATA/templates" --theme "$THEME")
(( ! REPLACE_CONFIGS )) || OPTIONS+=(--replace-configs)
python3 "$KUHL_DATA/render.py" "${OPTIONS[@]}"
# Automatic wallpaper follows selected theme unless user explicitly picks a wallpaper later.
mkdir -p "$KUHL_STATE"
if [[ ! -s "$KUHL_STATE/wallpaper-choice" ]]; then printf 'auto\n' > "$KUHL_STATE/wallpaper-choice"; fi
python3 "$ROOT/scripts/progress.py" 5 'Backed-up, tracked configuration deployment finished'
printf '\n[6/6] Validating your active Niri session configuration\n'
if ! niri validate; then
  kuhl_warn 'The active Niri config is invalid (possibly an existing user config).'
  kuhl_warn 'All bundled Kuhl themes passed isolated native validation before deployment.'
  kuhl_warn 'Existing files and Kuhl-managed configs are preserved for manual diagnosis.'
  kuhl_warn 'Run niri validate to inspect the active file; use kuhl uninstall if you want to undo Kuhl-managed configs.'
  exit 1
fi
if ! grep -q 'KUHL-MANAGED' "${XDG_CONFIG_HOME:-$HOME/.config}/niri/config.kdl"; then
  kuhl_warn 'Existing Niri config was preserved; add Kuhl integration manually or use --replace-configs.'
  ISSUES=$((ISSUES+1))
fi
python3 "$ROOT/scripts/progress.py" 6 'Kuhl Frontier installed successfully — ready for Niri'
printf '\nInstalled. GNOME remains available.\n'
printf 'Log out, choose Niri at the GDM login screen, then sign in.\n'
printf 'Super+Space opens search; Ctrl+Super+K opens the keyboard guide. Super+D opens Kuhl Control Center.\n'
printf 'See diagnostics: kuhl doctor  |  Install log: %s\n' "$LOG"
if (( ISSUES )); then kuhl_warn "$ISSUES nonfatal issue(s) need attention; review the log."; fi
printf 'No reboot performed; no GNOME settings or Fedora security controls were changed.\n'
