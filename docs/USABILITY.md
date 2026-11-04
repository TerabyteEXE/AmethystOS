# AmethystOS — daily use (RC2.8)

## The Home menu

- **Super+Space** or **Super+D**: open the same Amethyst Home panel.
- Start at **Home**, with Apps, Learn, Style, Setup, Install, Remove, Update,
  About, System and Power. Use **Up/Down** then **Enter/Right** to drill in.
- **Left** or **Backspace** with an *empty* search: return to Home.
- **Backspace/Delete with text in the search field:** edit the text normally.
  Ctrl+A, word deletion, selection and the text cursor remain handled by GTK.
- **Type to search**. At Home, search combines installed apps and built-in
  actions. Inside Apps or another category, search stays inside that category.
- The **Home panel stays narrow and minimal**, with no greeting, branding header,
  descriptions or footer. Choosing Apps opens a wider single-column app list.
- **Esc** or pressing **Super+Space** again closes the panel.
- **Super+Shift+S** still opens Amethyst Settings directly.

The launcher only runs known project helpers or installed app desktop files.
Installing, removing and updating software still requires confirmation in the
existing software tools. A minimal Fuzzel fallback remains if GTK cannot load.

## The top bar

The original Waybar modules, geometry and colors are retained. Clicking the
clock opens a local calendar; audio shows your current output volume, network
shows connected Wi-Fi if reported, Bluetooth shows controller status, and the
gear shows appearance/scale details and Settings links. The popovers display
local status, not cloud calendar events. Clicking the same widget again closes
its popup; selecting another widget switches to that popup. **Esc** closes.

A separate GTK layer-shell popup is used when available; there is no direct
Waybar-widget embedding. Multimonitor alignment and nondefault bar positions
need manual testing. Light/Dark popups follow the same appearance preference
as Settings, and the original Amethyst wallpapers are not modified.

## Recovery and testing

Use `bash install.sh --dry-run` before installing and `bash tests/validate.sh`
for portable checks. Niri and GTK rendering still need testing in Fedora. Keep
GNOME available as a fallback, and use `amethystos-uninstall --dry-run` to
inspect what restoration would change before running it.
