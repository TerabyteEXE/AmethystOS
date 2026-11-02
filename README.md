# Kuhl OS ✳

**Fedora Workstation, made cozy.** Kuhl is a small, open-source collection of scripts, original Day/Dusk wallpapers, Shell CSS, icons and GNOME extensions that makes Fedora feel like a complete personalized desktop. It's built **on Fedora Workstation**, not an independent ISO or a replacement for GNOME.

Website: https://terabyteexe.github.io/Kuhl-OS/main.html

> **Kuhl v0.2 — experimental build.** The scripts and mock tests are supplied, but this release hasn't been run on real Fedora hardware by the maintainer. Test on a spare Fedora install or VM before treating it as reliable. The YouTube video's extension list could not be verified from a transcript; the curated list below is a proposed Kuhl setup, not an exact reproduction.

## Install — only 4 commands

1. Install **Fedora Workstation 44 (GNOME 50)** on your PC from https://fedoraproject.org/workstation/download/, then boot and sign in.
2. Open Terminal, paste:

```bash
sudo dnf install -y git
git clone https://github.com/TerabyteEXE/Kuhl-OS.git
cd Kuhl-OS
bash install.sh --theme dusk --profile full
```

**Log out and in once** and open the GNOME **Extensions** app. If newly installed extensions aren't enabled yet, enable them there. Some Fedora/GNOME updates may require updated extension versions, and incompatible ones are skipped.

If downloading the GitHub repo as a ZIP, extract it and run `bash install.sh --theme dusk --profile full` from the extracted folder. **Never run the entire installer with sudo.** It uses `sudo` only for DNF package installs.

To preview changes without touching anything: `bash install.sh --dry-run`.

## Extension profiles

`--profile full` is the **recommended polished appearance**: five everyday GNOME extensions plus two visual effects. `--profile balanced` keeps the five everyday extensions without blurring and rounded-window compositor shaders. `--profile none` installs only the wallpaper, icon/font, GNOME Shell CSS and launcher shortcut; it still installs GNOME's official User Themes package unless `--no-packages` is passed.

| Extension | Purpose | Balanced | Full |
| --- | --- | :---: | :---: |
| User Themes (official Fedora RPM) | Kuhl Day/Dusk shell styling | ✓ | ✓ |
| Dash to Dock | Tidy app dock | ✓ | ✓ |
| Just Perfection | Customize GNOME UI elements | ✓ | ✓ |
| AppIndicator | Tray icons for desktop apps | ✓ | ✓ |
| Tiling Assistant | Window snapping/layout | ✓ | ✓ |
| Caffeine | One-click suspend/screen blank prevention | ✓ | ✓ |
| Blur my Shell | Soft blurred GNOME menus/overview | — | ✓ |
| Rounded Window Corners Reborn | Rounded corners on legacy apps | — | ✓ |

All seven third-party extensions are fetched from **extensions.gnome.org** and are checked against your running GNOME version. Kuhl *does not* force incompatible extensions or modify version metadata. **Open Bar is not installed**, because its current published versions don't officially support GNOME 50. Rounded corners and blur can cost GPU resources; Balanced is an easy option on older computers. The project's 8 GB RAM recommendation is a baseline, not a claim that extra extensions use no resources.

### What the installer actually does

- Installs Papirus Day/Dusk icons, `adw-gtk3` for older GTK3 apps, Noto Sans and JetBrains Mono via standard Fedora DNF.
- Adds Kuhl wallpapers and small CSS overrides to the stock GNOME Shell appearance. Modern libadwaita apps may retain their own colors; there is no full GTK4 repaint.
- Enables GNOME's **User Themes** extension (provided by Fedora) when possible.
- Registers `Ctrl+Space` for GNOME's built-in search/overview. This is *not* a standalone floating Spotlight-like search bar yet. File search depends on GNOME's search providers.
- Saves original GNOME settings before changing them; adds theme switchers and a `kuhl` CLI.
- Installs version-compatible add-ons through GNOME's official extension service; some need a new login to activate.

**It does not** remove Fedora apps, install AI services, replace Fedora's updater, disable SELinux/firewalld, or install random RPM repositories. It doesn't make any custom systemd services.

## After installation

