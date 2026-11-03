# ✳ Kuhl OS 0.8 — Frontier Edition

**Fedora Workstation + Niri**, with a keyboard-driven, artwork-led desktop. Kuhl is an installer and customizable desktop *layer*, **not** a new Linux distribution, ISO, custom kernel, or Fedora fork. GNOME is retained as an alternate login session.

**Experimental and AI-assisted. This code has not had a security audit.** AI-generated scripts can be wrong or insecure. Read [`docs/SECURITY.md`](docs/SECURITY.md), check source changes and external packages yourself, and use a VM/spare machine or verified backups first.

## The look

The new rice closely follows the feel of **[KyleOS](https://github.com/Person-008/KyleOS)** by Rosenkranz / Person-008, especially its understated full-width status bar, asymmetric rounded corners, minimal application launcher, and artwork-led colors. Kuhl is adapted for **Fedora 43+** rather than KyleOS's Arch Linux package manager and global `/etc` configuration layout. The MIT copyright and permission notice for the source adaptations is included in [`third_party/KyleOS-MIT.txt`](third_party/KyleOS-MIT.txt).

**Artwork has a different license:** Kuhl includes *static PNG first-frame conversions* of four GIF wallpapers from KyleOS, originally illustrated by **[PrisonerCoin](https://prisonercoin.newgrounds.com/)**. Those PNGs are **CC BY-NC-SA 3.0, NOT MIT** and carry non-commercial and share-alike obligations. Their original artwork URLs and modification notes are in [`docs/CREDITS.md`](docs/CREDITS.md). The unlicensed `Survey` artwork and massive icon/GTK directories from KyleOS were **not** carried over. The older Kuhl Day/Dusk palettes and wallpapers remain available. 

The new `main.html` / `index.html` website is a pared-down, GitHub Pages-friendly landing page. Its desktop composition is **illustrative** rather than a live screenshot.

## One-command installation

On a **regular Fedora Workstation 43+ x86_64** installation as your normal account (not root):

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
```

**Publish this updated project to GitHub first.** The command pulls from `main`, not from a ZIP you downloaded from this chat. The remote code is mutable: inspect the installer before piping it to Bash. Alternatively download the source, read it, and run `bash install.sh` locally.

The branded terminal UI offers six theme choices; the default is **Frontier**. Optional apps, a third-party COPR for Vicinae, and replacing existing dotfiles require explicit user choices. Install progress is shown in six real milestones. Fedora packages are installed using `sudo dnf`; no auto-reboot. Fedora GDM will let you choose **Niri** after logging out. Existing Fedora GNOME is not removed.

To upgrade an old Kuhl installation, choose **Replace existing desktop settings (with backups)**, read the prompt, then type `REPLACE`. Kuhl backs up only replaced configs to `~/.local/state/kuhl/backups/`, tracks files it writes, and doesn't silently overwrite your edits.

## Desktop commands

| Shortcut | Function |
|---|---|
| Super + Space | Spotlight-style search: Vicinae (optional), otherwise themed Rofi; Fuzzel fallback |
| Ctrl + Super + K | Searchable keyboard shortcuts guide |
| Super + D | Kuhl terminal Control Center |
| Super + Enter | Kitty terminal |
| Super + E | Thunar file manager |
| Super + H/J/K/L | Focus columns/windows |
| Super + Shift + H/J/K/L | Move columns/windows |
| Super + 1–5 | Change workspace |
| Super + Shift + T | Theme selection menu |
| Super + R | Cycle column size |
| Super + V | Toggle floating window |
| Super + Alt + L | Lock screen |

`config/keys.json` is the source of truth; Niri's binds and [`docs/KEYBINDS.md`](docs/KEYBINDS.md) are synchronized by `scripts/sync_keys.py`.

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

The test suite covers syntax, the config generator, deployment safety and installer dry-run. GitHub Actions also attempts native Niri validation inside Fedora. **These checks do not replace a live Niri login or security review.** Hardware-specific issues, graphics drivers, Wayland portals, and the session launcher may still need attention. For recovery, select GNOME from GDM and see [`docs/RECOVERY.md`](docs/RECOVERY.md).

### External repositories and disclosures

Fedora-packaged desktop tools include Niri, Rofi, Waybar, Kitty, Mako, Fuzzel, Thunar, and Wayland utilities. Vicinae requires separate COPR consent. No AI model is bundled or run by the desktop; **source code is AI-assisted** and still requires human review, particularly installation scripts that invoke sudo. See [`docs/SECURITY.md`](docs/SECURITY.md), [`docs/CREDITS.md`](docs/CREDITS.md), and the project's [`LICENSE`](LICENSE).
