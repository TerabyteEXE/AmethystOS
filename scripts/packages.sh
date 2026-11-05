#!/usr/bin/env bash
# Required packages come from Fedora 44 repos, except Noctalia v4 legacy.
# Noctalia v5 from Fedora is NOT compatible with this Gigi configuration.
AMETHYSTOS_REQUIRED=(
  niri xwayland-satellite kitty nautilus firefox gnome-text-editor
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
 [celluloid]='celluloid' [btop]='btop'
)

amethystos_install_legacy() {
  if rpm -q noctalia-legacy >/dev/null 2>&1 || rpm -q noctalia-shell >/dev/null 2>&1; then
    echo '[ok] Existing Noctalia legacy package detected.'; return
  fi
  if sudo dnf install -y noctalia-legacy; then return 0; fi
  echo >&2 'Noctalia v4.7.7 is required; Fedora noctalia v5 does not work with this rice.'
  echo >&2 'A third-party repository is needed for this archived shell. See docs/GIGI_MIGRATION.md.'
  if [[ ${AMETHYSTOS_ALLOW_TERRA:-0} != 1 ]]; then
    if [[ -r /dev/tty && ${AMETHYSTOS_NONINTERACTIVE:-0} != 1 ]]; then
      printf '\n%s\n' 'Noctalia v4 needs an external package provider.' >/dev/tty
      printf '%s\n' 'Read: https://docs.noctalia.dev/noctalia-shell-legacy/getting-started/installation/' >/dev/tty
      printf '%s\n' 'Terra bootstrap uses --nogpgcheck. Only proceed if you trust this source.' >/dev/tty
      printf 'Type TRUST TERRA to enable the third-party repository (or anything else to cancel): ' >/dev/tty
      IFS= read -r consent </dev/tty || consent=''
      [[ "$consent" == 'TRUST TERRA' ]] || { echo 'Declined external repository; stopping before dotfiles are installed.' >&2; return 1; }
    else
      echo >&2 'A third-party repository is required. For unattended install, review and pass --allow-terra explicitly.'
      return 1
    fi
  fi
  echo >&2 'Enabling Terra (third party) with explicit permission.'
  # This command comes from Noctalia legacy install documentation. The bootstrap RPM
  # bypasses signature checks: require explicit trust. Do not run via a pipe or without notice.
  sudo dnf install -y --nogpgcheck --repofrompath 'terra,https://repos.fyralabs.com/terra$releasever' terra-release || return
  sudo dnf install -y noctalia-legacy || sudo dnf install -y noctalia-shell
}
amethystos_install_fedora_packages() {
  # Treat an explicit empty string as "no optional apps", not the default group.
  # The installer always passes the user's choice, including "" for none.
  local groups="${1-firefox,essentials}" group
  echo 'Installing Fedora Niri desktop, graphics and Noctalia dependencies.'
  sudo dnf install -y "${AMETHYSTOS_REQUIRED[@]}" || return
  amethystos_install_legacy || return
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
  if ((${#flatapps[@]})); then
    command -v flatpak >/dev/null || sudo dnf install -y flatpak
    flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo || return
    for app in "${flatapps[@]}"; do flatpak install --user -y --noninteractive flathub "$app" || echo "Skipped $app" >&2; done
  fi
}
