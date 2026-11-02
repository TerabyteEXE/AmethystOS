#!/usr/bin/env bash
# Common routines for Kuhl OS. Sourced from install.sh and bin/kuhl.

KUHL_DATA="${XDG_DATA_HOME:-$HOME/.local/share}/kuhl"
KUHL_STATE="${XDG_STATE_HOME:-$HOME/.local/state}/kuhl"
KUHL_SETTINGS="$KUHL_STATE/settings.tsv"
KUHL_BIN="$HOME/.local/bin/kuhl"
KUHL_APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"

kuhl_info() { printf '[kuhl] %s\n' "$*"; }
kuhl_warn() { printf '[kuhl] WARNING: %s\n' "$*" >&2; }
kuhl_error() { printf '[kuhl] ERROR: %s\n' "$*" >&2; return 1; }

kuhl_key_exists() {
  command -v gsettings >/dev/null 2>&1 &&
  gsettings list-keys "$1" 2>/dev/null | grep -Fxq -- "$2"
}

# Accepts a GVariant-formatted value, e.g. "'prefer-dark'" or "['<Control>space']".
# Only records a change AFTER gsettings accepts it. Repeated installs preserve
# the first original value and update the last Kuhl-applied value.
kuhl_set() {
  local schema="$1" key="$2" value="$3" before tmp found=0 s k original applied
  if ! kuhl_key_exists "$schema" "$key"; then
    kuhl_warn "Skipping unsupported setting: $schema $key"
    return 0
  fi
  before="$(gsettings get "$schema" "$key")" || return 1
  if ! gsettings set "$schema" "$key" "$value"; then
    kuhl_warn "Couldn't set $schema $key"
    return 1
  fi
  mkdir -p "$KUHL_STATE"
  tmp="$(mktemp "$KUHL_STATE/.settings.XXXXXXXX")"
  if [[ -f "$KUHL_SETTINGS" ]]; then
    while IFS=$'\t' read -r s k original applied || [[ -n "${s:-}" ]]; do
      [[ -z "$s" ]] && continue
      if [[ "$s" == "$schema" && "$k" == "$key" ]]; then
        printf '%s\t%s\t%s\t%s\n' "$s" "$k" "$original" "$value" >> "$tmp"
        found=1
      else
        printf '%s\t%s\t%s\t%s\n' "$s" "$k" "$original" "$applied" >> "$tmp"
      fi
    done < "$KUHL_SETTINGS"
  fi
  if (( ! found )); then
    printf '%s\t%s\t%s\t%s\n' "$schema" "$key" "$before" "$value" >> "$tmp"
  fi
  mv -f "$tmp" "$KUHL_SETTINGS"
  chmod 600 "$KUHL_SETTINGS"
}

kuhl_quote() {
  python3 - "$1" <<'PY'
import sys
print(repr(sys.argv[1]))
PY
}

kuhl_theme() {
  local theme="$1" schema="org.gnome.desktop.interface"
  case "$theme" in
    day)
      kuhl_set "$schema" color-scheme "'prefer-light'"
      kuhl_set "$schema" gtk-theme "'adw-gtk3'"
      kuhl_set "$schema" icon-theme "'Papirus-Light'"
      kuhl_set org.gnome.shell.extensions.user-theme name "'Kuhl-Day'"
      ;;
    dusk)
      kuhl_set "$schema" color-scheme "'prefer-dark'"
      kuhl_set "$schema" gtk-theme "'adw-gtk3-dark'"
      kuhl_set "$schema" icon-theme "'Papirus-Dark'"
      kuhl_set org.gnome.shell.extensions.user-theme name "'Kuhl-Dusk'"
      ;;
    *) kuhl_error "Theme must be day or dusk (received: $theme)"; return 2 ;;
  esac
  kuhl_info "Theme set to $theme. If needed, log out and in to refresh older apps."
}
