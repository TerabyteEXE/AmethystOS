# Kuhl Settings — user guide (v1.0 RC2)

The Kuhl Control Center is a **terminal-based settings interface** (Super+Shift+S, or the **Settings** item in Waybar). Unlike GNOME Settings, it is designed to operate in a standalone Niri session. The following controls work without rebuilding or reinstalling Kuhl.

| Command | What changes |
| --- | --- |
| `kuhl settings` | Interactive settings menu; access network, sound, Bluetooth, bar and display |
| `kuhl bar scale 125` | Bar height, type and click padding at 125% |
| `kuhl bar scale 85` | Compact 85% bar |
| `kuhl bar position bottom` | Relocate full-width bar to bottom |
| `kuhl bar module workspaces on` | Show workspace labels |
| `kuhl bar module close off` | Hide right-side close-window × button |
| `kuhl bar module battery off` | Hide laptop battery module on desktops |
| `kuhl bar reset` | Restore standard module selection, position and size |
| `kuhl ui scale 125` | Scale Rofi, Kitty, Alacritty and supported GTK text |
| `kuhl ui reset` | Return to 100% font scaling |
| `kuhl display outputs` | List detected Niri outputs |
| `kuhl display wizard` | Interactive display connector and scale picker |
| `kuhl display scale HDMI-A-1 1.25` | Set a specific display to 125% |
| `kuhl display reset` | Restore automatic Niri output scaling |
| `kuhl window close` | Close focused Niri window (same as Super+Q or the bar ×) |

**Do not confuse three separate scales:**

1. **Display scale** changes the logical resolution of one monitor through Niri. This affects Wayland clients including bar and windows. Use it when *everything* is too small or large on one monitor.
2. **UI scale** changes configured text sizes in terminals, launcher and GTK apps. It does not change monitor resolution.
3. **Bar scale** independently resizes the bar's controls and spacing, so you can use a slim top bar even with larger application fonts.

Display scale writes only to `~/.config/niri/output.kdl`, and validates a staged copy with `niri validate` before applying. It will **not** overwrite a manually edited output config. `kuhl display reset` removes Kuhl scale overrides and returns to Niri's automatic detection. It does not alter monitor mode or position.

Theme switching now coordinates Waybar, Rofi, Kitty, Alacritty, Mako, Fuzzel, GTK 3/4 Adwaita dark/light preference and Papirus icon choice. The GTK preference is per-user and may affect the GNOME fallback session too; Kuhl records the original settings and restores them on `kuhl uninstall` unless you changed them afterward. Qt and Electron apps may choose their own theme.

The bar uses the upstream full-width KyleOS design, with a small **Settings** and **×** control added for mouse users. The source templates in `configs/` and original MIT copies in `third_party/` remain available. User edits to Kuhl-managed configs are protected; upgrading with the installer **Replace existing desktop settings (with backups)** choice is required to regain Kuhl control of manually edited files.

## Troubleshooting

Run `kuhl doctor`, `niri validate`, and `kuhl status`. If a menu command doesn't launch, check `command -v nm-connection-editor pavucontrol blueman-manager` as appropriate. `sudo dnf install nm-connection-editor pavucontrol` adds basic network and audio settings; Blueman is optional. Keep GNOME as the fallback login until a clean Niri reboot is verified. Use `docs/RECOVERY.md` for rollback.
