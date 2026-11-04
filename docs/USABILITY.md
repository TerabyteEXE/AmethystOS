# AmethystOS RC2.3 — Everyday desktop controls

This release retains the original Fedora/Niri window layout, styles and key
bindings except for two changes: Super+D is the new quick-actions menu, and
toggle-floating moves to Super+Shift+D to avoid a duplicate Niri binding.

## Search and commands

- **Super+Space**: open/close Fuzzel. Its normal desktop application search now
  includes searchable AmethystOS entries for Settings, install/remove software,
  updates, wallpapers, calendar and the top bar. **Esc** closes it as usual.
- **Super+D**: Amethyst quick-actions menu. Type to filter; use arrow keys and
  Enter to choose. No typing of arbitrary package names or commands.
- **Super+Shift+S**: Settings; **Super+Alt+B**: Waybar settings.
- **Super+Shift+W**: thumbnail wallpaper browser. Double-click or press Apply.

## Calendar and top bar

Hover the Waybar clock for the calendar tooltip and click it for a separate
calendar window. Right-click the Waybar gear icon for the bar settings menu;
choose top/bottom, compact/normal/roomy, or hide/show optional modules.

Preferences are stored at `~/.local/state/amethystos-base-v1/bar.json` and
reapplied after the Light/Dark theme changes. If you manually edit Waybar
files, AmethystOS will refuse to overwrite them until you reconcile your edits.
Use `amethyst-bar status` to inspect, or run `amethyst-bar menu`.

## Software manager

`amethyst-software install` and `amethyst-software remove` show a curated list
of Fedora packages and a few Flathub apps. DNF transactions are interactive
and show the actual package changes. External Flathub sources are explicitly
opt-in. The software menu does not remove AmethystOS system components.

`amethyst-software update` opens a terminal and runs Fedora updates (then
user Flatpak updates if Flatpak is installed). The commands work on Fedora,
not on every Linux distribution.

## Wallpaper browser

The GTK3 browser displays local PNG/JPEG/WebP pictures from
`~/Pictures/wallpapers/`, with a scrollable grid and thumbnail previews. It
reuses the existing `set-wallpaper --file` operation. If GTK or PyGObject is
missing, it falls back to Fuzzel's keyboard-only list. Default Amethyst Dark
and Light wallpapers stay intact, and personal wallpapers are never deleted.

## Limitations and testing

Automatic GUI styling is not universal: Qt, GTK4/libadwaita, Flatpak, Electron,
and individual games may retain independent settings. A live Fedora Niri login
and end-to-end app launches must be tested on your hardware before a stable v1.
The Super+Space toggle relies on Niri processing the keybinding while Fuzzel
has keyboard focus. If a particular session inhibits shortcuts, use Esc.

`bash tests/validate.sh` covers configuration, rollback, shortcuts and new
controller logic without a graphical session. Fedora CI installs Niri and
additionally checks the real compositor parser.
