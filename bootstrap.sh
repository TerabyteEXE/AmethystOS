#!/usr/bin/env bash
# KUHL-MANAGED - HTTPS bootstrap. Review before running; no script is executed as root.
set -Eeuo pipefail
URL='https://github.com/TerabyteEXE/Kuhl-OS/archive/refs/heads/main.tar.gz'
for cmd in curl tar; do command -v "$cmd" >/dev/null || { echo "$cmd is required" >&2; exit 1; }; done
[[ $(id -u) -ne 0 ]] || { echo 'Use your normal account, not root.' >&2; exit 1; }
[[ -r /dev/tty ]] || { echo 'An interactive terminal is required.' >&2; exit 1; }
tmp="$(mktemp -d -t kuhl-bootstrap.XXXXXXXX)"
trap 'rm -rf -- "$tmp"' EXIT
printf '✳ Downloading Kuhl OS source (please review public code before using)...\n'
curl -fL --retry 2 --max-time 120 "$URL" | tar -xz -C "$tmp"
[[ -f "$tmp/Kuhl-OS-main/install.sh" ]] || { echo 'Archive did not contain an installer.' >&2; exit 1; }
bash "$tmp/Kuhl-OS-main/install.sh" "$@" </dev/tty
