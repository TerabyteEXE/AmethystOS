# AmethystOS v1 RC2.5 — Menu and Settings refinement

This update preserves the working Niri rice, installer, Light/Dark palettes, and five named workspaces.

## Changes

- Removed the optional experimental Plymouth splash from the installer, Settings, install payload, and automated tests. System boot files are not modified.
- Refined the Amethyst Settings GTK3 window to match the active desktop palette. It now uses scoped stylesheets and the real project logo; existing settings continue to apply without dismissing the window.
- **Super+Space** still offers a fast native app search with only **Amethyst Settings** and **Amethyst Menu** added. Amethyst Menu gives the same arrow-key friendly six categories as **Super+D**. No flood of per-setting launchers.
- Older unmodified user-level splash scripts are safely retired on upgrade. Manually edited ones are left alone. Boot-level Plymouth changes from earlier releases are **not** reverted automatically; see `docs/UPGRADING.md`.

## Testing

`bash tests/validate.sh` checks packaging, website keybinds, installer menus, migration, theme assets and config restore. This cannot confirm GTK rendering or live Wayland focus. Please test on Fedora/Niri before declaring stable v1.

## Upgrade

`bash install.sh` → choose replace with backups → log out and log into Niri. Your pre-Amethyst backups remain protected.