```bash
kuhl theme day                 # Switch to warm light theme
kuhl theme dusk                # Switch to cozy dark theme
kuhl status                    # Show paths and active mode
kuhl doctor                    # Inspect basic installation state
kuhl extensions list           # See all curated extensions
kuhl extensions install full   # Add all visual effects
kuhl extensions install balanced # Switch to lighter profile, remove Kuhl-owned effects
kuhl uninstall                 # Restore preferences/remove Kuhl-owned assets
```

`~/.local/bin/kuhl` is always available if the terminal hasn't refreshed your PATH. Extension settings remain configurable through the GNOME **Extensions** app: adjust dock icon size/position, blur amount, rounded corners and panel visibility to your taste. For performance concerns, prefer `balanced` rather than turning off Fedora services.

### Custom wallpapers

Place your own **PNG** files at these paths *inside your downloaded repository*, then rerun `bash install.sh`:

- `assets/wallpapers/kuhl-day.png` — Day wallpaper
- `assets/wallpapers/kuhl-dusk.png` — Dusk wallpaper

The wallpapers supplied here are original Kuhl artwork. GNOME can use other image formats, but this installer expects PNG filenames. No extra image services run in the background.

### Upgrades and uninstall

To update the scripts in a Git clone: `git pull --ff-only && bash install.sh --profile full`. The first backup of your settings is preserved across reinstalls.

`kuhl uninstall` restores previous preferences only if the value is still what Kuhl set, removes the add-ons **installed by Kuhl**, and preserves any extensions you had beforehand. DNF packages are deliberately left installed to avoid deleting shared software. Settings history is saved in `~/.local/state/kuhl/settings.tsv`. No factory reset occurs.

If a GNOME extension causes trouble, open the **Extensions** app to disable it or run `kuhl extensions install balanced`; for full cleanup run `kuhl uninstall`.

## GitHub repo structure

```text
Kuhl-OS/
├── main.html                      # Keep your existing website unchanged
├── LICENSE                        # Keep your existing MIT license
├── README.md
├── install.sh
├── uninstall.sh
├── bin/kuhl
├── lib/common.sh
├── config/
│   ├── extensions.tsv             # Five everyday GNOME extensions
│   └── effects.tsv                # Two optional GPU visual effects
├── assets/
│   ├── wallpapers/kuhl-day.png
│   ├── wallpapers/kuhl-dusk.png
│   └── themes/{Kuhl-Day,Kuhl-Dusk}/gnome-shell/gnome-shell.css
├── scripts/
│   ├── extensions.py              # Official API + GNOME version validation
│   ├── patch-site.py              # Optional: update website install text
│   └── generate-wallpapers.py     # Only if recreating example artwork
├── docs/
└── tests/validate.sh
```

**To publish into your existing GitHub repo:** extract the attached release ZIP on your computer; upload the **contents** into [TerabyteEXE/Kuhl-OS](https://github.com/TerabyteEXE/Kuhl-OS), preserving folder structure. Do **not** delete `main.html` or `LICENSE`; this ZIP deliberately leaves those existing files alone. GitHub can accept a folder dragged into its upload screen, or you can copy into a Git clone and commit/push. If you'd like to update the site's outdated “coming soon”/“four extensions” copy, run `python3 scripts/patch-site.py main.html` in your local repository before committing. The patcher creates a backup and refuses unknown layouts; details in `docs/WEBSITE.md`.

## Validation and notes

`bash tests/validate.sh` runs shell syntax checks, checks the expected assets and profiles, and mocks save/switch/restore of GNOME settings **without touching your desktop**. It doesn't validate real Fedora DNF installation, GNOME theme rendering, or GNOME's extension network API; those require testing on Fedora 44. The installer targets regular Fedora Workstation on **x86_64**, 8 GB RAM or more suggested, and approximately 40 GB storage for a comfortable setup.

Kuhl OS is independent of Fedora/Red Hat, not affiliated with or endorsed by either project. Fedora is a trademark of Red Hat, Inc. Kuhl's own files are MIT licensed where included under the repository's license. Third-party GNOME extensions, fonts and icon themes retain **their own licenses**; they are fetched from upstream or official Fedora packages, not repackaged as Kuhl assets.
