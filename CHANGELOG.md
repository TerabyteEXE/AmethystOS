# Kuhl OS changelog

## v1.0-rc1 — Direct KyleOS Rice Edition (2026-11-03)

- Ported the MIT-licensed KyleOS Niri configuration, window animation shader, layout, theme files, Waybar status-line layout, Rofi appearance and Alacritty theme configurations as actual source files.
- Retained Kuhl-specific Control Center, keyboard guide, six theme options, one-command installer, GNOME fallback, and safe config replacement/restore features.
- Applied minimal compatibility fixes for Fedora (relative Niri includes, personal output rules removed, malformed urgent-color fixed, valid Waybar layer, arch-specific shell scripts replaced).
- Added source code attribution, untouched upstream config copies, original animated wallpapers and thumbnails under CC BY-NC-SA 3.0, detailed noncommercial artwork credits and licensing warnings.
- Kept the established minimalist website layout, correcting desktop descriptions and disclosures.
- Added an isolated test suite checking actual theme-byte equivalence, full 107-key guide, user config protection and original source provenance.

### Known release gates

- Native Niri KDL validation happens in Fedora CI or on a Fedora PC (`python3 scripts/validate_niri.py`), not in the current build environment.
- Live Fedora/Niri login, Rofi window rendering, Waybar, Mako, multimedia and multi-monitor setup still require manual verification.
- Original KyleOS Nerd Fonts, GTK and icon pack are **not** bundled, so typography/icons cannot be promised pixel-identical. The four animated GIF wallpapers are bundled but require an optional external wallpaper daemon; static PNG versions work with swaybg immediately.
- This is AI-assisted code, not security audited. Do not publish as a stable v1 release until the v1 acceptance checklist is completed.
