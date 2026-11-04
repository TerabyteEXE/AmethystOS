# AmethystOS v1 RC2.2 — Desktop polish

Built from the working **RC2.1** Fedora + Niri installer with its original desktop layout, branding, wiki and wallpaper files retained.

## Added

- Five persistent **named** workspaces (`one`–`five`), displayed as 1–5 in Waybar, with Super+1…5 and Super+Ctrl+1…5 bindings. Niri may also show extra dynamic workspaces.
- Subtle, native Niri transitions with no new compositor dependencies.
- Amethyst Dark / Light theme profiles for Waybar, Fuzzel, Kitty, Alacritty, Mako, GTK, and Qt6ct, coordinating the corresponding wallpapers.
- `amethyst-scale auto|100|115|125|150|175` for readable text and bar geometry. Niri's native per-output DPI is left to the compositor.
- AmethystOS logo in Fastfetch (image display depends on terminal capabilities and optional chafa).
- **Optional** AmethystOS Plymouth boot theme (`amethyst-boot --apply` / `--restore`), requiring sudo and an initramfs rebuild. Never enabled silently.
- Expanded optional app selection: individual creative/productivity/dev choices and explicit Flathub selections for Steam, Discord, OBS Studio and Flatseal.
- More Settings menu actions for appearance, scaling, workspace selection and boot-splash management.

## Safety and known limitations

- Existing Niri, GNOME, and user configs remain protected; upgrades require opt-in replacement with backups.
- Light/Dark is coordinated for supported tools, not a guarantee every Flatpak, Electron or proprietary app follows the palette.
- 100% / `auto` avoids extra Amethyst text magnification; Niri chooses actual monitor scale itself. Existing terminal windows may need a restart to pick up fonts.
- The optional Plymouth theme only changes the graphical splash, not firmware, GRUB, GDM or the Linux distribution name. Test boot carefully before using it on a primary system.
- Fedora packages and external Flatpak packages are third-party dependencies with their own update cycles and security risks.
- Native `niri validate` and actual graphical/hardware boot were **not available in the build environment**; run on Fedora before declaring stable v1.

## Install and test

First back up your running configuration. On an extracted repository:

```bash
bash tests/validate.sh
bash install.sh --dry-run
bash install.sh
```

Choose **Replace existing configs (with backups)** to upgrade an existing AmethystOS setup. Once the replacement is deployed, log out of GNOME and select Niri; try `amethyst-settings`, `amethyst-theme light`, `amethyst-scale 125`, and the five workspace shortcuts.

If anything fails, return to GNOME and use `amethystos-uninstall --dry-run` before restoring. Do not interrupt a Plymouth `-R` initramfs rebuild.
