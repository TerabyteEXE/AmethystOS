# Kuhl OS

**A straightforward Fedora + Niri desktop.**

Kuhl OS brings a configured [Niri](https://github.com/YaLTeR/niri) desktop to **Fedora Workstation** with a small, guided installer. It keeps your existing Fedora installation and GNOME fallback. This is a **v1 release candidate**, not a separate Linux distribution or bootable ISO.

**[Website](https://terabyteexe.github.io/Kuhl-OS/) · [Installation](https://terabyteexe.github.io/Kuhl-OS/install.html) · [Wiki](https://terabyteexe.github.io/Kuhl-OS/wiki/index.html) · [Keybindings](https://terabyteexe.github.io/Kuhl-OS/wiki/keybinds.html)**

## Installation

Start with a working Fedora Workstation installation. Run as your normal user:

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
```

**Security note:** The command above downloads and executes the current repository `main` branch, not a version-pinned or checksum-verified release. Read [`bootstrap.sh`](bootstrap.sh), [`install.sh`](install.sh), and [`docs/SECURITY.md`](docs/SECURITY.md) before running, especially on a daily-use machine. This project was built with AI assistance and has not received an independent security audit.

For an inspectable local install:

```bash
git clone https://github.com/TerabyteEXE/Kuhl-OS.git
cd Kuhl-OS
bash install.sh --dry-run
bash install.sh
```

When the installer is complete, **log out, choose Niri at the Fedora login screen**, and log back in. GNOME stays installed. Existing dotfiles require explicit approval and are backed up before replacement.

## What's included

| Desktop element | Project |
| --- | --- |
| Scrollable tiling compositor | Niri |
| Status bar | Waybar |
| App launcher | Fuzzel |
| Terminal | Alacritty (Kitty also configured) |
| Notifications | Mako |
| Wallpaper | Swaybg and a wallpaper picker |
| Lock screen | GTKLock |
| Audio and network integration | Fedora packages and supporting desktop tools |

**Kuhl Still**, an original minimal wallpaper, is included under `assets/wallpapers/`. On first installation only, it is copied if `~/Pictures/wallpapers/` does not contain any image. Your current wallpaper and selection are not replaced.

## First shortcuts

| Keys | Action |
| --- | --- |
| `Super + Enter` | Terminal |
| `Super + Space` | App launcher |
| `Super + Q` | Close focused window |
| `Super + H / L` | Navigate columns |
| `Super + Up / Down` | Navigate workspaces |
| `Super + O` | Overview |
| `Super + Shift + /` | Niri built-in keybinding overlay |

The [complete 125-shortcut reference](wiki/keybinds.html) is **generated directly from** [`payload/niri/keybinds.kdl`](payload/niri/keybinds.kdl). Refresh it after editing shortcuts with `python3 scripts/build_site.py`.

## Local commands

```bash
bash install.sh --dry-run   # inspect the plan without modifying anything
bash install.sh             # install on Fedora Workstation
bash install.sh --replace   # replace existing dotfiles with backups
bash uninstall.sh           # restore tracked configs, if unmodified
bash tests/validate.sh      # portable tests and Niri validation, where available
```

Backups live at `~/.local/state/kuhl-base-v1/backups/`. Restore deliberately protects files you've edited after installation. Packages installed through DNF are not removed by the restore script.

## Website and docs

The website is a **simple, documentation-first static site** using dependency-free HTML, CSS and JavaScript, ready for GitHub Pages. Its routes are `index.html`, `install.html`, `wiki/index.html`, `wiki/keybinds.html`, `wiki/customization.html`, and `wiki/troubleshooting.html`.

```bash
python3 scripts/build_site.py         # regenerate the pages and keybinding reference
python3 scripts/build_site.py --check # ensure generated pages aren't stale
```

The homepage source lives in `site_templates/home.html`; edit that template rather than editing generated `index.html`.

To publish it, go to **Settings → Pages → Build and deployment**, choose **Deploy from a branch**, select `main` and `/ (root)`. See [`docs/GITHUB_PAGES.md`](docs/GITHUB_PAGES.md).

## Source and credit

The desktop rice is adapted from **[New Niri Minimal Dots](https://github.com/youngcoder45/New-Niri-minimal-dots)** by **Aditya Verma**. Its MIT copyright notice is retained in [`LICENSE.upstream`](LICENSE.upstream); Fedora portability changes are listed in [`docs/UPSTREAM.md`](docs/UPSTREAM.md). Kuhl OS is a separate project and is not affiliated with Fedora, Niri, or Omarchy. It does not include unverified third-party wallpaper assets.

## Status

**v1 site release candidate.** The desktop has been tested by its maintainer, but specific Fedora versions, other GPUs, display configurations, and third-party components still need wider testing. Local automated checks do not prove all hardware and graphical integrations work on every computer. See [`docs/TESTING.md`](docs/TESTING.md) and [`docs/SECURITY.md`](docs/SECURITY.md).
