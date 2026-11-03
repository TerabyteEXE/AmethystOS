# Kuhl OS 0.8 — Frontier rice specification

This design is inspired by [KyleOS](https://github.com/Person-008/KyleOS) (MIT code by Rosenkranz/Person-008) and includes CC BY-NC-SA artwork by PrisonerCoin. **See `docs/CREDITS.md` for licenses and modifications.**

- Full-width, 29px, top-anchored Waybar with minimal status text, workspaces at left, date/time centered, tools at right.
- Niri scrolling tiling with 16px gaps, focused ring, and asymmetric corner geometry `20 0 40 0`; terminals get `10 0 40 0`.
- Rofi desktop launcher with clipped-corner theme and a 3x2 artwork gallery for `Super+Shift+T`. Optional Vicinae is retained, Fuzzel remains installed as fallback.
- Six color sets: `frontier` (default), `dyson`, `puncture`, `slowend`, plus legacy `day` and `dusk`.
- Theme-linked wallpaper is a **static modified frame** from the source GIF and licensed **CC BY-NC-SA 3.0**. Custom wallpapers override; old Kuhl wallpapers are optional.
- Every shortcut is mapped in `config/keys.json` and its Niri manifest. `Ctrl+Super+K` still opens the searchable guide; `Super+D` opens Kuhl Control Center.
- Fedora’s packaged apps and GNOME fallback are retained. No KyleOS system-level `/etc` files, fish auto-start behaviors, Arch-specific installer, shader animations, or per-monitor display IDs are imported.

**AI-assisted source, unaudited.** See `docs/SECURITY.md` and independently review before deployment.


## Release candidate direction
The original pixel-like KyleOS UI is now used directly for v1 RC in Niri, Waybar, Rofi, Alacritty and Mako. The previous Studio centered-pill appearance is no longer the default; this document describes an older concept kept for historical reference.
