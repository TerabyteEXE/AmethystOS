# AmethystOS — everyday controls (RC2.4)

The default Niri layout is unchanged. The interface is now organized around
**one Settings application** and a short quick-action menu.

## Launcher and menus

- **Super+Space** opens or closes the Fuzzel application search. It lists
  installed applications and a single **Amethyst Settings** entry, not a long
  series of maintenance launchers.
- **Super+D** opens a six-item keyboard-friendly quick menu: Applications,
  Settings, Software, Wallpapers, Calendar, and Power. Navigate with the arrow
  keys, filter by typing, and press Enter to choose.
- **Super+Shift+S** opens the categorized graphical Settings window.
- **Super+Alt+B** opens its **Top bar** page directly. Right-clicking the
  Waybar gear opens the same page; left-click opens the Settings overview.

## Settings categories

**Overview:** common tasks, wallpapers, calendar.

**Appearance:** light/dark theme, font and UI scaling, wallpaper browser,
GTK and Qt tools.

**Top bar:** change position, density, and visible modules. These controls
apply immediately **without closing the window**. Preferences persist through
Light/Dark theme changes. If a managed Waybar config was manually edited,
AmethystOS refuses to overwrite it and shows an error.

**Devices:** network connections, volume, Bluetooth. An unavailable tool is
reported as missing rather than silently failing.

**Desktop:** switch between the five named workspaces, open the calendar and
inspect Niri display information.

**Software:** launch the curated installer, uninstaller, or Fedora/Flatpak update
workflow. Transactions still require normal package-manager approval.

**System:** Niri shortcut overlay, diagnostics, optional boot splash and power.

The GTK3 Settings app requires Fedora `python3-gobject` and `gtk3`, already
included in the essential package list. Without GTK, a smaller Fuzzel/text
fallback remains available. System apps such as Qt, GTK4/libadwaita,
Flatpak and games can still have their own appearance preferences.

## Shortcuts

| Keys | Purpose |
| --- | --- |
| `Super+Space` | Search installed applications (toggle) |
| `Super+D` | Quick menu |
| `Super+Shift+S` | Amethyst Settings |
| `Super+Alt+B` | Top bar settings |
| `Super+Shift+W` | Wallpaper gallery |
| `Super+W` | Close focused window |
| `Super+Shift+Tab` | Toggle tabbed columns (moved from Super+W) |
| `Super+1–5` | Switch named workspaces |

The complete source-derived list is at `wiki/keybinds.html`.

## Troubleshooting

Use `amethyst-settings` from a terminal if the launcher entry appears broken;
look for GTK error messages. Run `amethyst-bar status` to inspect the saved
Waybar settings. If the GUI won't open, check that Fedora has `python3-gobject`
and `gtk3`, and use `amethyst-settings` in a terminal as a fallback.

`bash tests/validate.sh` tests the source files, CLI commands and deployment
safety. A real Fedora/Niri graphical session is still needed to verify GTK
rendering, popup focus, and Waybar interactions before a stable release.
