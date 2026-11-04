#!/usr/bin/env bash
# AmethystOS: one installer, user-selectable Fedora apps, recoverable dotfiles.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DRY=0 REPLACE=0 SKIP_PACKAGES=0 NON_INTERACTIVE=0 NO_THEME=0
APP_GROUPS='' APPS_SET=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --replace) REPLACE=1 ;;
    --no-packages) SKIP_PACKAGES=1 ;;
    --non-interactive) NON_INTERACTIVE=1 ;;
    --no-theme) NO_THEME=1 ;;
    --apps=*) APP_GROUPS=${arg#--apps=}; APPS_SET=1 ;;
    --help|-h)
      cat <<'HELP'
AmethystOS — Fedora + Niri
Usage: bash install.sh [--dry-run] [--replace] [--no-packages]
                       [--non-interactive] [--apps=browser,essentials,dev]
  Interactive setup uses a branded terminal menu and makes optional apps selectable.
  --replace         Back up and replace existing user configurations
  --non-interactive Use default app selections, no terminal prompts
  --apps=...        Comma-separated app groups; empty value installs no extras
  --no-packages     Don't run DNF (advanced)
  --no-theme        Do not change existing GNOME/GTK appearance preferences
  --dry-run         Validate the plan without modifying the system
The persistent removal command after install is: amethystos-uninstall
HELP
      exit 0 ;;
    *) printf 'Unknown option: %s\n' "$arg" >&2; exit 2 ;;
  esac
done
if (( DRY == 0 )) && (( ${EUID:-$(id -u)} == 0 )); then
  echo 'Run as your normal user, not root (sudo is used for DNF only).' >&2; exit 2
fi
if (( DRY == 0 )); then
  [[ -r /etc/os-release ]] || { echo 'Cannot detect Fedora.' >&2; exit 2; }
  # shellcheck disable=SC1091
  source /etc/os-release
  [[ ${ID:-} == fedora ]] || { echo 'AmethystOS requires Fedora Workstation.' >&2; exit 2; }
  command -v dnf >/dev/null || { echo 'DNF was not found.' >&2; exit 2; }
fi
command -v python3 >/dev/null || { echo 'Python 3 is required.' >&2; exit 2; }
TMPPLAN=$(mktemp)
cleanup() { rm -f -- "$TMPPLAN"; [[ ! -t 1 ]] || printf '\033[?25h'; }
trap cleanup EXIT
trap 'code=$?; printf "\n[amethystos] Setup stopped (exit %s). Existing user configs are protected.\n" "$code" >&2' ERR

PURPLE=$'\033[38;5;141m'; GREEN=$'\033[38;5;116m'; DIM=$'\033[2m'; BOLD=$'\033[1m'; RESET=$'\033[0m'
if [[ -t 1 ]]; then printf '\033[?25l'; fi
stage() {
  local n=$1 label=$2 x filled bar=''
  filled=$((n*3))
  for ((x=0; x<21; x++)); do
    if ((x<filled)); then bar+='━'; else bar+='─'; fi
  done
  printf '\n%s[%d/7]%s %s\n  %s%s%s\n' "$PURPLE" "$n" "$RESET" "$label" "$GREEN" "$bar" "$RESET"
}
printf '\n%s◆ AMETHYSTOS%s     %sFEDORA + NIRI  ·  INSTALLER%s\n' "$BOLD$PURPLE" "$RESET" "$DIM" "$RESET"
printf '  Existing Fedora and GNOME are preserved. Review scripts before installing.\n'

stage 1 'Checking the source, storage and system'
for path in LICENSE.upstream payload/niri/config.kdl payload/waybar/config.jsonc assets/wallpapers/AmethystDark.png assets/wallpapers/AmethystLight.png; do
  [[ -s "$ROOT/$path" ]] || { echo "Missing: $path" >&2; exit 1; }
done
if (( ! DRY && ! SKIP_PACKAGES )); then
  free_kb=$(df -Pk / | awk 'NR==2 {print $4}')
  if [[ -n "$free_kb" ]] && (( free_kb < 1048576 )); then
    printf 'Not enough root disk space: %s MiB free; need at least 1 GiB.\n' "$((free_kb/1024))" >&2
    exit 1
  fi
