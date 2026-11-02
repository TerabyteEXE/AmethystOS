# ✳ Kuhl OS — One-command Fedora setup (v0.3, experimental)

**Fedora Workstation, made cozy.** Kuhl is a theme and application setup for **regular Fedora Workstation** with GNOME, not a separate distribution yet.

- Project website: https://terabyteexe.github.io/Kuhl-OS/main.html
- Video reference: https://www.youtube.com/watch?v=8QSJSZdUawk

> **Important:** The video caption/transcript was inaccessible when this package was assembled. This ZIP implements a curated GNOME customization with many of the same types of tools, but is **not yet verified as a precise reproduction of every program or command in the video**. See `docs/VIDEO-CHECKLIST.md` to reconcile the list. The installation has not been tested on a real Fedora machine; basic syntax, menu and settings-restore tests are included. Test on a disposable Fedora install first.

## One terminal command

On a **fresh, booted, logged-in Fedora Workstation GNOME desktop**, open Terminal and paste **one line**:

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
```

**Upload this ZIP's contents to your GitHub repo before using that command.** It retrieves `bootstrap.sh` from your repo and downloads its full `main` branch (including wallpapers and menus). The script then launches the text-based installer interactively using `/dev/tty`. You should review scripts from a repository before running one-line network installers.

**No systemd background daemon, no AI features, no third-party RPM repositories, and no modifications to Fedora's core update/security systems.** Internet is required for DNF, Flathub and extensions.gnome.org.

If you prefer to install locally: download/extract this ZIP, then run:

```bash
bash install.sh
```

**Do not use `sudo bash install.sh`** — install as your own logged-in GNOME account. It requests sudo for Fedora packages and optional login logo only.

## Text installer

The installer displays **descriptions** for every item. Use **↑/↓** to navigate, **Space** to toggle an optional item, **T** to switch Day/Dusk, **Enter** to review, and **Y** to confirm. Required base items cannot be unchecked. There is a plain text fallback for terminals where curses does not work.

### Core (always selected)

- Extension Manager (Flatpak `com.mattjakeman.ExtensionManager`) — graphic extension browsing and controls
- GNOME Tweaks and GNOME Extensions — Fedora tools
- Day/Dusk artwork, Papirus icons, fonts and shell CSS (via GNOME User Themes)

### Recommended extensions (on by default)

- Dash to Dock — application dock
- Just Perfection — shell visibility and layout
- AppIndicator — status tray icons
- Tiling Assistant — improved window snapping
- Caffeine — keep the computer awake when useful
- Blur my Shell — prettier shell blur; may cost graphics resources
- Rounded Window Corners Reborn — rounded window styling; may cost graphics resources

All extensions are downloaded from **extensions.gnome.org**, checked for the installed GNOME major version, and enabled for the next login when successfully installed. Unsupported or failed extension downloads are reported; the installer does **not** disable GNOME's version checks. `Extension Manager` will then let you further adjust settings after reboot. **No claim that these seven extensions are the video's exact list.**

### Optional apps (off by default)

- Flatseal — Flatpak permission manager
- Pika Backup — straightforward backups
- VLC — media player
- GIMP — raster image editor
- Inkscape — vector graphics
- LibreOffice — offline office suite

Additional apps are all Flathub Flatpaks (`--user`), so the setup won't add random third-party RPM repositories. Fedora's normal apps are not removed.

### Optional system choices

- **Kuhl logo on the GDM login screen** (off): Supported `org.gnome.login-screen.logo` setting via `/etc/dconf/db/gdm.d/95-kuhl-logo`. **This only adds a small logo, not a replacement login theme/background**. It does not modify GDM shell CSS, patches, or authentication settings. Reversible with `kuhl uninstall`.
- **Reboot when complete** (on): Installer asks again before rebooting. A reboot/login refresh is important because GNOME Wayland cannot load all newly installed extensions until a fresh session.

## Changes made

- Installs packages through `sudo dnf install` (Fedora RPMs) and Flatpak apps in the user's Flatpak installation.
- Saves changed GSettings values to `~/.local/state/kuhl/settings.tsv` for cautious restoration.
- Installs `~/.local/bin/kuhl`, two app-launcher theme shortcuts, and two wallpapers in `~/.local/share/kuhl/wallpapers/`.
- Configures Day/Dusk, title/body/terminal fonts, accent, icon theme, and Ctrl+Space for the **built-in GNOME overview** (not a floating Spotlight window).
- Installs compatible GNOME add-ons and sets their UUIDs to be enabled on next login. Extension activation can still fail if GNOME or an extension has a regression.
- If selected, adds a Kuhl logo to GDM using the officially supported dconf key. No custom login wallpaper is attempted.
- Logs installation to `~/.local/state/kuhl/install.log`. The log shows all failed components; **if any optional component fails, automatic reboot is suppressed** so you can diagnose it.

## Commands and troubleshooting

```bash
bash install.sh --dry-run             # no changes; shows default choices
bash install.sh --defaults --no-reboot # quick install without terminal menu
~/.local/bin/kuhl doctor              # diagnose basic GNOME + theme prerequisites
~/.local/bin/kuhl theme day           # warm light theme
~/.local/bin/kuhl theme dusk          # warm dark theme
~/.local/bin/kuhl extensions list     # list Kuhl's suggested extension UUIDs
~/.local/bin/kuhl uninstall           # restore tracked GNOME settings and assets
```

If **nothing seems to change**: first reboot/sign out and in, open **Extension Manager**, check that the extensions you selected show as *enabled*, and look in `~/.local/state/kuhl/install.log`. If an extension isn't compatible with your Fedora GNOME release, it will be skipped. The installer cannot guarantee upstream compatibility or wallpaper/theme behavior without running on your machine. There is no unsupported force flag. Fedora 44 uses GNOME 50; later Fedora releases may need newer extension versions.

If you have **very weak graphics**, deselect Blur my Shell and Rounded Window Corners. This does not require uninstalling Fedora or tweaking system security.

## Replacing wallpaper and adding video apps

- Replace `assets/wallpapers/kuhl-day.png` and `assets/wallpapers/kuhl-dusk.png` with your own PNG files before uploading to GitHub, then rerun the installer.
- Edit `config/choices.json` to add/change optional apps. `type: flatpak` with official Flathub app ID works directly in the installer. For new GNOME extensions, add official name, UUID, URL (TAB-separated) to `config/extensions.tsv` or `config/effects.tsv` **and** add the corresponding `type: extension` choice. GNOME version checks will still apply.
- Use `docs/VIDEO-CHECKLIST.md` to capture the video's exact apps/extension settings and update the catalog together.

## Files

```text
Kuhl-OS/
├── bootstrap.sh                 # one-line GitHub entrypoint
├── install.sh                   # Fedora installer orchestrator
├── uninstall.sh                 # uninstaller shortcut
├── bin/kuhl                     # theme/status/extensions/doctor/uninstall
├── lib/common.sh                # cautious GSettings backup
├── config/
│   ├── choices.json             # explained TUI choices
│   ├── extensions.tsv           # core GNOME extension catalog
│   └── effects.tsv              # optional graphics extensions
├── scripts/
│   ├── menu.py                  # Python curses text installer
│   ├── extensions.py            # GNOME official API version-checked installs
│   └── gdm-brand.sh             # reversible small greeter logo
├── assets/
│   ├── branding/kuhl-logo.svg
│   ├── wallpapers/{kuhl-day.png,kuhl-dusk.png}
│   └── themes/{Kuhl-Day,Kuhl-Dusk}/gnome-shell/gnome-shell.css
├── docs/
└── tests/validate.sh
```

The ZIP **does not delete your existing `main.html` or `LICENSE`**. Merge its contents into the existing `TerabyteEXE/Kuhl-OS` repository. Your website's old “4 extensions” and placeholder install command will need updating separately to avoid confusing visitors.

## Limitations

- Not independently verified on Fedora hardware; requires live testing on GNOME/Wayland.
- Cannot exactly reproduce an inaccessible YouTube video without its commands, timeline, or screenshots.
- Does not repaint libadwaita GTK4 apps, change GNOME login's full background, or install a custom Spotlight launcher yet.
- Does not remove existing Fedora software or delete existing GNOME extension user data.
- Third-party apps/extensions are installed from their own package sources and retain their own licenses. No AI or telemetry is bundled in Kuhl scripts.
