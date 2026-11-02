#!/usr/bin/env bash
# Public HTTPS loader. Download source in one tarball; then run the interactive installer.
set -Eeuo pipefail
URL='https://github.com/TerabyteEXE/Kuhl-OS/archive/refs/heads/main.tar.gz'
command -v curl >/dev/null || { echo 'curl is required; sudo dnf install curl'; exit 1; }
command -v tar >/dev/null || { echo 'tar is required; sudo dnf install tar'; exit 1; }
[[ $(id -u) -ne 0 ]] || { echo 'Run as your normal GNOME user, not root.' >&2; exit 1; }
[[ -r /dev/tty ]] || { echo 'Kuhl needs a real terminal for the interactive installer.' >&2; exit 1; }
tmp="$(mktemp -d -t kuhl-bootstrap.XXXXXX)"
trap 'rm -rf -- "$tmp"' EXIT
printf '✳ Fetching Kuhl OS source from GitHub...\n'
curl --fail --location --silent --show-error --retry 2 --max-time 120 "$URL" | tar -xzf - -C "$tmp"
[[ -f "$tmp/Kuhl-OS-main/install.sh" ]] || { echo 'Repository is missing install.sh' >&2; exit 1; }
printf 'Source downloaded. Starting setup...\n'
# Important when invoked via `curl ... | bash`: restore interactive input for curses.
bash "$tmp/Kuhl-OS-main/install.sh" "$@" </dev/tty
