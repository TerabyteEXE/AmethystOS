# AmethystOS v1 RC2.9 — Cohesion and reliability

A focused update of the working Fedora/Niri rice. The original Amethyst Dark/Light wallpapers and Niri tiling layout are unchanged.

## Fixed

- **Home:** arrow-key selection now scrolls the visible app list; application icons use each installed desktop file’s Gio icon.
- **Home appearance:** the launcher has a single translucent, rounded GTK surface rather than GTK-theme-dependent double borders; it remains small and keyboard-first.
- **Panel overlap:** popovers dismiss when opening another Settings/application window; mute stays in the audio popup.
- **Coherence:** the Home menu, Waybar popups, wallpaper picker, Settings and themed Waybar share restrained translucent purple/neutral surfaces across Light/Dark modes. Niri's existing blur is enabled for the named popup surface.
- **Updating:** the existing Software → Update path invokes one terminal updater for Fedora RPMs, user Flatpaks and an **optional confirmed AmethystOS desktop refresh**. Desktop updates are fetched from the official GitHub main branch at a specific displayed commit hash, source URL is shown before confirmation, and the refreshed installer preserves appearance and backs up configuration files.

## Beta test on Fedora

1. From a GNOME session, run `bash install.sh --dry-run`, then `bash install.sh` with **backups and replacement**. Log into Niri.
2. Open Home (`Super+Space`), enter Apps, navigate past ten rows using Up/Down. The highlighted entry must stay visible and display its actual app icon. Enter should open an app and close Home.
3. Open an audio/clock popup, choose Settings, verify the popup dismisses.
4. Toggle Light/Dark and check Home, Waybar, popup, Settings, wallpaper picker. No manual wallpaper selection should be lost to a scale-only adjustment or desktop update.
5. Run `amethyst-update --dry-run`, then `amethyst-update check`, review the official source commit and choose a deliberate update. Ensure the original Amethyst settings can be restored using `amethystos-uninstall --dry-run` first.
6. Verify both Wayland and XWayland app icons and settings on physical hardware; the portable suite cannot verify GTK/Niri rendering or every theme/third-party app.

## Security and limits

An AmethystOS source refresh downloads **code that will execute locally** from the official GitHub repository. Read the linked commit before confirming; SHA pinning prevents a moving branch from changing between review and download, but **does not make the source trustworthy**. The updater does not update the bootloader, change repos, or install optional application bundles. Fedora and Flatpak updates use their own official tooling. No automatic/unattended updates are configured.
