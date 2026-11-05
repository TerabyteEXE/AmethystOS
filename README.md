# AmethystOS

**A keyboard-first Fedora desktop powered by Niri and Noctalia.**

AmethystOS installs a curated desktop experience onto Fedora Workstation. It
is not yet a separate bootable distribution. Your existing GNOME login stays
available as a fallback. The project uses original AmethystOS crystal
branding, light/dark wallpapers, and a clean, accessible setup.

> **RC4 migration preview.** This release moves to the stable Noctalia **v5**
> package from Fedora 44's official repositories. Noctalia v4 settings and
> plugins cannot be used unchanged. Back up your working RC3.1 configuration
> and read [the v5 migration notes](docs/NOCTALIA_V5_MIGRATION.md) before
> upgrading. A fresh graphical Fedora/Niri test is still required.

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

Noctalia v5 uses its own TOML configuration. Its saved graphical preferences
are **not** migrated from v4; AmethystOS installs a new custom palette with
its own purple accent. The original Niri window layout and core shortcuts
remain, but shell command bindings use the new `noctalia msg` interface.

## Useful shortcuts

| Shortcut | Action |
|---|---|
| Super+Space | Toggle the app launcher |
| Super+D | Open the same launcher |
| Super+Shift+S | Open settings |
| Ctrl+Super+K | Open shortcuts guide |
| Super+W | Close the active window |
| Super+1–5 | Jump to permanent Niri workspaces |
| Super+T | Terminal |

See the [keybinding reference](wiki/keybinds.html) and [wiki](wiki/index.html).

## Development and security

The source is **AI-assisted and experimental**, not independently security
reviewed. Read installers before executing them, verify third-party software,
and keep backups. Fedora and Noctalia are maintained by their respective
upstream projects; AmethystOS is an independent desktop configuration.

[Installation guide](install.html) · [Security](docs/SECURITY.md) · [Migration](docs/NOCTALIA_V5_MIGRATION.md)

## Attribution and licenses

This project incorporates Niri dotfiles from **Gigi's Rice by Gigi / deadduck-09**
(2026), used under the MIT license. The original license is preserved in
[`third_party/gigis-rice/LICENSE`](third_party/gigis-rice/LICENSE) and
[`LICENSE.gigi`](LICENSE.gigi), with original source material retained for
reference. Noctalia, Fedora, and other components are separate projects with
their own licenses. The bundled AmethystOS wallpapers and logo are project
artwork, not part of those third-party MIT grants.
