# ✳ Kuhl OS 0.7.2 — Studio Edition

**The tiny, elegant desktop that gets out of your way.** Kuhl OS is an independently designed Fedora Workstation + Niri experience: scrolling tiling, a centered capsule bar, Day/Dusk palettes, quick search, a searchable shortcut guide, a keyboard-driven control center, and a branded terminal installer.

Kuhl is **not** a separate distro, a replacement kernel, an ISO or a Fedora fork. Fedora continues providing updates and packages, and GNOME remains installed as a fallback.

> **Status: experimental release.** Static functional tests pass, but this build environment cannot perform a real Fedora / Niri compositor login. On Fedora the install script validates both palettes with the real `niri validate` parser before modifying personal configs. Try on a spare machine or VM first. Development focus: Fedora 44 on x86_64.

## Gallery and reference

`main.html` is the GitHub Pages-ready website with an explicitly labeled **concept** preview. It does not impersonate a live Niri screenshot. The Studio look uses a small **centered status pill**, generous corner radii, minimal charcoal/cream colors and gold highlights. This visual direction was inspired by screenshots in a user-provided low-spec Niri reference. **No code, images, fonts, scripts, or wallpaper assets from that unlicensed reference are included here**; the new configs are independently written for Kuhl.

The original Kuhl wallpapers are retained for compatibility, but **not enabled by default**. The default desktop is a soft, solid Day/Dusk color. Add your own wallpaper later (see below).

## One-command install / upgrade

