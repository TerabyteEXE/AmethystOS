#!/usr/bin/env bash
# Launch without killing unrelated Waybar sessions or hiding actual errors.
set -Eeuo pipefail
exec waybar "$@"
