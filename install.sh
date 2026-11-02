#!/usr/bin/env bash
# Kuhl OS v0.2 - cautious, repeatable Fedora Workstation GNOME customization.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$ROOT/lib/common.sh"

THEME=dusk
PROFILE=full
INSTALL_PACKAGES=1
DRY_RUN=0
usage() {
  cat <<'HELP'
Kuhl OS installer - run as your normal user inside a Fedora GNOME session.

Usage: bash install.sh [--theme day|dusk] [--profile full|balanced|none] [--no-packages] [--dry-run]

--theme day|dusk  First appearance (default: dusk)
--profile         full (all visual effects), balanced (lighter), or none (no add-ons)
--no-packages     Skip DNF package installation; themes may be incomplete
--dry-run         Show planned actions without changing anything
-h, --help        Show this information
HELP
}
while (( $# )); do
  case "$1" in
    --theme) [[ $# -ge 2 ]] || { usage; exit 2; }; THEME="$2"; shift 2;;
    --profile) [[ $# -ge 2 ]] || { usage; exit 2; }; PROFILE="$2"; shift 2;;
    --no-packages) INSTALL_PACKAGES=0; shift;;
    --dry-run) DRY_RUN=1; shift;;
    -h|--help) usage; exit 0;;
    *) kuhl_error "Unknown argument: $1"; usage; exit 2;;
  esac
done
[[ "$PROFILE" == full || "$PROFILE" == balanced || "$PROFILE" == none ]] || { kuhl_error "--profile must be full, balanced, or none"; exit 2; }
[[ "$THEME" == day || "$THEME" == dusk ]] || { kuhl_error "--theme must be day or dusk"; exit 2; }
[[ "$(id -u)" != 0 ]] || { kuhl_error "Do not run as root or with sudo. The script will request sudo for DNF only."; exit 1; }
[[ "$(uname -m)" == x86_64 ]] || { kuhl_error "This Kuhl release targets x86_64 PCs only."; exit 1; }
[[ -f /etc/os-release ]] || { kuhl_error "Could not identify the operating system."; exit 1; }
# shellcheck source=/dev/null
source /etc/os-release
[[ "${ID:-}" == fedora ]] || { kuhl_error "This installer requires Fedora Workstation."; exit 1; }
[[ "${VARIANT_ID:-workstation}" == workstation || "${VARIANT_ID:-}" == "" ]] || kuhl_warn "This does not appear to be Fedora Workstation."
if command -v rpm-ostree >/dev/null 2>&1 && [[ -f /run/ostree-booted ]]; then
  kuhl_error "Fedora Atomic desktops use rpm-ostree; install regular Fedora Workstation instead."
  exit 1
fi
if [[ "${XDG_CURRENT_DESKTOP:-}" != *GNOME* ]]; then
  kuhl_error "Log into your GNOME desktop session before installing. XDG_CURRENT_DESKTOP=${XDG_CURRENT_DESKTOP:-unset}"
  exit 1
fi
command -v gsettings >/dev/null || { kuhl_error "gsettings not found."; exit 1; }
command -v python3 >/dev/null || { kuhl_error "python3 is required."; exit 1; }
command -v dnf >/dev/null || { kuhl_error "dnf is required."; exit 1; }
if [[ ! -d "$ROOT/assets/wallpapers" ]] || [[ ! -f "$ROOT/assets/wallpapers/kuhl-day.png" ]] || [[ ! -f "$ROOT/assets/wallpapers/kuhl-dusk.png" ]]; then
  kuhl_error "Missing wallpaper assets. Download/extract the entire repository, not only install.sh."
  exit 1
fi
if [[ -r /proc/meminfo ]]; then
  mem_kib="$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)"
  (( mem_kib >= 7*1024*1024 )) || kuhl_warn "This system has under ~8 GB RAM; Kuhl recommends 8 GB or more."
fi
kuhl_info "Fedora ${VERSION_ID:-unknown} / GNOME / ${THEME^} theme"
if (( DRY_RUN )); then
  cat <<'PLAN'
DRY RUN — no changes will be made.
  1. Install fonts, Papirus icons and GTK3 compatibility theme via Fedora DNF.
  2. Copy two Kuhl wallpapers into ~/.local/share/kuhl/.
  3. Save previous GNOME settings under ~/.local/state/kuhl/.
  4. Set Day/Dusk wallpaper pair, fonts, icons and warm accent.
  5. Add Ctrl+Space to GNOME's built-in Overview search shortcut.
  6. Install `kuhl` CLI and two desktop theme switchers.
  7. Install Kuhl Shell CSS via GNOME User Themes, plus compatible extensions
     (select --profile balanced/none to reduce add-ons).
  No apps or packages are removed. Fedora security settings are untouched.
PLAN
  exit 0
fi

if (( INSTALL_PACKAGES )); then
  kuhl_info "Installing a small set of Fedora packages (sudo is required for this step)..."
  sudo dnf install -y \
    papirus-icon-theme papirus-icon-theme-dark papirus-icon-theme-light \
    adw-gtk3-theme google-noto-sans-fonts jetbrains-mono-fonts \
    gnome-extensions-app gnome-shell-extension-user-theme
else
  kuhl_warn "Skipping package installation by request; install packages later for best results."
