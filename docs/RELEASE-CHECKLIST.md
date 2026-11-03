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
