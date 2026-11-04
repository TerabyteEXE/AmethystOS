#!/usr/bin/env bash
# No COPRs, AUR, RPM Fusion, Flatpak remotes or arbitrary installer scripts.
# The official Fedora repository is the only source used by this installer.
AMETHYSTOS_REQUIRED=(
  niri xwayland-satellite waybar fuzzel mako swaybg
  alacritty kitty gtklock polkit-kde
  xdg-desktop-portal-gnome xdg-desktop-portal-gtk gnome-keyring
  NetworkManager network-manager-applet nm-connection-editor
  nautilus pavucontrol playerctl brightnessctl wl-clipboard cliphist
  pipewire wireplumber pipewire-pulseaudio bluez blueman libnotify jq gtk3 fish
  adw-gtk3-theme papirus-icon-theme-dark qt6ct
  cascadia-mono-nf-fonts google-noto-sans-fonts
)
# These are cosmetic tools. Missing ones do NOT block the graphical desktop.
AMETHYSTOS_OPTIONAL=(starship fastfetch btop cava nwg-look gammastep grim slurp zoxide)

# Software chosen in the terminal UI; packages are from configured Fedora repos.
# This is intentionally not a general-purpose package-name input field.
declare -A AMETHYSTOS_APP_GROUPS=(
  [firefox]='firefox'
  [chromium]='chromium'
  [essentials]='gnome-calculator gnome-text-editor file-roller loupe'
  [office]='libreoffice-writer thunderbird'
  [creative]='gimp inkscape krita'
  [dev]='git micro neovim python3-pip'
  [media]='celluloid rhythmbox'
  [gaming]='lutris gamemode mangohud'
)

amethystos_install_fedora_packages() {
  local groups="${1:-firefox,essentials}" group
  printf 'Installing %s essential Fedora packages.\n' "${#AMETHYSTOS_REQUIRED[@]}"
  sudo dnf install -y "${AMETHYSTOS_REQUIRED[@]}" || return
  printf 'Installing optional desktop extras where available.\n'
  if ! sudo dnf install -y --skip-unavailable "${AMETHYSTOS_OPTIONAL[@]}"; then
    printf '%s\n' 'Optional system extras were unavailable; continuing.' >&2
  fi
  local -a pkgs=()
  local -a selected=()
  IFS=',' read -r -a selected <<< "$groups"
  for group in "${selected[@]}"; do
    [[ -n "$group" ]] || continue
    if [[ ! -v "AMETHYSTOS_APP_GROUPS[$group]" ]]; then
      echo "Unknown application group: $group" >&2; return 2
    fi
    local -a parts=()
    read -r -a parts <<< "${AMETHYSTOS_APP_GROUPS[$group]}"
    pkgs+=("${parts[@]}")
  done
  if ((${#pkgs[@]})); then
    printf 'Installing selected applications: %s\n' "${pkgs[*]}"
    if ! sudo dnf install -y --skip-unavailable "${pkgs[@]}"; then
      printf '%s\n' 'Some selected apps could not be installed. The desktop remains usable.' >&2
    fi
  fi
}
