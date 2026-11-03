#!/usr/bin/env bash
# AmethystOS Base v1 — Fedora package manifest and install operation.
# Only official, already-enabled DNF repositories are used.
# Keep this file sourceable so the package transaction can be tested offline.

AMETHYSTOS_REQUIRED=(
  niri xwayland-satellite waybar fuzzel mako swaybg
  alacritty kitty gtklock polkit-kde
  xdg-desktop-portal-gnome xdg-desktop-portal-gtk gnome-keyring
  NetworkManager network-manager-applet nm-connection-editor
  nautilus firefox pavucontrol playerctl brightnessctl
  wl-clipboard cliphist pipewire wireplumber pipewire-pulseaudio
  bluez libnotify jq gtk3 fish
)

# None of these is essential for starting a working Niri desktop.
# Starship is intentionally optional: Fedora may need a separate COPR for it.
# Fish initialization already checks for the executable before loading it.
AMETHYSTOS_OPTIONAL=(
  starship fastfetch papirus-icon-theme-dark adw-gtk3-theme
  cascadia-code-nf-fonts btop cava qt6ct nwg-look grim slurp zoxide
)

amethystos_install_fedora_packages() {
  printf 'Installing %s essential Fedora packages (sudo required once).\n' "${#AMETHYSTOS_REQUIRED[@]}"
  sudo dnf install -y "${AMETHYSTOS_REQUIRED[@]}"
  printf 'Installing optional desktop extras where available.\n'
  # Fedora 44 uses DNF5. --skip-unavailable allows the optional package group
  # to continue even if (for example) Starship has no candidate in enabled repos.
  if ! sudo dnf install -y --skip-unavailable "${AMETHYSTOS_OPTIONAL[@]}"; then
    printf '%s\n' 'WARNING: Optional desktop extras could not all be installed.' \
      'The essential Niri desktop packages succeeded; continuing.' >&2
  fi
  if ! command -v starship >/dev/null 2>&1; then
    printf '%s\n' 'Note: Starship is unavailable in your enabled repositories.' \
      'Fish will use its normal prompt. Starship can be installed later if desired.'
  fi
}
