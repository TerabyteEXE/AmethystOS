# Kuhl OS — Base v1 (Niri)

**One desktop. One installer. No extras.**

Kuhl OS v1 is a **Fedora Workstation + Niri configuration/installer**, not a separately built Linux distribution or ISO. This fresh repository installs an adapted version of **[New Niri Minimal Dots](https://github.com/youngcoder45/New-Niri-minimal-dots)** by Aditya Verma. It does not include the previous Kuhl website, themes, control center, custom launchers, or old repository code.

## Install on Fedora Workstation

After publishing this repository to `TerabyteEXE/Kuhl-OS` on `main`:

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
```

**Read scripts before running a remote command.** This command downloads and executes the latest source from GitHub; it is *not pinned to a commit*. For a safer manual installation, download the ZIP, inspect its scripts, then run `bash install.sh`.

The installer uses **official Fedora packages**, checks free disk space, validates the Niri configuration with `niri validate` on Fedora, backs up existing dotfiles before replacing them, and **does not** remove GNOME or alter the default shell or login manager. An existing desktop prompts for backup-and-replace confirmation.

When installation finishes, **log out, select Niri at the login screen**, then log back in.

## Keybindings from the original Niri setup

| Action | Keys |
|---|---|
| Terminal | `Super + Enter` |
| App search | `Super + Space` |
| Close focused window | `Super + Q` |
| Navigate columns | `Super + H` / `Super + L` |
| Next/previous workspace | `Super + Up` / `Super + Down` |
| Window overview | `Super + O` |
| Power menu | `Super + P` |
| Show Niri keyboard help | `Super + Shift + /` |

The original keymap is preserved as far as Fedora compatibility allows. No new Kuhl shortcut scheme has been layered on top. See `payload/niri/keybinds.kdl`.

## Wallpapers

The original bundled wallpaper photographs/illustrations are **not redistributed** because their separate artwork rights could not be verified. Add your own `.jpg`, `.png`, or `.webp` images to `~/Pictures/wallpapers/`, then use `~/.local/bin/set-wallpaper`. Until then, the session uses a neutral dark background. All other styling is derived from the source dotfiles.

## Install and recovery

```bash
bash install.sh --dry-run        # no changes
bash install.sh                  # Fedora native install
bash install.sh --replace        # back up + replace old configs
bash uninstall.sh                # restore previous configs (if unmodified)
bash tests/validate.sh           # portable tests + native Niri parser when present
```

Config backups live at `~/.local/state/kuhl-base-v1/backups/`. Packages are not uninstalled during restoration. GNOME remains available as a fallback. If you've edited Kuhl-managed configs since installation, restoration stops rather than deleting your changes.

## Scope

- Included: Niri, Waybar, Fuzzel, Mako, GTK/Qt appearance, terminal configuration, clipboard, power menu, wallpaper picker, screen lock, portals, and Fish/Starship terminal styling and optional btop/Cava styling.
- Excluded: old Kuhl projects and website, Arch/AUR installer, bundled wallpapers of uncertain rights, personally customized dev/game apps, shell changes, SDDM replacement, and automatic third-party repositories.
- Fedora-native adjustments: autostart and Polkit integration, session portals, paths and font fallback, GTK lock command, and removal of machine-specific/Arch-only launcher references.

## Credits and security

The desktop configuration is adapted from **New Niri Minimal Dots** by **Aditya Verma**, © 2026, MIT licensed. The exact original copyright/license text is in `LICENSE.upstream`. See `docs/UPSTREAM.md` for the original repository and the changes to the source.

**AI-assisted software; not security audited.** Inspect the installer, verify packages, maintain backups, and test in a VM/spare system before deploying to a daily driver. See `docs/SECURITY.md`.

## Status

**v1 base candidate, not a verified stable release.** Portable tests can run here; actual login, hardware support, and the Fedora-native Niri validation require a Fedora machine or the included Fedora CI workflow. See `docs/TESTING.md`.
