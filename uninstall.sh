#!/usr/bin/env bash
# From a cloned repo. Prefer the persistent amethystos-uninstall command.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
[[ ${EUID:-$(id -u)} -ne 0 ]] || { echo 'Run as the regular user, not root.' >&2; exit 2; }
DRY=0 YES=0
for arg in "$@"; do
  case "$arg" in --dry-run) DRY=1 ;; --yes) YES=1 ;; --help|-h)
    echo 'bash uninstall.sh [--dry-run] [--yes] — restores backed-up configs; does not uninstall packages.'; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 2;;
  esac
done
printf '\n\033[38;5;141m◆ AMETHYSTOS  /  RESTORE\033[0m\n'
if (( DRY )); then exec python3 "$ROOT/scripts/deploy.py" restore --dry-run; fi
if (( ! YES )); then
  [[ -e /dev/tty ]] || { echo 'Confirmation required (use --yes).' >&2; exit 1; }
  printf 'Restore previous config files? Type RESTORE: '
  read -r confirmation </dev/tty || confirmation=''
  [[ "$confirmation" == RESTORE ]] || { echo 'No changes made.'; exit 1; }
fi
python3 "$ROOT/scripts/deploy.py" restore --dry-run >/dev/null
python3 "$ROOT/scripts/desktop_prefs.py" restore || true
python3 "$ROOT/scripts/appearance.py" restore-scale || true
python3 "$ROOT/scripts/deploy.py" restore
printf 'Dotfiles restored. Fedora applications and user wallpapers are left in place.\n'
