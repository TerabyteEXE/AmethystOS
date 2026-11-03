# ✳ Kuhl OS v1.0 RC2 — Stabilization Build

**Fedora Workstation + Niri**, with a keyboard-driven, artwork-led desktop. Kuhl is an installer and customizable desktop *layer*, **not** a new Linux distribution, ISO, custom kernel, or Fedora fork. GNOME is retained as an alternate login session.

**Experimental and AI-assisted. This code has not had a security audit.** AI-generated scripts can be wrong or insecure. Read [`docs/SECURITY.md`](docs/SECURITY.md), check source changes and external packages yourself, and use a VM/spare machine or verified backups first.

## The look

The desktop incorporates MIT-licensed dotfiles from **[KyleOS](https://github.com/Person-008/KyleOS)** by Rosenkranz / Person-008, including its original Niri animation shader, layouts and window rules, Waybar layout/CSS, Rofi launchers, Alacritty palettes and Mako themes. Only Fedora compatibility and Kuhl integration changes are made. See `third_party/KyleOS/original/` for the untouched originals and `docs/CREDITS.md` for an adaptation map. Kuhl is adapted for **Fedora 43+** rather than KyleOS's Arch Linux package manager and global `/etc` configuration layout. The MIT copyright and permission notice for the source adaptations is included in [`third_party/KyleOS-MIT.txt`](third_party/KyleOS-MIT.txt).

**Artwork has a different license:** Kuhl includes *static PNG first-frame conversions AND the original GIF files* of four wallpapers from KyleOS, originally illustrated by **[PrisonerCoin](https://prisonercoin.newgrounds.com/)**. Those images are **CC BY-NC-SA 3.0, NOT MIT** and carry non-commercial and share-alike obligations. Their original artwork URLs and modification notes are in [`docs/CREDITS.md`](docs/CREDITS.md). The unlicensed `Survey` artwork and the massive third-party icon/GTK directories from KyleOS were **not** carried over. The original KyleOS font families are not bundled, so font metrics and some icons may differ until you install them yourself. The default `swaybg` wallpaper is static; exact KyleOS animated GIF playback needs optional `awww`, set via `KUHL_ANIMATED_WALLPAPER=1`, which Kuhl does not install automatically. The older Kuhl Day/Dusk palettes and wallpapers remain available. 

The `index.html` website is a pared-down, GitHub Pages-friendly landing page (`main.html` is an optional duplicate, not required for tests or hosting). Its desktop composition is **illustrative** rather than a live screenshot.

## One-command installation

On a **regular Fedora Workstation 43+ x86_64** installation as your normal account (not root):

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
```

**Publish this updated project to GitHub first.** The command pulls from `main`, not from a ZIP you downloaded from this chat. The remote code is mutable: inspect the installer before piping it to Bash. Alternatively download the source, read it, and run `bash install.sh` locally.

The branded terminal UI offers six theme choices; the default is **Frontier**. Optional apps, a third-party COPR for Vicinae, and replacing existing dotfiles require explicit user choices. Install progress is shown in six real milestones. Fedora packages are installed using `sudo dnf`; no auto-reboot. Fedora GDM will let you choose **Niri** after logging out. Existing Fedora GNOME is not removed.

To upgrade an old Kuhl installation, choose **Replace existing desktop settings (with backups)**, read the prompt, then type `REPLACE`. Kuhl backs up only replaced configs to `~/.local/state/kuhl/backups/`, tracks files it writes, and doesn't silently overwrite your edits.

## Kuhl Settings and scaling

The RC2 stabilization pass adds a working Niri-native settings experience, mouse-accessible window close control, adjustable full-width Waybar, per-output display scaling, and coordinated light/dark GTK appearance. Niri now permits native application titlebars rather than hiding all close buttons.

```bash
kuhl settings                     # Super+Shift+S, also clickable from Waybar
kuhl display wizard               # safely select a monitor and output scale
kuhl ui scale 125                 # larger application and terminal text
kuhl bar scale 125                # larger clickable Waybar
kuhl bar position bottom          # move the top bar to the bottom
kuhl bar module close off         # hide the mouse close-window button
kuhl bar reset                    # reset Kuhl bar layout
```

See [`docs/SETTINGS.md`](docs/SETTINGS.md) for the complete menu, independently configurable scale types, and GTK/Qt limitations.

## Desktop commands

| Shortcut | Function |
|---|---|
| Super + Space | Rofi application search, as in KyleOS (Vicinae still available optionally via `kuhl launcher vicinae`) |
| Ctrl + Super + K | Searchable keyboard shortcuts guide |
| Super + D | Kuhl terminal Control Center |
| Super + Shift + S | Kuhl Settings |
| Super + Q | Close focused application |
| Super + M | Maximize to edges |
| Super + Enter | Alacritty terminal |
| Super + E | Thunar file manager |
| Super + H/J/K/L | Focus columns/windows |
| Super + Shift + H/J/K/L | Move columns/windows |
| Super + 1–5 | Change workspace |
| Super + Shift + T | Theme selection menu |
| Super + R | Cycle column size |
| Super + V | Toggle floating window |
| Super + Alt + L | Lock screen |

The adapted `configs/niri/binds.kdl` is authoritative. The 110-entry `config/keys.json` manifest and [`docs/KEYBINDS.md`](docs/KEYBINDS.md) are verified against it by `scripts/sync_keys.py`.

```bash
kuhl theme list                       # frontier, dyson, puncture, slowend, day, dusk
kuhl theme frontier                   # change entire rice and auto wallpaper
kuhl wallpaper set ~/Pictures/me.png # use your own image
kuhl wallpaper reset                  # return to artwork for current theme
kuhl keys                             # list keyboard shortcuts
kuhl keys --ui                        # keyboard guide
kuhl menu                             # Kuhl control center
kuhl status                           # desktop status
kuhl doctor                           # check components and Niri config
kuhl uninstall                        # restore unchanged managed configs
```

## Testing and known limitations

```bash
bash tests/validate.sh
python3 scripts/validate_niri.py      # run on Fedora with niri installed
bash install.sh --dry-run
```

The test suite covers Bash/Python syntax, direct KyleOS source-file equivalence, wallpaper rights/metadata, 107 shortcut bindings, theme deployment, upgrade backups, restoration and installer dry-run. GitHub Actions also attempts native Niri validation inside Fedora. **These checks do not replace a live Niri login or security review. RC2 is NOT certified stable.** Hardware-specific issues, graphics drivers, Wayland portals, and the session launcher may still need attention. For recovery, select GNOME from GDM and see [`docs/RECOVERY.md`](docs/RECOVERY.md).

### External repositories and disclosures

Fedora-packaged desktop tools include Niri, Rofi, Waybar, Alacritty, Kitty, Mako, Fuzzel, Thunar, and Wayland utilities. Vicinae requires separate COPR consent. No AI model is bundled or run by the desktop; **source code is AI-assisted** and still requires human review, particularly installation scripts that invoke sudo. See [`docs/SECURITY.md`](docs/SECURITY.md), [`docs/CREDITS.md`](docs/CREDITS.md), and the project's [`LICENSE`](LICENSE).

## v1 release gate

**This archive is a release candidate, not a claim of a tested stable v1 build.** Before tagging v1.0 publicly, complete [`docs/RELEASE-CHECKLIST.md`](docs/RELEASE-CHECKLIST.md) on Fedora 44 hardware. These tests cannot be substituted by a successful static CI run.
