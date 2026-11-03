# Kuhl OS 0.6.1 — Fedora + Niri

A warm, keyboard-first **Fedora Workstation + Niri desktop experience**. Kuhl is **not** a separate distribution, ISO, modified kernel, or package manager. It adds a Niri scrolling-tiling session to Fedora while keeping GNOME as a fallback.

> **Status: experimental developer preview.** Configuration is based on documented Niri 26.04 and Fedora 43–45 packaging; static and simulated tests pass. No physical Fedora installation or full GUI login has been executed in the build environment. Test in a VM or spare machine before daily driving.

Website: `main.html` (publish to your GitHub Pages repository). The website's desktop graphic is a concept illustration, **not a screenshot**.

## What changed from 0.5

- Replaced the old GNOME extension-dependent desktop with **Niri**: scrollable tiling, rounded corners, live-reloading KDL, and comfortable workspace shortcuts.
- Added **Waybar**, **Kitty**, **Mako**, **Swaybg**, **Swaylock**, **Swayidle**, **Fuzzel**, XWayland satellite and recommended XDG portals.
- **Super + Space** opens **Fuzzel** out of the box. Both launchers can find Kuhl Day and Kuhl Dusk as application entries. Optional **Vicinae** offers a more macOS/Raycast-style search experience with file indexing, actions and clipboard features.
- Kept the original Kuhl wallpapers and warm Day/Dusk aesthetic. `kuhl theme day|dusk` updates Niri's focus colors, bar, terminal, notifications, Fuzzel and the default wallpaper together. Theme entries also appear in application search.
- Removed obsolete GNOME-extension manifests, installer logic and misleading website copy. Kuhl does **not** disable GNOME or remove existing apps.
- Added non-destructive file ownership tracking, backups before explicitly requested replacement, and user-edit-aware uninstall.

## Requirements

Regular **Fedora Workstation 43 or newer**, x86_64; Fedora 44/45 are the primary targets, at least 8 GB RAM recommended, working Wayland-capable graphics and internet for package installation. Do not use on Silverblue/Kinoite or other rpm-ostree systems. Keep a functional GNOME session as a safety net.

No AI services, telemetry, scheduled jobs, proprietary drivers, alternate update daemon, or ISO build system are included.

## Install (review files first)

Use the downloaded ZIP or, **after publishing this updated code to your Kuhl-OS repo**:

```bash
git clone https://github.com/TerabyteEXE/Kuhl-OS.git
cd Kuhl-OS
bash tests/validate.sh
bash install.sh --dry-run
bash install.sh
```

Run `install.sh` as your **normal user**, not as root. A Python curses menu lets you choose Day/Dusk and optional apps. Fedora packages are installed via sudo as needed. The optional Vicinae COPR is **off by default** and, if chosen, requires typing `VICINAE` to authorize the extra repository.

When installation finishes, **log out**, choose **Niri** in GDM, and sign in. GNOME stays available on the same login screen. `kuhl doctor` checks required commands and validates your Niri config; `kuhl keys` prints the keybinding reference.

Already on old Kuhl GNOME v0.5? Install 0.6 as a separate Niri session. The GNOME theme, extension state, captured settings and old assets are **not automatically removed or reverted**. Back them up separately if you plan to retire the GNOME variant.

### Config collision protection

By default, Kuhl **never replaces existing** `~/.config/niri/config.kdl`, Waybar config, Kitty config, or Mako or Fuzzel config that it cannot identify as unchanged Kuhl-managed files. It prints a warning for preserved files. If you want Kuhl to own your existing Niri setup, review your dotfiles first and run:

```bash
bash install.sh --replace-configs
```

Type `REPLACE` at the confirmation prompt; originals are backed up under `~/.local/state/kuhl/backups`. **Edited Kuhl-managed configs are also preserved on future installs** unless you explicitly request replacement. To add personal Niri customizations, edit your config and know that Kuhl will preserve it rather than silently overwriting it.

`--defaults` skips the menu and uses only Fedora-packaged components; it does not silently install Vicinae or Flathub apps. `--dry-run` shows all default selections without modifying your system and is runnable even on non-Fedora machines for review.

## Core keyboard shortcuts

