#!/usr/bin/env bash
set -euo pipefail
if ! command -v gammastep >/dev/null 2>&1; then
  notify-send 'AmethystOS' 'Night light requires gammastep (sudo dnf install gammastep)'
  exit 0
fi
if pgrep -x gammastep >/dev/null; then
  pkill -x gammastep
else
  nohup gammastep -O 4000 >/dev/null 2>&1 &
fi
