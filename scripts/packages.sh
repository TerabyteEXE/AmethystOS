#!/usr/bin/env bash
# The required desktop uses Fedora packages only, without COPR/RPM Fusion.
# Optional user-selected Flatpaks may add the Flathub remote explicitly.
AMETHYSTOS_REQUIRED=(
  niri xwayland-satellite waybar fuzzel mako swaybg
  alacritty kitty gtklock polkit-kde
  xdg-desktop-portal-gnome xdg-desktop-portal-gtk gnome-keyring
  NetworkManager network-manager-applet nm-connection-editor
  nautilus pavucontrol playerctl brightnessctl wl-clipboard cliphist
  pipewire wireplumber pipewire-pulseaudio bluez blueman libnotify jq gtk3 fish
  adw-gtk3-theme papirus-icon-theme papirus-icon-theme-dark qt6ct python3-gobject
  cascadia-mono-nf-fonts google-noto-sans-fonts
)
# These are cosmetic tools. Missing ones do NOT block the graphical desktop.
AMETHYSTOS_OPTIONAL=(starship fastfetch btop cava nwg-look gammastep grim slurp zoxide chafa)

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
  [steam]=''
  [obs]=''
  [discord]=''
  [flatseal]=''
  [libreoffice]='libreoffice-writer libreoffice-calc'
  [thunderbird]='thunderbird'
  [gimp]='gimp'
  [krita]='krita'
  [inkscape]='inkscape'
  [kdenlive]='kdenlive'
  [audacity]='audacity'
  [git]='git'
  [neovim]='neovim'
  [lutris]='lutris gamemode'
  [celluloid]='celluloid'
  [btop]='btop'
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
  # Third-party Flatpak sources are installed only when explicitly selected.
  # The remote is user-scoped; no surprise system-wide repo changes.
  local -a flatapps=()
  [[ ",$groups," == *,steam,* ]] && flatapps+=(com.valvesoftware.Steam)
  [[ ",$groups," == *,obs,* ]] && flatapps+=(com.obsproject.Studio)
  [[ ",$groups," == *,discord,* ]] && flatapps+=(com.discordapp.Discord)
  [[ ",$groups," == *,flatseal,* ]] && flatapps+=(com.github.tchx84.Flatseal)
  if ((${#flatapps[@]})); then
    if ! command -v flatpak >/dev/null 2>&1; then
      sudo dnf install -y flatpak || { echo 'Flatpak unavailable, skipping selected Flathub apps' >&2; return 0; }
    fi
    echo 'Selected Flathub applications require the Flathub user repository.'
    echo 'You explicitly selected them in the installer; adding Flathub for this user.'
    if ! flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo; then
      echo 'Flathub could not be added; skipping these optional applications.' >&2
      return 0
    fi
    for app in "${flatapps[@]}"; do
      flatpak install --user -y --noninteractive flathub "$app" || echo "Could not install optional Flatpak: $app" >&2
    done
  fi
}
