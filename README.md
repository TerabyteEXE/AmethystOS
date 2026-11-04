<img src="assets/branding/amethyst-logo.png" alt="AmethystOS purple crystal logo" width="92">

# AmethystOS

**A straightforward Fedora + Niri desktop, with keyboard-friendly everyday controls.**

AmethystOS brings a configured [Niri](https://github.com/YaLTeR/niri) desktop to **Fedora Workstation** with a branded terminal installer, reversible settings, and optional application choices. It keeps your existing Fedora installation and GNOME fallback. This is a **v1 release candidate**, not a separate Linux distribution or bootable ISO.

**[Website](https://terabyteexe.github.io/AmethystOS/) · [Installation](https://terabyteexe.github.io/AmethystOS/install.html) · [Wiki](https://terabyteexe.github.io/AmethystOS/wiki/index.html) · [Keybindings](https://terabyteexe.github.io/AmethystOS/wiki/keybinds.html)**

## Installation

**Before using the command, rename your repository to `TerabyteEXE/AmethystOS` and publish these files to its `main` branch.** The command will not fetch this ZIP until the renamed repo contains the updated `bootstrap.sh`.

Start with a working Fedora Workstation installation. Run as your normal user:

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/AmethystOS/main/bootstrap.sh | bash
```

**Security note:** The command above downloads and executes the current repository `main` branch, not a version-pinned or checksum-verified release. Read [`bootstrap.sh`](bootstrap.sh), [`install.sh`](install.sh), and [`docs/SECURITY.md`](docs/SECURITY.md) before running, especially on a daily-use machine. This project was built with AI assistance and has not received an independent security audit.

For an inspectable local install:

```bash
git clone https://github.com/TerabyteEXE/AmethystOS.git
cd AmethystOS
bash install.sh --dry-run
bash install.sh
```

When the installer is complete, **log out, choose Niri at the Fedora login screen**, and log back in. GNOME stays installed. Existing dotfiles require explicit approval and are backed up before replacement.

## Installer, software choices and removal

Run `bash install.sh` or use the one-command bootstrap above. On a normal Fedora
terminal the **terminal UI** offers a set of optional application groups:
Firefox, Chromium, everyday utilities, office/mail, creative software,
development, media, and gaming tools. You can deselect all extras; required Niri
components, terminal fonts, portals, Waybar, audio and network tools are always
installed. Packages come only from your enabled Fedora repositories. A missing
optional app is reported and skipped rather than breaking the desktop.

The terminal UI also asks whether to back up and replace existing dotfiles and
whether to coordinate GTK/libadwaita dark appearance with the Niri desktop.
Appearance preferences affect your GNOME fallback too; AmethystOS saves their
previous values and restores them on uninstall **unless you have changed them
outside AmethystOS**. Qt and Flatpak apps can retain their own styling.

After a remote installation, the recovery tool remains available:

```bash
amethystos-uninstall --dry-run # inspect what would be restored
amethystos-uninstall           # asks for RESTORE confirmation
```

It restores tracked configuration files, preserving their original backups even
after AmethystOS upgrades. It does **not** remove installed Fedora packages,
personal wallpapers or GNOME.

## What's included

| Desktop element | Project |
| --- | --- |
| Scrollable tiling compositor | Niri |
| Status bar | Waybar |
| App launcher | AmethystOS Home (GTK, nested categories), Fuzzel fallback |
| Terminal | Alacritty (Kitty also configured) |
| Notifications | Mako |
| Wallpaper | Swaybg and a wallpaper picker |
| Lock screen | GTKLock |
| Audio and network integration | Fedora packages and supporting desktop tools |
| System settings | Amethyst Settings (Super+Shift+S and Waybar gear) |
| Fonts and application themes | Cascadia Mono NF, Noto Sans, GTK3/4, Qt6ct |

**AmethystDark.png** and **AmethystLight.png** are included under `assets/wallpapers/`. Both are copied if missing on every installation, without replacing files of the same name. A fresh, empty wallpaper directory selects Amethyst Dark by default; existing wallpaper choices remain untouched. Change through Super+Shift+W, `set-wallpaper`, or Amethyst Settings.

## Amethyst Home and bar controls (RC2.8)

**Super+Space** opens **Amethyst Home**, a compact, dark translucent menu with
**Apps, Learn, Style, Setup, Install, Remove, Update, About, System, and Power**.
Use **Up/Down** to choose, **Enter or Right** to open, **Left/Backspace** to return
from a category, and **type to search** either the current category or the full
menu from Home. **Esc** or **Super+Space again** closes the launcher.
**Super+D** opens the exact same Home menu; it is not a second menu anymore.

Installed apps launch through GIO desktop-file metadata; maintenance actions are
fixed local commands and retain their existing confirmation steps. The menu has
no telemetry, account requirement, or arbitrary shell command input. If GTK
cannot start, Fuzzel remains a lightweight app-search fallback.

Waybar keeps its original compact layout. Clock, audio, network, Bluetooth,
and settings widgets open small matching Light/Dark panels. The calendar
shows your local date and can return to today; the other panels show available
local device state and link to real settings. Their shared style uses restrained
translucency with native Niri background blur when available. They are
**separate GTK surfaces**, not embedded Waybar widgets: precise anchoring can
vary with output size, bar position, and GTK-layer-shell support.

Your original **AmethystDark.png** and **AmethystLight.png** are unchanged.
No mockup art, additional wallpaper, new boot splash, or new GTK-wide styling
is forced on other apps. See [`docs/RELEASE_NOTES_RC27.md`](docs/RELEASE_NOTES_RC27.md).

## First shortcuts

| Keys | Action |
| --- | --- |
| `Super + Enter` | Terminal |
| `Super + Space` | Amethyst Home: categories, app search and actions |
| `Super + W` | Close focused window |
| `Super + Shift + Tab` | Toggle tabbed column display |
| `Super + Shift + S` | Open Settings |
| `Super + H / L` | Navigate columns |
| `Super + Up / Down` | Navigate workspaces |
| `Super + O` | Overview |
| `Super + Shift + /` | Niri built-in keybinding overlay |

The [keybinding reference](wiki/keybinds.html) is **generated directly from** [`payload/niri/keybinds.kdl`](payload/niri/keybinds.kdl). Refresh it after editing shortcuts with `python3 scripts/build_site.py`. Other pages, including `about.html`, are maintained as HTML and are not overwritten by this command.

## Local commands

```bash
bash install.sh --dry-run   # inspect the plan without modifying anything
bash install.sh             # terminal GUI installer, selected apps and backups
bash install.sh --replace   # replace existing dotfiles with backups
amethystos-uninstall       # persistent uninstaller after remote installation
bash uninstall.sh           # same restore from a local repo checkout
bash tests/validate.sh      # portable tests and Niri validation, where available
```

Backups live at `~/.local/state/amethystos-base-v1/backups/`. Restore deliberately protects files you've edited after installation. Packages installed through DNF are not removed by the restore script.

## Website and docs

The website is a **simple, documentation-first static site** using dependency-free HTML, CSS and JavaScript, ready for GitHub Pages. Its routes are `index.html`, `install.html`, `wiki/index.html`, `wiki/keybinds.html`, `wiki/customization.html`, and `wiki/troubleshooting.html`.

```bash
python3 scripts/build_site.py         # regenerate only the keybinding reference
python3 scripts/build_site.py --check # ensure keybinding reference isn't stale
```

The homepage source lives in `site_templates/home.html`; edit that template rather than editing generated `index.html`.

To publish it, go to **Settings → Pages → Build and deployment**, choose **Deploy from a branch**, select `main` and `/ (root)`. See [`docs/GITHUB_PAGES.md`](docs/GITHUB_PAGES.md).

## Official logo

The purple crystal is the official AmethystOS project logo supplied by the project creator. The repository contains the [original image](assets/branding/amethyst-logo-original.png), a [transparent web-ready PNG](assets/branding/amethyst-logo.png), and PNG browser icons. The website uses the image directly; it is **not** a replacement illustration.

## Source and credit

The desktop rice is adapted from **[New Niri Minimal Dots](https://github.com/youngcoder45/New-Niri-minimal-dots)** by **Aditya Verma**. Its MIT copyright notice is retained in [`LICENSE.upstream`](LICENSE.upstream); Fedora portability changes are listed in [`docs/UPSTREAM.md`](docs/UPSTREAM.md). AmethystOS is a separate project and is not affiliated with Fedora, Niri, or Omarchy. It does not include unverified third-party wallpaper assets.

## Upgrading from an older installation

If you are switching from an earlier installation, read [the upgrade notes](docs/UPGRADING.md) before replacing existing dotfiles. Older backups are not deleted or migrated automatically.

## Status

**v1 polish release candidate.** The desktop has been tested by its maintainer, but specific Fedora versions, other GPUs, display configurations, and third-party components still need wider testing. Local automated checks do not prove all hardware and graphical integrations work on every computer. See [`docs/TESTING.md`](docs/TESTING.md) and [`docs/SECURITY.md`](docs/SECURITY.md).

## RC2.1 installer hotfix

The interactive menu was fixed for the documented `curl | bash` installer. It now opens the controlling terminal separately for input/output; choosing optional app group 8 (Gaming) no longer toggles configuration replacement. The portable validation suite includes a pseudo-terminal regression test. No changes were made to the existing Niri rice.


## AmethystOS RC2.2: desktop controls

- **Super+1–5** opens five permanent named Niri workspaces; **Super+Ctrl+1–5** moves the focused column there. Niri still has its own dynamic workspace behavior for additional workspaces.
- **Super+Shift+S** opens Amethyst Settings. **Super+Shift+T** opens the appearance picker.
- **Amethyst Dark / Light** recolor Waybar, launcher, notification and terminal files, coordinate GTK where available, and use the corresponding wallpaper.
- **Interface scaling:** `amethyst-scale auto` leaves Niri's automatic per-monitor Wayland scaling alone. `amethyst-scale 125` adjusts bar and application font sizes; advanced users can choose 100, 115, 125, 150 or 175.
- **Fastfetch** uses the official AmethystOS crystal PNG; terminal rendering support varies.
- **Boot integration:** AmethystOS leaves Fedora’s boot screen and Plymouth configuration unchanged. Legacy splash tooling was retired; see `docs/UPGRADING.md` if you previously enabled it.
- **Optional apps** can be selected individually. Steam, OBS Studio, Discord and Flatseal are installed from Flathub only after explicit opt-in. They are not required for the desktop.

**Safety:** This is an AI-assisted experimental release candidate, not a security-audited operating system or ISO. Review scripts and test on Fedora with GNOME available for recovery.

## RC2.5 — Settings and launcher cleanup (historical)

- **Super+Space** continues to search apps, and now also finds a single **Amethyst Menu** entry. Open that entry to access the same six categories as **Super+D**, without filling search with dozens of settings shortcuts.
- Amethyst Settings now has light/dark styling drawn from the desktop’s existing palettes and uses the project crystal logo. Theme changes update Settings without dismissing the window.
- The experimental Plymouth/boot splash option has been removed; no boot files are changed during installation or upgrades.

See [`docs/RELEASE_NOTES_RC25.md`](docs/RELEASE_NOTES_RC25.md) for compatibility and testing notes.
