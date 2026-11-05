#!/usr/bin/env bash
# AmethystOS uses Niri + stable Noctalia v5 from Fedora official repositories.
# No third-party RPM repos are enabled automatically.
AMETHYSTOS_REQUIRED=(
  niri noctalia xwayland-satellite kitty nautilus firefox gnome-text-editor
  polkit-kde xdg-desktop-portal-gnome xdg-desktop-portal-gtk
  gnome-keyring NetworkManager network-manager-applet
  pavucontrol playerctl brightnessctl wl-clipboard cliphist
  pipewire wireplumber pipewire-pulseaudio bluez blueman
  jq gtk3 python3 python3-gobject ImageMagick git
  fish fastfetch mpv mpd neovim
  papirus-icon-theme papirus-icon-theme-dark
  google-noto-sans-fonts cascadia-mono-nf-fonts
)
AMETHYSTOS_OPTIONAL=(starship btop yazi rmpc celluloid qt6ct chafa zoxide)
declare -A AMETHYSTOS_APP_GROUPS=(
 [firefox]='firefox' [chromium]='chromium' [essentials]='gnome-calculator gnome-text-editor file-roller'
 [office]='libreoffice-writer thunderbird' [creative]='gimp inkscape krita'
 [dev]='git micro neovim python3-pip' [media]='celluloid rhythmbox'
 [gaming]='lutris gamemode mangohud' [steam]='' [obs]='' [discord]='' [flatseal]=''
 [libreoffice]='libreoffice-writer libreoffice-calc' [thunderbird]='thunderbird'
 [gimp]='gimp' [krita]='krita' [inkscape]='inkscape' [kdenlive]='kdenlive'
 [audacity]='audacity' [git]='git' [neovim]='neovim' [lutris]='lutris gamemode'
 [celluloid]='celluloid' [rhythmbox]='rhythmbox' [btop]='btop'
 [calculator]='gnome-calculator' [archive]='file-roller' [micro]='micro' [vscode]=''
)

amethystos_install_fedora_packages() {
  # Treat an explicit empty string as "no optional apps", not the default group.
  # The installer always passes the user's choice, including "" for none.
  local groups="${1-firefox,essentials}" group
  echo 'Installing Fedora Niri desktop, graphics and Noctalia dependencies.'
  sudo dnf install -y "${AMETHYSTOS_REQUIRED[@]}" || return
  # Noctalia v5 is installed from Fedora's signed official repository above.
  sudo dnf install -y --skip-unavailable "${AMETHYSTOS_OPTIONAL[@]}" || echo 'Optional extras skipped.' >&2
  local -a pkgs=() selected=() parts=() flatapps=()
  IFS=',' read -r -a selected <<< "$groups"
  for group in "${selected[@]}"; do
    [[ -n "$group" ]] || continue
    if [[ ! -v "AMETHYSTOS_APP_GROUPS[$group]" ]]; then echo "Unknown app group: $group" >&2; return 2; fi
    read -r -a parts <<< "${AMETHYSTOS_APP_GROUPS[$group]}"
    pkgs+=("${parts[@]}")
  done
  if ((${#pkgs[@]})); then sudo dnf install -y --skip-unavailable "${pkgs[@]}" || echo 'Some optional apps unavailable.' >&2; fi
  [[ ",$groups," == *,steam,* ]] && flatapps+=(com.valvesoftware.Steam)
  [[ ",$groups," == *,obs,* ]] && flatapps+=(com.obsproject.Studio)
  [[ ",$groups," == *,discord,* ]] && flatapps+=(com.discordapp.Discord)
  [[ ",$groups," == *,flatseal,* ]] && flatapps+=(com.github.tchx84.Flatseal)
  [[ ",$groups," == *,vscode,* ]] && flatapps+=(com.vscodium.codium)
  if ((${#flatapps[@]})); then
    command -v flatpak >/dev/null || sudo dnf install -y flatpak
    flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo || return
    for app in "${flatapps[@]}"; do flatpak install --user -y --noninteractive flathub "$app" || echo "Skipped $app" >&2; done
  fi
}