| Action | Shortcut |
| --- | --- |
| Spotlight-style search (Vicinae or Fuzzel) | **Super + Space** |
| Terminal | Super + Enter / T |
| Files | Super + E |
| Focus left/right column | Super + H / L |
| Focus up/down | Super + K / J |
| Move column/window | Super + Ctrl + H/J/K/L |
| Workspace | Super + 1–5 |
| Move column to workspace | Super + Shift + 1–5 |
| Resize column | Super + R |
| Toggle floating | Super + V |
| Lock screen | Super + Shift + L |
| Quit window | Super + Shift + Q |
| Log out of Niri (confirmation) | Super + Shift + E |
| Screenshot | Print |

See `docs/KEYBINDS.md` for the full list and practical tips.

## Commands

```bash
kuhl theme day          # light palette and wallpaper
kuhl theme dusk         # warm dark palette and wallpaper
kuhl wallpaper day      # pin the Day wallpaper even in Dusk mode
kuhl wallpaper dusk     # pin Dusk wallpaper
kuhl wallpaper default  # use original Kuhl default wallpaper
kuhl status             # audit managed file state
kuhl doctor             # check programs / validate Niri config
kuhl keys               # printable hotkeys
kuhl uninstall          # remove only unchanged Kuhl-owned config files
```

To return to automatic theme-based wallpaper switching, remove `~/.local/state/kuhl/wallpaper-choice` or set its contents to `auto`, then run `kuhl wallpaper apply` in Niri.

## Safety and recovery

If Niri fails to start, use GDM's gear/session menu to log into **GNOME** instead. Review `~/.local/state/kuhl/install.log`, run `niri validate` and `kuhl doctor` from GNOME. If your existing Niri dotfiles conflicted, the installer intentionally left them in place; review the warning and decide whether to use `--replace-configs`. The installer validates both bundled Niri themes in isolation before deploying configs. If the active user Niri configuration is invalid afterwards, it stops without automatically deleting previously managed files. Use `kuhl uninstall` to restore tracked, unmodified files if needed.

`kuhl uninstall` removes or restores Kuhl-managed config files **only if they have not been modified since Kuhl generated them**. It retains RPMs, any enabled COPR, Flatpaks, the GNOME fallback, installed wallpapers, and backup/state logs to avoid deleting unrelated work. See `docs/RECOVERY.md` for manual cleanup.

For changes to the repo, start with `bash tests/validate.sh`. On Fedora, additionally run `python3 scripts/validate_niri.py`; this validates both themes with the real Niri parser, without touching user dotfiles. CI executes the Fedora/Niri check on every push/PR. A real Fedora guest is required to test login, workspace animations, portal screen sharing, input devices, notifications, suspend, X11 apps and battery behavior. See `docs/TESTING.md`.

## Project structure

```text
Kuhl-OS/
├── assets/                   # Original wallpapers and branding
├── bin/kuhl                  # Theme, diagnostics, search and recovery command
├── bootstrap.sh              # Optional GitHub source downloader
├── config/
│   ├── choices.json          # Terminal installer menu choices
│   └── themes.json           # Day/Dusk color tokens
├── configs/                  # Niri/Waybar/Kitty base configurations
├── docs/                     # Design, testing, keybindings and recovery
├── install.sh                # Fedora installer
├── lib/common.sh             # Installer environment helpers
├── main.html                 # Website, interactive launcher demo
├── scripts/menu.py           # Curses TUI
├── scripts/render.py         # Safe, manifest-backed config deployment
├── scripts/validate_niri.py  # Real Niri validation before config deployment
└── tests/validate.sh         # Static + isolated functional tests
```

### Sources and licenses

Niri: https://github.com/niri-wm/niri · Fedora packages: https://packages.fedoraproject.org/pkgs/niri/niri/ · Vicinae Fedora packaging: https://docs.vicinae.com/install/linux · Niri + Vicinae: https://docs.vicinae.com/quickstart/niri · Waybar: https://github.com/Alexays/Waybar

All these components are third-party software distributed under their respective licenses. Kuhl and its branding do not imply endorsement by Fedora, Red Hat, Niri, Vicinae or their maintainers. See `LICENSE` for the license of this repository's original code.

**Vicinae theming:** Kuhl installs a `kuhl-day.toml` or `kuhl-dusk.toml` theme file into your user Vicinae theme directory when you apply that palette. Use Vicinae’s **Set Theme** command if automatic selection does not take effect on your version.
