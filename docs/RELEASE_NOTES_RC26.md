# AmethystOS v1 RC2.6 · Desktop coherence beta

This is a conservative feature update based on the working RC2.5 configuration.

## What changes

- Super+Space opens one wider GTK application and command search with **All, Apps, Settings, Software, Wallpapers, System, and Power** filters. Navigate with arrows; Enter opens an item; Esc or Super+Space closes. Ctrl+1–7 selects a category.
- Super+D opens that **same** launcher, initially filtered to Settings. It is no longer a separate quick menu.
- Standard `.desktop` application launch commands use GIO (including Flatpak launchers). System commands are an explicit allowlist; software changes still require review and confirmation.
- Clicking clock/audio/network/Bluetooth/settings widgets opens compact matching GTK popups. If `gtk-layer-shell` is installed, those panels are anchored below Waybar. Without that optional library, they behave as regular small windows.
- Launcher and popups use the **existing Settings Light/Dark palettes** rather than a new visual theme.
- **Both original user-supplied Amethyst wallpapers are unchanged**, as are the Niri layout, Waybar geometry, installer/uninstaller, and existing settings backends.
- Fuzzel remains available as a lightweight launcher fallback if GTK can't load.

## Test before tagging

1. Run `bash tests/validate.sh` and `bash install.sh --dry-run` from the extracted archive.
2. In Fedora, run `niri validate` before logging into a new session.
3. Select *Replace existing configurations with backups* in `bash install.sh`, then log out and back into Niri.
4. Check Super+Space twice, Super+D, keyboard selection, app launches, themed search, clock/audio/network widgets, and Light/Dark.
5. Confirm both wallpapers remain exactly as before. Check `amethystos-uninstall --dry-run` before restoring.

### Known limits

The GTK launcher and layer-shell popups have **not been tested in a live Fedora/Niri graphical session** here. A Waybar click launches a small separate GTK layer surface, not a Waybar-native widget tree; focus/position can vary across compositor versions and multiple monitors. Some apps manage their own themes and will not exactly match GTK styling. We deliberately avoided adding glowing mockups, alternative wallpapers, or risky desktop-shell rewrites.
