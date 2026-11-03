#!/usr/bin/env bash
# KUHL-MANAGED — the one-command entry point for Kuhl OS Studio.
# Public install command:
#   curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
# Runs with the current user; only DNF operations inside install.sh use sudo.
set -Eeuo pipefail

SOURCE_URL='https://github.com/TerabyteEXE/Kuhl-OS/archive/refs/heads/main.tar.gz'

if [[ "${1:-}" == --help || "${1:-}" == -h ]]; then
  printf '%s\n' 'Kuhl OS Studio — one-command installer' \
    'Install from Fedora Workstation as your regular user:' \
    '  curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash' \
    'The installer opens a terminal menu to configure your desktop and backups.'
  exit 0
fi

[[ $(id -u) -ne 0 ]] || { echo '[kuhl] Run as your normal user, not root or sudo.' >&2; exit 1; }
[[ -r /dev/tty && -t 1 ]] || { echo '[kuhl] Run this from an interactive terminal, not a background job.' >&2; exit 1; }
for cmd in curl tar mktemp; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "[kuhl] Missing required command: $cmd" >&2; exit 1; }
done

# Download to disk first. Do not pipe an incomplete or failed download to tar.
umask 077
tmp="$(mktemp -d -t kuhl-bootstrap.XXXXXXXX)"
trap 'rm -rf -- "$tmp"' EXIT
mkdir -p "$tmp/source"

printf '\n\033[1;33m'
printf '  ✳  K U H L   O S    /    S T U D I O\n'
printf '\033[0m'
printf '  Fedora + Niri · one-command desktop installer\n\n'
printf '  [1/2] Downloading the current Kuhl OS release from GitHub...\n'
if ! curl -fLSs --retry 2 --connect-timeout 15 --max-time 120 \
    --output "$tmp/source.tar.gz" "$SOURCE_URL"; then
  echo '[kuhl] Download failed. Check your internet connection and the repository URL.' >&2
  exit 1
fi
if ! tar -xzf "$tmp/source.tar.gz" --no-same-owner --strip-components=1 -C "$tmp/source"; then
  echo '[kuhl] The downloaded release could not be extracted.' >&2
  exit 1
fi
for file in install.sh lib/common.sh config/choices.json scripts/menu.py scripts/validate_niri.py; do
  [[ -f "$tmp/source/$file" ]] || { echo "[kuhl] Incomplete source archive (missing $file)." >&2; exit 1; }
done
printf '  [2/2] Opening the Kuhl setup experience...\n\n'
# Installer prompts work even when this bootstrap is launched via curl | bash.
# All Fedora/architecture checks, validation, backups and progress UI remain in install.sh.
bash "$tmp/source/install.sh" "$@" </dev/tty
