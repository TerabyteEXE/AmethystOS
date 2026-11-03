#!/usr/bin/env bash
# Kuhl OS — Fedora installation wrapper for the upstream Niri dotfiles.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DRY=0
REPLACE=0
SKIP_PACKAGES=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --replace) REPLACE=1 ;;
    --no-packages) SKIP_PACKAGES=1 ;;
    --help|-h)
      printf '%s\n' 'Kuhl OS Base v1 — Fedora + Niri' \
       'Usage: bash install.sh [--dry-run] [--replace] [--no-packages]' \
       '  --replace       Back up and replace existing user dotfiles' \
       '  --no-packages   Skip Fedora package installation (advanced)' \
       '  --dry-run       Test without changing the system'; exit 0 ;;
    *) printf 'Unknown argument: %s\n' "$arg" >&2; exit 2 ;;
  esac
done

if [[ ${EUID:-$(id -u)} -eq 0 && $DRY -eq 0 ]]; then
  echo 'Do not run Kuhl OS installer as root (sudo is requested only for DNF).' >&2
  exit 2
fi

if [[ $DRY -eq 0 ]]; then
  if [[ ! -r /etc/os-release ]]; then echo 'Cannot detect Fedora.' >&2; exit 2; fi
  # shellcheck disable=SC1091
  source /etc/os-release
  if [[ ${ID:-} != fedora ]]; then echo 'Kuhl OS v1 supports Fedora Workstation only.' >&2; exit 2; fi
  if [[ ! $(command -v dnf) ]]; then echo 'DNF was not found.' >&2; exit 2; fi
fi
command -v python3 >/dev/null || { echo 'Python 3 is required' >&2; exit 2; }

printf '\033[?25l'
trap 'printf "\033[?25h"' EXIT
BOLD=$'\033[1m'; DIM=$'\033[2m'; GOLD=$'\033[38;5;179m'; RESET=$'\033[0m'
step() {
  local i=$1 label=$2 done=0 bar='' n=0
  done=$((i*4))
  for ((n=0;n<20;n++)); do if ((n<done)); then bar+='━'; else bar+='─'; fi; done
  printf '\n%s [%d/5] %s\n %s[%s]%s\n' "$GOLD" "$i" "$label" "$RESET" "$bar" "$RESET"
}

printf '\n%sKUHL OS%s  /  BASE v1\n%sFedora + Niri  ·  one desktop, one installer%s\n' "$BOLD$GOLD" "$RESET" "$DIM" "$RESET"
printf 'This installer adds the upstream Niri desktop to your existing Fedora system.\n'
printf 'GNOME, the login manager, and your personal files are not removed.\n'
printf 'Code is MIT-licensed; please review the security notes before use.\n\n'

step 1 'Checking storage, system and source files'
if [[ ! -f "$ROOT/LICENSE.upstream" || ! -f "$ROOT/payload/niri/config.kdl" || ! -f "$ROOT/payload/waybar/config.jsonc" ]]; then
  echo 'Installation archive incomplete.' >&2; exit 1
fi
if [[ $DRY -eq 0 && $SKIP_PACKAGES -eq 0 ]]; then
  free_kb=$(df -Pk / | awk 'NR==2 {print $4}')
  if [[ -n "$free_kb" ]] && (( free_kb < 1048576 )); then
    printf '\nNot enough free space on / (about %s MiB available). Free at least 1 GiB and retry.\n' "$((free_kb/1024))" >&2
    exit 1
  fi
fi

step 2 'Preparing Fedora software'
if [[ $DRY -eq 1 ]]; then
  echo 'Dry run: no DNF operations'
elif [[ $SKIP_PACKAGES -eq 1 ]]; then
  echo 'Skipping packages by request'
else
  # DNF packages are separated into essential runtime pieces and optional polish.
  # In particular Starship requires a non-default Fedora repository, so a missing
  # package must never block the compositor/desktop installation.
  # No COPR/AUR/custom repositories are enabled automatically.
  # No global changes to GDM or the user's login shell.
  # shellcheck disable=SC1091
  source "$ROOT/scripts/packages.sh"
  kuhl_install_fedora_packages

fi

step 3 'Checking existing configurations'
conflicts=()
for name in niri waybar fuzzel kitty alacritty mako niri-lock gtk-3.0 gtk-4.0 qt6ct btop cava fastfetch starship fish; do
  [[ -e "$HOME/.config/$name" || -L "$HOME/.config/$name" ]] && conflicts+=("$name")
done
[[ -e "$HOME/.config/xdg-desktop-portal/niri-portals.conf" ]] && conflicts+=("niri-portals.conf")
if (( ${#conflicts[@]} > 0 )); then
  if [[ $REPLACE -eq 0 && $DRY -eq 0 ]]; then
    printf '\nExisting settings found for: %s\n' "${conflicts[*]}"
    printf 'Replace these configs after making a recoverable backup? [y/N] '
    read -r reply </dev/tty || reply='n'
    case "$reply" in y|Y|yes|YES) REPLACE=1;; *) echo 'No configs were changed. Re-run with --replace if desired.'; exit 1;; esac
  fi
fi

step 4 'Validating and deploying the original desktop configuration'
args=(install)
(( REPLACE )) && args+=(--replace)
(( DRY )) && args+=(--dry-run)
(( DRY || SKIP_PACKAGES )) || args+=(--require-niri)
python3 "$ROOT/scripts/deploy.py" "${args[@]}"

step 5 'Finishing'
if [[ $DRY -eq 1 ]]; then
  echo 'Dry-run complete. No changes made.'
else
  mkdir -p "$HOME/Pictures/wallpapers" "$HOME/Pictures/Screenshots"
  echo 'Done. Log out and choose Niri from the Fedora login screen.'
  echo 'Keybinds: Super+Return terminal; Super+Space search; Super+Q close; Super+P power menu.'
  echo 'Restore previous settings: bash uninstall.sh (checks for user modifications first).'
  echo 'No reboot required; keep GNOME as your recovery session.'
fi
