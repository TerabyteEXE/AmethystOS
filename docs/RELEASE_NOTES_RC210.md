# AmethystOS v1 RC2.10 — Readability and cohesion

RC2.10 is a focused refinement of the working RC2.9 Niri desktop, **not** a desktop reset. It retains the existing wallpapers and keyboard workflow.

## Changes

- **Actual UI scale in the custom apps.** The `amethyst-scale` preference now affects Amethyst Home, the Settings app, the Waybar popovers/calendar, and the wallpaper gallery. Previously those programs used hard-coded font and control sizes, unlike the terminal and Waybar themes.
- **Readable defaults.** Enlarged the launcher search/rows/icons, popup captions/buttons, small bar labels and Settings hit targets. The menu stays compact, and at higher scales its geometry is capped to fit the monitor's usable area.
- **Theme continuity.** Shared dark/light Amethyst purple accents across the Home selection, Settings sidebar, bar panels, wallpaper picker, and a small theme-colored Waybar gem icon. Existing background colors and wallpapers remain unchanged.
- **GTK4 repair.** Removed Windows-format `IntxLNK` shortcut bytes masquerading as GTK4 CSS. Replaced them with small, valid Light/Dark GTK4 accent definitions that are managed by the reversible theme system. Native GTK4/libadwaita widget layout is intentionally not overridden.
- **Waybar scaling.** Density preferences now account for the active UI-scale percentage, instead of overriding scaled font sizes with a fixed 11/13/15px value.
- **Startup correctness.** The launcher now loads its saved scale before trying to size its window.
- **Regression checks.** New tests verify GUI scale rules, window bounds, theme files, source deployment, startup order, Waybar scale, and undo/restore.

## Quick test on Fedora

1. Back up your working RC2.9 setup and install RC2.10 using the existing `bash install.sh` flow with explicit config replacement/backups.
2. Log into Niri and open **Super+Space**. Check the menu, typing, Backspace, scroll selection and app icons.
3. Open Settings (Super+Shift+S), try **Appearance > Text and UI: 100%, 125%, 150%**, and reopen Home, wallpaper gallery and Waybar calendar. Check that no controls get cropped at your display resolution.
4. Switch Light/Dark. Confirm Amethyst Dark/Light backgrounds and the gem/accent remain legible.
5. Check one GTK3 and one GTK4 app. Toolkit/Flatpak/Electron app-specific theming is still separate, so do not expect every external app to have identical decorations.
6. Verify the Waybar widgets, Niri workspaces, Settings, GNOME fallback and `amethystos-uninstall --dry-run`.

## Limits and rollback

This release was checked with portable source tests and archive tests, **not** a live Fedora/Niri graphical session. GTK rendering, application theme coverage, focus and blur still need testing on real hardware. `amethystos-uninstall` restores backed-up configuration files, but will refuse to overwrite manually modified managed files. The installer does not replace the Fedora boot manager or GNOME.
