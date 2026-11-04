# AmethystOS v1 RC2.3 — Search & Usability

This is an incremental update to the *working* RC2.2 desktop. It does not
replace the Niri rice or remove previous installer and recovery features.

## Changes

- **Search:** Super+Space launches the normal Fuzzel application finder, now
  with new searchable `.desktop` entries for AmethystOS actions. Super+Space
  again requests termination of only the launcher process started by this
  shortcut; Esc still works.
- **Control menu:** Super+D opens a Fuzzel keyboard-driven system menu for apps,
  settings, install/remove curated software, updates, appearance, wallpaper,
  bar, calendar, network, audio, Bluetooth, diagnosis and recovery.
- **Shortcut collision resolved:** the existing floating-window toggle moved
  from Super+D to Super+Shift+D. Other Niri tiling shortcuts stay as before.
- **Settings:** adds bar options, calendar, install/remove, and a gallery.
- **Bar:** clock opens a calendar, while the gear's right-click menu changes
  top/bottom position, compact/normal/roomy density, and optional modules.
  Preferences persist through dark/light and scale changes.
- **Wallpapers:** GTK3 thumbnail grid with scrollbar and keyboard movement;
  double-click or Apply selects the image. The old Fuzzel list remains a
  fallback for systems lacking GTK bindings.
- **Updates and packages:** software removal/install is limited to supported
  app IDs; Fedora always presents its package transaction for approval.
  Flathub is opt-in and user-scoped.
- **Quality:** extra package dependencies for the gallery, diagnostics and
  regression tests; bar changes no longer reset manually selected wallpapers.

## Safety

No configuration replacement without explicit approval in the installer.
Existing backups and the self-contained uninstaller remain. Custom Waybar
edits are not silently overwritten by the theme or bar manager. External
software repositories are not added without selection/approval.

## Release gate

The portable suite `bash tests/validate.sh` passed. Niri's own parser is
checked only on systems where Niri is installed, and GUI behavior requires a
live Fedora/Wayland session. The new features should be beta-tested before
publishing this as stable v1.

On an existing installation, select **Back up and replace existing configs**
when running `bash install.sh`. Then log out and back into Niri to reload new
bar modules, startup scripts and keybinds.
