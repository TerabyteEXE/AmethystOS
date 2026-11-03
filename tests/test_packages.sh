#!/usr/bin/env bash
# Simulate the Fedora 44 failure: Starship is absent from enabled repos.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/packages.sh"

[[ " ${KUHL_REQUIRED[*]} " != *' starship '* ]] || { echo 'starship is in the essential set' >&2; exit 1; }
[[ " ${KUHL_OPTIONAL[*]} " == *' starship '* ]] || { echo 'starship is not optional' >&2; exit 1; }

calls=0
sudo() {
  [[ $1 == dnf && $2 == install && $3 == -y ]] || { echo 'Unexpected DNF invocation' >&2; return 40; }
  calls=$((calls + 1))
  shift 3
  if [[ " $* " == *' starship '* ]]; then
    [[ " $* " == *' --skip-unavailable '* ]] || {
      echo 'No match for argument: starship' >&2
      return 1
    }
    echo '[mock DNF] starship unavailable; skipped by --skip-unavailable'
  else
    echo '[mock DNF] essential packages installed'
  fi
  return 0
}
kuhl_install_fedora_packages
[[ $calls -eq 2 ]] || { echo "Expected 2 DNF operations, got $calls" >&2; exit 1; }

echo '[test] Missing Fedora 44 Starship cannot block required desktop packages: OK'
