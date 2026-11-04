# AmethystOS v1 RC2.4 — Settings and usability

This incremental build keeps the existing Niri rice. It consolidates launcher
actions into a single **Amethyst Settings** application using system GTK3
widgets, grouped into Overview, Appearance, Top bar, Devices, Desktop,
Software and System pages. The GTK UI remains open while applying bar and
appearance settings. Both `python3-gobject` and `gtk3` are already essential
Fedora dependencies. Fuzzel remains a fallback if GTK is unavailable.

The standalone AmethystOS desktop entries for install/remove/update,
control menu, wallpapers, calendar and bar settings now have `NoDisplay=true`,
so they remain callable by keyboard, menus and scripts without bloating search.
Super+D opens a concise six-item quick menu. Super+Shift+S or the Waybar gear
opens Settings, and Super+Alt+B or right-clicking the gear opens its Top Bar page.

- **Super+W** closes the focused window (replacing Super+Q).
- **Super+Shift+Tab** toggles tabbed-column display (previously Super+W).
- **Super+Space** still toggles Fuzzel and now searches applications.
- The website keybinding guide is regenerated directly from the revised KDL.

## How to upgrade

From your updated repository, run `bash install.sh` and choose replacement with
backups. You must log out and back into Niri for the newly deployed shortcuts
and `.desktop` entries to be reliably picked up. Your Light/Dark settings,
wallpaper selection, and original backup state are preserved.

## Release gate

Portable tests check deployed files, menu fallback iteration, launcher entries,
config safety and keybinding documentation. They **cannot** prove actual GTK
rendering, Waybar focus behavior or Fedora GPU integration. Check those in a
real Fedora Niri session before calling this stable.
