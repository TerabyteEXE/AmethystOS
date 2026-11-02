#!/usr/bin/env bash
set -Eeuo pipefail
BIN="$HOME/.local/bin/kuhl"
if [[ -x "$BIN" ]]; then
  exec "$BIN" uninstall
fi
printf 'Kuhl OS is not installed (no %s).\n' "$BIN" >&2
exit 1
