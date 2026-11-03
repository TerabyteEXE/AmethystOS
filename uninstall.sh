#!/usr/bin/env bash
set -Eeuo pipefail
BIN="$HOME/.local/bin/kuhl"
if [[ -x "$BIN" ]]; then
  exec "$BIN" uninstall
fi
echo 'Kuhl management command not installed; nothing was removed.' >&2
exit 1
