#!/usr/bin/env bash
if ! command -v wf-recorder >/dev/null 2>&1; then
  notify-send 'AmethystOS' 'Screen recording requires wf-recorder (optional).'
  exit 0
fi
notify-send 'AmethystOS' 'Open a terminal to run wf-recorder safely; no unattended recording starts.'