fi

stage 2 'Choosing applications and upgrade behavior'
uiargs=(--output "$TMPPLAN")
if (( DRY || NON_INTERACTIVE )) || [[ ! -t 1 ]]; then uiargs+=(--non-interactive); fi
if (( APPS_SET )); then uiargs+=(--groups "$APP_GROUPS"); fi
if (( REPLACE )); then uiargs+=(--replace); fi
if (( NO_THEME )); then uiargs+=(--no-theme); fi
python3 "$ROOT/scripts/setup_ui.py" "${uiargs[@]}"
readarray -t selection < <(python3 - "$TMPPLAN" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]))
print(','.join(p['groups']))
print('1' if p['replace'] else '0')
print('1' if p.get('apply_dark') else '0')
PY
)
APP_GROUPS=${selection[0]}
REPLACE=${selection[1]}
APPLY_DARK=${selection[2]}
printf 'Optional apps: %s\n' "${APP_GROUPS:-none}"

stage 3 'Checking existing desktop settings (before DNF changes)'
conflicts=()
for name in niri waybar fuzzel kitty alacritty mako niri-lock gtk-3.0 gtk-4.0 qt6ct btop cava fastfetch starship fish; do
  [[ -e "$HOME/.config/$name" || -L "$HOME/.config/$name" ]] && conflicts+=("$name")
done
[[ -e "$HOME/.config/xdg-desktop-portal/niri-portals.conf" ]] && conflicts+=('niri-portals.conf')
if (( ${#conflicts[@]} )); then
  printf 'Existing config paths: %s\n' "${conflicts[*]}"
  if (( ! REPLACE && ! DRY )); then
    if (( NON_INTERACTIVE )) || [[ ! -e /dev/tty ]]; then
      echo 'Refusing to overwrite. Re-run with --replace after reviewing the backups.' >&2; exit 1
    fi
    printf 'Back up and replace existing configs? Type REPLACE to proceed: '
    read -r reply </dev/tty || reply=''
    [[ "$reply" == REPLACE ]] || { echo 'Canceled. No configs were changed.'; exit 1; }
    REPLACE=1
  fi
fi


stage 4 'Installing the Fedora desktop and selected apps'
if (( DRY )); then
  echo 'Dry run: DNF packages will not be changed.'
elif (( SKIP_PACKAGES )); then
  echo 'Packages skipped by request. You are responsible for dependencies.'
else
  # shellcheck disable=SC1091
  source "$ROOT/scripts/packages.sh"
  amethystos_install_fedora_packages "$APP_GROUPS"
fi

stage 5 'Validating Niri and installing desktop configurations'
args=(install)
(( REPLACE )) && args+=(--replace)
(( DRY )) && args+=(--dry-run)
(( DRY || SKIP_PACKAGES )) || args+=(--require-niri)
python3 "$ROOT/scripts/deploy.py" "${args[@]}"

stage 6 'Preparing the official light and dark wallpapers'
if (( DRY )); then
  echo 'Dry run: both Amethyst wallpapers are present in the bundle.'
else
  python3 "$ROOT/scripts/wallpapers.py"
  if (( APPLY_DARK )); then
    if ! python3 "$ROOT/scripts/desktop_prefs.py" dark; then
      echo 'Note: GSettings appearance preference unavailable; GTK configs are still installed.' >&2
    fi
  fi
  mkdir -p "$HOME/Pictures/Screenshots"
fi

stage 7 'Finished'
if (( DRY )); then
  echo 'Dry run complete. No changes made.'
else
  printf '%sAmethystOS is installed.%s Log out, select Niri at the login screen.\n' "$GREEN" "$RESET"
  printf 'Settings: %samethyst-settings%s   |   Check installation: %samethyst-doctor%s\n' "$BOLD" "$RESET" "$BOLD" "$RESET"
  echo 'Wallpaper picker: set-wallpaper  |  Uninstall: amethystos-uninstall'
  echo 'GNOME is left available as your backup graphical session.'
fi
