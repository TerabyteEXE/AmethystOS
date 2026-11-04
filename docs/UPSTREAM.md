# Original work and adaptations

**Source:** [New Niri Minimal Dots](https://github.com/youngcoder45/New-Niri-minimal-dots) by [Aditya Verma / youngcoder45](https://github.com/youngcoder45). The original `LICENSE` grants MIT rights; its text is included unchanged in `LICENSE.upstream` and `LICENSE` (copyright © 2026 Aditya Verma). The code and config files within `payload/` originate from the user-supplied `New-Niri-minimal-dots-main.zip`, with modifications listed below. The repository's upstream scripts remain the copyrighted work of their author.

**Adaptations for Fedora, not a redesign:**
- `niri/autostart.sh`: keep Waybar, Mako, clipboard and swaybg; remove the forced GNOME screencast portal killing, replace unavailable Arch Polkit binary, and avoid duplicate keyring process.
- `niri/config.kdl`: use supported shell startup action and system cursor fallback; keep includes, geometry, animations and layouts.
- `niri/keybinds.kdl`: remove bindings for apps not part of this base (Vesktop, VS Code, Zed); use built-in Niri screenshot; keep window keys and launcher keys.
- `waybar/scripts/powermenu.sh` and `local-bin/powermenu`: replace unavailable `niri-lock` program with the included GTKLock wrapper; keep visual menu.
- `niri-lock/`: fix GTKLock launch and remove a lockscreen wallpaper path pointing to an image not included.
- `xdg-desktop-portal/niri-portals.conf`: route portal features to Fedora's GNOME/GTK backends without interfering with GNOME session's own settings.
- `local-bin/set-wallpaper`: safely list unusual filenames and use swaybg rather than guessing which external setter to run.
- `waybar/style.css` and `kitty/kitty.conf`: Fedora-packaged Nerd Font fallback; keep the upstream palette and layout.
- `gtk-3.0`, `gtk-4.0`, `qt6ct`: use available cursor/style fallbacks; remove stale modules and fixed global DPI.
- `fish/config.fish`: preserve interactive Fish/Starship styling while dropping personal development paths, forced locale, forced TERM, and user-specific variables; do not change the account default shell.
- Removed source's non-Linux Windows `.lnk` placeholder, original wallpapers with unverified rights, personal shell paths, Arch branding, unrelated dev applications, shell swap and Arch package installer.

**Package code** is not embedded. Fedora distributes Niri, Waybar, Fuzzel, and the other installed applications under their own licenses. Their upstream projects are credited in the original source README at the source URL.

## AmethystOS v1 polish adaptations

Replaced unavailable fonts with Fedora's Cascadia Mono NF; increased terminal
text sizes; added complete GNOME/GTK and Qt6 appearance integration, a small
settings menu, proper Waybar settings/tray actions, browser fallback shortcuts,
a reversible installer UI and an optional application manifest. These are
AmethystOS-specific additions to the MIT-licensed source configuration.