fi

mkdir -p "$KUHL_DATA/wallpapers" "$KUHL_STATE" "$HOME/.local/bin" "$KUHL_APPS" "$KUHL_DATA/config"
install -m 644 "$ROOT/assets/wallpapers/kuhl-day.png" "$KUHL_DATA/wallpapers/kuhl-day.png"
install -m 644 "$ROOT/assets/wallpapers/kuhl-dusk.png" "$KUHL_DATA/wallpapers/kuhl-dusk.png"
install -m 644 "$ROOT/lib/common.sh" "$KUHL_DATA/common.sh"
install -m 755 "$ROOT/bin/kuhl" "$KUHL_BIN"
install -m 755 "$ROOT/scripts/extensions.py" "$KUHL_DATA/extensions.py"
install -m 644 "$ROOT/config/extensions.tsv" "$KUHL_DATA/config/extensions.tsv"
install -m 644 "$ROOT/config/effects.tsv" "$KUHL_DATA/config/effects.tsv"
# Kuhl theme files are original CSS, not downloaded third-party code.
for name in Day Dusk; do
  target="$HOME/.themes/Kuhl-$name"
  if [[ -d "$target" && ! -f "$target/.kuhl-owned" ]]; then
    kuhl_warn "A theme already exists at $target; leaving it intact."
    continue
  fi
  mkdir -p "$target/gnome-shell"
  install -m 644 "$ROOT/assets/themes/Kuhl-$name/gnome-shell/gnome-shell.css" "$target/gnome-shell/gnome-shell.css"
  touch "$target/.kuhl-owned"
done
# User Themes is an official Fedora extension provided by DNF; on some sessions
# GNOME will not see it until the next login. Save the change we made to its status.
if (( INSTALL_PACKAGES )) && command -v gnome-extensions >/dev/null 2>&1; then
  uuid='user-theme@gnome-shell-extensions.gcampax.github.com'
  if ! gnome-extensions list --enabled 2>/dev/null | grep -Fxq "$uuid"; then
    if gnome-extensions enable "$uuid" 2>/dev/null; then
      printf '%s\n' "$uuid" > "$KUHL_STATE/enabled-user-theme.txt"
    else
      kuhl_warn 'User Themes may need to be enabled in Extensions after logging out/in.'
    fi
  fi
fi

kuhl_info "Applying GNOME preferences (original settings are backed up)..."
kuhl_set org.gnome.desktop.background picture-uri "$(kuhl_quote "file://$KUHL_DATA/wallpapers/kuhl-day.png")"
kuhl_set org.gnome.desktop.background picture-uri-dark "$(kuhl_quote "file://$KUHL_DATA/wallpapers/kuhl-dusk.png")"
kuhl_set org.gnome.desktop.interface accent-color "'orange'"
kuhl_set org.gnome.desktop.interface cursor-theme "'Adwaita'"
kuhl_set org.gnome.desktop.interface font-name "'Noto Sans 11'"
kuhl_set org.gnome.desktop.interface document-font-name "'Noto Sans 11'"
kuhl_set org.gnome.desktop.interface monospace-font-name "'JetBrains Mono 11'"
kuhl_set org.gnome.desktop.wm.preferences titlebar-font "'Noto Sans Bold 11'"

# Use GNOME's native Overview rather than relying on a GNOME Shell extension.
# Preserve the user's existing shortcuts while adding Ctrl+Space.
if kuhl_key_exists org.gnome.shell.keybindings toggle-overview; then
  old_keys="$(gsettings get org.gnome.shell.keybindings toggle-overview)"
  new_keys="$(python3 - "$old_keys" <<'PY'
import ast, sys
keys = ast.literal_eval(sys.argv[1])
assert isinstance(keys, list)
if '<Control>space' not in keys:
    keys.insert(0, '<Control>space')
print(repr(keys))
PY
)"
  kuhl_set org.gnome.shell.keybindings toggle-overview "$new_keys"
else
  kuhl_warn "Could not enable Ctrl+Space: no toggle-overview key available."
fi
kuhl_theme "$THEME"
if [[ "$PROFILE" != none ]]; then
  kuhl_info "Installing compatible GNOME extensions ($PROFILE profile); they run as your user."
  python3 "$KUHL_DATA/extensions.py" install --profile "$PROFILE" --config "$KUHL_DATA/config" || \
    kuhl_warn 'Some extensions could not be installed; the base desktop still works.'
fi

# Simple app-launcher entries: no background services or extensions.
for theme in day dusk; do
  display="${theme^}"
  cat > "$KUHL_APPS/kuhl-$theme.desktop" <<ENTRY
[Desktop Entry]
Type=Application
Name=Kuhl $display
GenericName=Kuhl OS appearance
Comment=Switch Kuhl OS to its $display look
Exec="$KUHL_BIN" theme $theme
Icon=preferences-desktop-theme
Terminal=false
Categories=Settings;DesktopSettings;
Keywords=Kuhl;Theme;$display;
ENTRY
done
kuhl_info "Installed Kuhl OS ($THEME / $PROFILE). Run: ~/.local/bin/kuhl doctor"
kuhl_info "Log out and back in, then open Extensions to confirm the add-ons are enabled."
