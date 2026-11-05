# AmethystOS

**A keyboard-first Fedora desktop powered by Niri and Noctalia.**

AmethystOS installs a curated desktop experience onto Fedora Workstation. It
is not yet a separate bootable distribution. Your existing GNOME login stays
available as a fallback.

## Install

1. Start with Fedora Workstation 44 or newer.
2. Review [the installer](install.sh) and [security notes](docs/SECURITY.md).
3. Run the single public command:

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/AmethystOS/main/bootstrap.sh | bash
```

This downloads and runs code from GitHub. Review the scripts before trusting them.
The terminal installer uses **↑/↓ to navigate**, **Space** to select individual
apps, and **Enter** to continue. It also asks before replacing existing
configs and saves backups. Optional Flathub apps require your selection.

To use a reviewed local checkout:

```bash
bash install.sh --dry-run
bash install.sh
```

## The desktop

| | Component |
|---|---|
| Linux base | Fedora Workstation (GNOME retained) |
| Compositor | Niri with five named workspaces and keyboard navigation |
| Desktop shell | Stable Noctalia v5 (bar, launcher, calendar, notifications, settings) |
| Terminal | Kitty; Fish and Fastfetch configs available |
| Wallpapers | Amethyst Dark and Light |
| First login | AmethystOS Welcome (dismissible; optional show-at-login) |
| System updates | `amethyst-update` |
| Recovery | `amethystos-uninstall --dry-run`, then `amethystos-uninstall` |
| Login screen | Optional Noctalia Greeter (GDM retained for recovery) |

## Optional matching login screen

To replace the GNOME/GDM sign-in screen with **Noctalia Greeter** using the
Amethyst wallpaper and synced Noctalia palette, follow the
[greeter installation and recovery guide](docs/GREETER.md). This is an
**opt-in system-level change**, never made during the normal installer.
GNOMEs login screen will still be available.

## Useful shortcuts

| Shortcut | Action |
|---|---|
| Super+Space | Toggle the app launcher |
| Super+D | Open the same launcher bc I had this as another feature |
| Super+Shift+S | Open settings |
| Ctrl+Super+K | Open shortcuts guide |
| Super+W | Close the active window |
| Super+1–5 | Jump to permanent Niri workspaces |
| Super+T | Terminal |

See the [keybinding reference](wiki/keybinds.html) and [wiki](wiki/index.html).

## Development and security

The source is **AI-assisted**, not independently security
reviewed. Read installers before executing them, verify third-party software,
and keep backups. Fedora and Noctalia are maintained by their respective
upstream projects; AmethystOS is an independent desktop configuration.

[Installation guide](install.html) · [Security](docs/SECURITY.md) · [Migration](docs/NOCTALIA_V5_MIGRATION.md)

## Thanks
Thank you for checking AmethystOS out!