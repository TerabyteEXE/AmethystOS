#!/usr/bin/env bash
# Simple notification tools using mako's actual control API.
set -u
command -v makoctl >/dev/null 2>&1 || { command -v notify-send >/dev/null && notify-send 'AmethystOS' 'Mako is not running'; exit 1; }
choice=$(printf '%s\n' 'Restore recent notification' 'Dismiss all notifications' 'Show notification history' | fuzzel --dmenu --prompt 'Notifications: ') || exit 0
case "$choice" in
  'Restore recent notification') makoctl restore || notify-send 'Notifications' 'There are no notifications to restore' ;;
  'Dismiss all notifications') makoctl dismiss -a ;;
  'Show notification history')
    if command -v alacritty >/dev/null; then
      alacritty -e bash -lc 'makoctl history; echo; read -r -p "Press Enter to close..."' &
    else
      makoctl history
    fi ;;
esac
