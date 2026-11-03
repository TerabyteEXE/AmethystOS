# Kuhl OS — Fedora + Niri

An easy-to-install **Fedora Workstation desktop customization**, not a standalone Linux distribution or ISO(yet). Includes Niri tiling, a vertical Waybar based on Sevens dotfiles, Kuhl's installer, searchable shortcut guide, and settings tools.

**Experimental beta / AI-assisted / not security-audited.** Before installing, review the scripts and dependencies, understand the risks, and back up your files. See [Security](docs/SECURITY.md) and [Credits](docs/CREDITS.md).

## Install on Fedora Workstation (Fedora 43+, x86_64)

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
```

This command works **after you publish this repository to `main`** at that exact URL. It downloads this repo and launches Kuhl's interactive terminal installer with progress, Fedora package checks and protected config replacement. No Arch/AUR installer is run. For safety, you may download the repository and inspect `bootstrap.sh` and `install.sh` before running `bash install.sh`.

Existing Niri installs: choose **Replace existing desktop settings (with backups)**, then type `REPLACE`. GNOME remains installed as the recovery session.

## Essential shortcuts

| Key | Action |
|---|---|
| Super + Space | App/file search |
| Super + Enter | Alacritty terminal |
| Super + D | Kuhl Control Center |
| Super + Shift + S | Kuhl Settings |
| Ctrl + Super + K | Searchable keyboard guide |
| Super + Shift + T | Themes |
| Super + Q | Close focused window |
| Super + H/J/K/L | Navigate windows |
| Super + 1–9 | Workspaces |
| Super + W | Wallpapers |

See the complete [keyboard guide](docs/KEYBINDS.md).

## Settings and appearance

```bash
kuhl settings
kuhl bar show
kuhl bar scale 125
kuhl bar position left
kuhl bar module close off
kuhl ui scale 110
kuhl display wizard
kuhl theme sevens
kuhl wallpaper set ~/Pictures/wallpaper.png
kuhl doctor
```

The default is **Kuhl Sevens**, using the MIT source's gapless Niri layout, animations, clean slate/blue palette, and compact vertical Waybar. Kuhl Day and Dusk remain available. The source's separately maintained wallpaper submodule is not included; use your own image.


## Upgrading a repository that still contains older release files

Uploading a ZIP over an existing GitHub repository does **not** automatically delete old files.
Unused `third_party/KyleOS/` or `assets/wallpapers/third-party/` folders from earlier versions
may remain visible on GitHub. The validation script warns about these leftovers, but
does not fail, since the new Fedora installer does not use them.

For a clean public release, review the Git diff and remove *tracked* legacy paths
from the repository in a separate commit if you no longer need them:

```bash
git rm -r --cached --ignore-unmatch third_party/KyleOS assets/wallpapers/third-party
git status
# Review the proposed changes before committing and pushing.
```

This does not delete your local copies. It removes those paths from Git's index.
GitHub Pages uses `index.html`; `main.html` is only an optional convenience copy.

## Test before releasing

```bash
bash tests/validate.sh
python3 scripts/validate_niri.py   # on Fedora with niri installed
```

A static test on another OS does not prove the Niri compositor or desktop integrations work on Fedora. Test a real graphical login, Network/Sound/Settings, portal screen-sharing, Waybar, restart, upgrade, and uninstall before tagging stable 1.0.

## Upstream and licenses

Base reference: [Niri Dotfiles by Saatvik Sharma](https://github.com/saatvik333/niri-dotfiles), MIT (2025). Snapshot in `third_party/niri-dotfiles` with license. Adaptations documented in [Credits](docs/CREDITS.md). Kuhl retains its previous MIT code/license.

**This is not an official Fedora or Niri project.**