On **Fedora Workstation 43+ (Fedora 44 target), x86_64**, open Terminal as your **normal user** and paste **one command**:

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
```

That's it. The bootstrap downloads the current project from the public [`TerabyteEXE/Kuhl-OS`](https://github.com/TerabyteEXE/Kuhl-OS) `main` branch, checks that the archive is complete, then launches the **branded Kuhl terminal installer**. No ZIP extraction, manual `git clone`, `cd`, or separate validation command is required. The installer handles packages, native Niri checks, backups and the six progress stages. Its options include a Day/Dusk palette and optional Vicinae (which separately requires approval for a third-party COPR).

**Already running Kuhl or another Niri rice?** In the terminal menu, enable **“Replace existing desktop settings (with backups)”**. Review the confirmation and type `REPLACE` to overwrite managed target configurations; otherwise your existing files are kept. Kuhl records original files under `~/.local/state/kuhl/backups/`, and keeps GNOME installed as a fallback.

When complete, log out and select **Niri** at the login screen. No automatic reboot. Wallpapers can be set later with `kuhl wallpaper set ~/Pictures/my-wallpaper.png`.

**Before using a remote installer:** inspect [bootstrap.sh](https://github.com/TerabyteEXE/Kuhl-OS/blob/main/bootstrap.sh) and [install.sh](https://github.com/TerabyteEXE/Kuhl-OS/blob/main/install.sh). The one-line command runs code from your public GitHub repository. It will install the version currently published there, so **publish this entire revised project to `main` before using the command**. Kuhl does not support Fedora Atomic/rpm-ostree installations; working Wayland graphics and sufficient `/` space are required. Try it on a spare machine or VM first.

For **development/testing from a downloaded source ZIP** (not the public install path):

```bash
bash tests/validate.sh
bash install.sh --dry-run
bash install.sh
```

### Installer features

- Single copy-and-paste command opens the branded, keyboard-operated terminal option selector (arrow keys / J/K, Space, T, Enter)
- Six honest progress milestones during package install, config checking, optional apps and deployment
- Free-space check before DNF's transaction; guidance when the VM disk is too small
- Validates both Niri palette configurations *before* writing personal config files
- Tracks owned files by hash, preserves user edits and backs up explicitly chosen replacements
- Optional Flatpaks and Vicinae are opt-in; no automatic system reboot

## A desktop you can learn

| Key | Action |
| --- | --- |
| **Super + Space** | Search (Vicinae if installed, otherwise Fuzzel) |
| **Ctrl + Super + K** | **Searchable, categorized shortcut atlas** |
| **Super + D** | Kuhl terminal control center |
| **Super + Enter** | Kitty terminal |
| **Super + E** | Thunar file manager |
| **Super + H/J/K/L** | Navigate columns and stacked windows |
| **Super + Shift + H/J/K/L** | Move columns and stacked windows |
| **Super + 1–5** | Change workspace |
| **Super + Shift + 1–5** | Move column to workspace |
| **Super + Shift + T** | Palette picker |
| **Super + R** | Cycle column width |
| **Super + F** | Maximize column |
| **Super + Alt + L** | Lock screen |
| **Super + Shift + P** | Power / session menu |

Full list: [`docs/KEYBINDS.md`](docs/KEYBINDS.md), generated from **`config/keys.json`**. The actual Niri `binds {}` block is generated from the same manifest with `python3 scripts/sync_keys.py`. Run `--check` in tests to detect if files get out of sync.

**Migration note:** v0.6.x used Super+Ctrl+K for moving a window up and Super+Shift+L to lock. In v0.7, these are **Super+Shift+K** (move up) and **Super+Alt+L** (lock), reserving Ctrl+Super+K for the guide and Shift+L for moving a column right. Old Ctrl+Super+H/J/L aliases remain. 

## Kuhl commands

```bash
kuhl menu                            # Kuhl Control Center (Super+D)
kuhl keys --ui                       # keyboard atlas (Ctrl+Super+K)
kuhl keys                            # print full shortcut guide
kuhl launcher                        # Spotlight-style search (Super+Space)
kuhl theme dusk                      # charcoal/gold theme
kuhl theme day                       # warm-cream theme
kuhl wallpaper set ~/Pictures/my-wallpaper.jpg  # your own image
kuhl wallpaper reset                 # solid background, no generated art
kuhl wallpaper day                   # optional legacy Day wallpaper
kuhl wallpaper dusk                  # optional legacy Dusk wallpaper
kuhl wallpaper default               # optional legacy original wallpaper
kuhl status                          # check managed file state
kuhl doctor                          # verify session and Niri config
kuhl uninstall                       # restore unchanged tracked dotfiles
```

The control center and keyboard atlas are made with Python curses; no new GUI shell, Electron app, JavaScript runtime, or external script is required. The power menu asks before restart or power-off.

## Make it yours

- **Themes:** tweak `config/themes.json` (then reinstall). Applies matching Niri ring/shadow, Waybar, Kitty, Mako, Fuzzel and optional Vicinae theme files. Note that Kuhl preserves your manual edits instead of overwriting them during palette switches.
- **Hotkeys:** edit `config/keys.json`, then run `python3 scripts/sync_keys.py`. It updates both the Niri binding block and Markdown reference. Reinstall with `--replace-configs` if you changed your managed config intentionally.
- **Bar:** `configs/waybar/config.jsonc` (small fixed-width floating capsule) and generated CSS in `scripts/render.py`.
- **Terminal:** `configs/kitty/kitty.conf`. Keep backgrounds opaque to remain fast on older GPUs.
- **Wallpaper:** `kuhl wallpaper set PATH` selects a local PNG/JPG/WebP and remembers it separately from themes. `reset` uses only the Kuhl palette color. Your image is never uploaded, modified or deleted.

Files are installed under `~/.local/share/kuhl` and managed user configs in `~/.config`. `kuhl uninstall` only removes or restores **unchanged** tracked files; modified files are left intact. Wallpapers/assets and backups remain for manual recovery. See [`docs/RECOVERY.md`](docs/RECOVERY.md).

## Verify and troubleshoot

```bash
bash tests/validate.sh          # syntax, manifests, dry-run, file safety tests
python3 scripts/validate_niri.py # on Fedora with Niri: native validation of both themes
niri validate                   # validate your active configuration
kuhl doctor
```

The repository's GitHub Actions workflow also runs the native Niri parser in a Fedora container. An actual hardware/VM login is still necessary to verify portal screen sharing, media keys, GPU acceleration, lock screen, multiple displays and Bluetooth. If Niri fails, choose GNOME from the login screen and consult [`docs/TESTING.md`](docs/TESTING.md) and [`docs/RECOVERY.md`](docs/RECOVERY.md).

**Known limitations:** Vicinae is third-party software with its own privacy settings and requirements; Kuhl does not control them. On very old AMD GPUs, Mesa/Wayland acceleration must be tested separately. A fixed 646-pixel Waybar capsule is intended for typical laptop/desktop displays, not very narrow screens. The Kuhl terminal guide is a floating Kitty window; visual appearance can vary slightly by installed terminal fonts.

## Licenses and independence

The Kuhl project retains its existing [`LICENSE`](LICENSE). Third-party Fedora packages are installed from their respective repositories under their own licenses. The low-spec Niri reference provided by the project author was **used only as a high-level visual reference** and is not redistributed. The name Kuhl does not imply endorsement by Fedora, Red Hat, Niri, Waybar, Vicinae or their creators. No bundled AI integration, telemetry collector, hosted backend, or automatic background updater is installed by Kuhl.
