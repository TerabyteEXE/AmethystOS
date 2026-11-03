# Kuhl OS 1.0 — release candidate acceptance checklist

Do **not** describe this project as stable or security-audited on the basis of the automated tests alone.

## Required on a clean Fedora 44 machine

- [ ] Review changed scripts, the [AI/security disclosure](SECURITY.md), and the license boundaries in [CREDITS.md](CREDITS.md).
- [ ] Check disk space (`df -h /`) and make a backup before installation.
- [ ] In the extracted repository, run `bash tests/validate.sh` and `python3 scripts/validate_niri.py`.
- [ ] Run `bash install.sh` as a normal Fedora Workstation user. The test machine should retain GNOME as a fallback.
- [ ] Choose Niri at GDM. Confirm no blank screen, no crash, and correct monitor output. The copy of KyleOS's personal display mappings is NOT applied.
- [ ] Confirm the KyleOS status bar, asymmetric corners, Alacritty colors, Rofi search, notifications and wallpaper are visible.
- [ ] Test `Super+Space`, `Alt+K`, `Ctrl+Super+K`, `Super+D`, `Super+Enter`, `Super+E`, `Super+Shift+T`, lock/sleep, screenshots, volume and workspace controls.
- [ ] Test launcher from an older Kuhl deployment using the **replace and back up** installer option, followed by rollback with `kuhl uninstall`.
- [ ] Verify theme switching across all six themes, then use a custom wallpaper and reset it.
- [ ] Test `waybar` `mako` `rofi` logs, screen sharing, portals, audio, NetworkManager, sleep, resume, and multimonitor if relevant.
- [ ] Check whether the required Nerd Fonts for exact KyleOS font/icon appearance are installed; Kuhl does not ship third-party font binaries.
- [ ] Review all source credits and noncommercial artwork restrictions before tagging or commercial promotion.

## Must not ship as source-copied components

Do not import KyleOS's Arch/pacman installation script or `/etc`-wide configuration overlay. Do not copy machine-specific monitor coordinates, personal screenshot exclusions, unknown-license GUI icons or the Survey artwork. Do not merge the wallpapers with a general MIT label.

## After test failures

Use GNOME at GDM; run `niri validate`, `kuhl doctor`, and read `~/.local/state/kuhl/install.log`. Kuhl has a config restore function in `kuhl uninstall`; it does not undo DNF packages. Full backup and rollback guidance is in [RECOVERY.md](RECOVERY.md).

## RC2 additional acceptance checks — required before claiming v1 stable

- [ ] Open Kuhl Settings through the top bar **and** Super+Shift+S. Network, Sound, Bluetooth, and Display options must launch; missing peripherals should be handled gracefully.
- [ ] Change the Waybar to 85%, 125%, 150%; toggle a module, move bar bottom and back top. Confirm no clipping on 1366×768, 1920×1080 and any HiDPI monitors.
- [ ] Test the bar's **×** close button and Super+Q; confirm dialogs and standard GTK titlebar close buttons are available.
- [ ] Set UI text to 125%; confirm Alacritty, Kitty, Rofi, and supported GTK apps become readable without breaking tiling. Restore 100%.
- [ ] Run `kuhl display outputs`, then `kuhl display wizard`, try 125% on a known output, then `kuhl display reset` and confirm restoration.
- [ ] Switch between Day and Frontier; confirm Waybar, Rofi, terminal, notifications, Adwaita light/dark and Papirus icon preference change together.
- [ ] Confirm privileged settings actually show an authentication prompt from the polkit-kde agent; test Flatpak file dialogs and screencasting portals.
- [ ] On upgraded installations, check Kuhl's `~/.local/state/kuhl/backups/` and `kuhl uninstall` restore paths, including changes to previous GTK settings.
- [ ] Reboot and test a cold Niri login. Test a separate GNOME fallback login; do not remove GNOME.

**Known scope:** arbitrary third-party Qt, Electron, and web apps may ignore GNOME's GTK color preference. This is not a universal cross-toolkit theme engine. Real monitor changes depend on connected output names and hardware driver support. No static test can certify those behaviors.
