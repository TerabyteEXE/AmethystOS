#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
  echo 'Run as your normal user, not root.' >&2; exit 2
fi
python3 "$ROOT/scripts/deploy.py" restore "$@"
