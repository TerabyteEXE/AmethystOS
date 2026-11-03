#!/usr/bin/env bash
# Kuhl OS: upstream session components, with Fedora-safe integration.
set -u

# Niri's session handles the desktop environment and portal environment.
# Do not kill xdg-desktop-portal services or rewrite global session variables.

# Use the user's saved wallpaper if present; otherwise a dark solid background.
WALLDIR="$HOME/Pictures/wallpapers"
SELECTION="$HOME/.local/state/kuhl-base-v1/wallpaper"
WALL=""
if [[ -f "$SELECTION" ]]; then
  IFS= read -r WALL < "$SELECTION" || true
  [[ -f "$WALL" ]] || WALL=""
fi
if [[ -z "$WALL" ]]; then
  WALL=$(find "$WALLDIR" -maxdepth 1 -type f \
    \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) \
    -print 2>/dev/null | sort | head -n 1)
fi
if [[ -n "$WALL" ]]; then
  swaybg -i "$WALL" -m fill &
else
  swaybg -c '#141823' &
fi

mako &
wl-paste --watch cliphist store &
waybar &
# GNOME Workstation already starts keyring/NetworkManager via session services.
# Start a policy agent only when one is not registered already.
if command -v /usr/libexec/polkit-kde-authentication-agent-1 >/dev/null 2>&1; then
  /usr/libexec/polkit-kde-authentication-agent-1 &
elif command -v /usr/lib64/libexec/polkit-kde-authentication-agent-1 >/dev/null 2>&1; then
  /usr/lib64/libexec/polkit-kde-authentication-agent-1 &
fi
wait
