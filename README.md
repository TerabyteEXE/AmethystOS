# AmethystOS — Niri + Gigi's Rice (RC3 beta)

**AmethystOS** is a Fedora Workstation desktop setup with the [Gigi's Rice](https://github.com/deadduck-09/gigis-rice) **MIT-licensed Niri configuration and Noctalia Shell v4**. The original Gigi layout, window effects, plugins, and desktop shell are retained; Fedora-specific startup fixes and Amethyst purple branding are applied. This is **not yet a separate ISO/distribution**.

**Important compatibility warning:** Gigi's Rice is archived and targets **Noctalia Shell v4.7.7**. Fedora 44's official `noctalia` package is v5 and **cannot run Gigi's v4 configs unchanged**. You must install the **legacy v4 shell**, which may require a third-party package repository. We will not silently enable one. [Read the installation caveat](docs/GIGI_MIGRATION.md).

## Install

1. Install Fedora Workstation (GNOME remains available as a fallback).
2. Review `bootstrap.sh`, `install.sh`, `scripts/packages.sh`, and the [security notes](docs/SECURITY.md).
3. Install AmethystOS:

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/AmethystOS/main/bootstrap.sh | bash
```

On a fresh Fedora machine, you may need to approve an external package source to install Noctalia v4. The installer **stops rather than installing the incompatible Noctalia v5**. To explicitly allow the third-party Terra bootstrap, use a reviewed local checkout:

```bash
bash install.sh --allow-terra
```

On an existing AmethystOS install, choose **replace existing configuration with backup**. Test first: `bash install.sh --dry-run`.

## What you get

| | Program |
|---|---|
| Window manager | Niri (Gigi's window geometry, animations and layout) |
| Desktop shell | **Noctalia Shell v4.7.7** (bar, launcher, popups, wallpaper, control center, lock) |
| Terminal | Kitty (Gigi's config; Amethyst colors and packaged font fallbacks) |
| Other tools | Fish, Fastfetch, MPV, MPD, rmpc, Yazi, Neovim configurations |
| Wallpapers | Amethyst Dark and Light originals only (no third-party wallpapers) |
| OS updater | `amethyst-update` (Fedora, user Flatpaks, explicit source update) |
| Recovery | `amethystos-uninstall --dry-run` and `amethystos-uninstall` |

**No overlapping Waybar/Mako/Fuzzel launcher or old GTK popups.** The Noctalia shell provides those functions. Noctalia Settings owns bar, colors, widgets and wallpaper choice.

## Common shortcuts

| Keys | Action |
|---|---|
| **Super + Space** | Noctalia app launcher |
| **Super + D** | Same launcher |
| **Super + Shift + S** | Shell settings |
| **Super + Shift + W** | Wallpaper picker |
| **Ctrl + Super + K** | Keybinding reference |
| **Super + W** | Close active window |
| **Super + 1–5** | Named Niri workspaces |
| **Super + T** | Kitty terminal |

The full [keybinding reference](wiki/keybinds.html) is generated from the actual Gigi-derived Niri module.

## Licensing and authorship

- Gigi's original dotfiles by **Gigi / deadduck-09**, MIT; full license in [`LICENSE.gigi`](LICENSE.gigi) and original README in [`third_party/gigis-rice`](third_party/gigis-rice).
- Noctalia Shell and any bundled Noctalia plugins are separate upstream projects, with their own respective licenses and dependencies. Plugin metadata and included license files are retained. Not all artwork/media found in Gigi's repository has verified redistribution rights; the original anime wallpapers and demo videos are excluded.
- The original AmethystOS crystal logo and AmethystDark/AmethystLight wallpapers remain part of this project. The previous AmethystOS license and prior upstream attribution are also retained.

This is **AI-assisted experimental software, not security audited**. It can execute installation scripts and change user configs. Inspect the source and maintain an external backup before use. See [migration and limitations](docs/GIGI_MIGRATION.md) and [security](docs/SECURITY.md).
