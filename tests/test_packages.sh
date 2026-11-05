#!/usr/bin/env bash
# Prevent DNF package-name regressions; simulate Fedora installation safely.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/packages.sh"
[[ " ${AMETHYSTOS_REQUIRED[*]} " == *" ImageMagick "* ]] || { echo 'ImageMagick package name is missing' >&2; exit 1; }
[[ " ${AMETHYSTOS_REQUIRED[*]} " != *" imagemagick "* ]] || { echo 'Bad lowercase imagemagick package name' >&2; exit 1; }
log=$(mktemp)
trap 'rm -f "$log"' EXIT
# No privileged commands or network access during this test.
sudo() { printf '%s\n' "$*" >> "$log"; }
amethystos_install_legacy() { :; }
amethystos_install_fedora_packages ''
grep -q 'dnf install -y .*ImageMagick' "$log" || { echo 'ImageMagick not in simulated DNF transaction' >&2; exit 1; }
! grep -Eq 'gnome-calculator|file-roller|libreoffice-writer' "$log" || { echo 'Empty optional selection installed extra apps' >&2; exit 1; }
: > "$log"
amethystos_install_fedora_packages 'essentials'
grep -q 'gnome-calculator' "$log" || { echo 'Explicit essentials option not installed' >&2; exit 1; }
echo '[ok] Fedora package spelling and no-optional-apps choice'
