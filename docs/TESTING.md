# Verification checklist — v1 base

Automated: `bash tests/validate.sh`. On Fedora with `niri` installed, the native Niri KDL parser runs against the staged complete config.

Manual Fedora GNOME/Niri login test (not verified in the development container):
1. On Fedora Workstation, log in to GNOME and install AmethystOS from the extracted ZIP. Confirm desktop session **Niri** appears in GDM.
2. Log in to Niri. Check Waybar, Mako, Fuzzel (`Super+Space`) and terminal (`Super+Enter`).
3. Create two terminal windows, scroll between columns, close using `Super+Q`; test workspaces and Niri help overlay.
4. Open `Super+P` power menu and use *Lock* to verify GTKLock.
5. Click Waybar network/audio/Bluetooth/notifications/clipboard controls, including the menu scripts.
6. Add a wallpaper to `~/Pictures/wallpapers/` and use `set-wallpaper`. Log out and back in.
7. Verify `xdg-desktop-portal` OpenURI/file chooser and screen sharing in a Wayland-compatible application.
8. Check correct scaling on laptop/desktop/external monitor, suspend/resume and an X11 application.
9. From GNOME, test `bash install.sh --replace`; inspect backup folder and `bash uninstall.sh` recovery.
10. Reboot and verify GNOME remains available. Repeat after Fedora update.

Known caveats: the Fedora Cascadia Mono NF package may differ in glyph shapes from the original rice. Original Amethyst Dark and Light wallpapers are included, but third-party wallpapers are excluded. GPU and portal behavior vary across hardware. Do not mark this stable solely on the CI green checkmark.

## Fedora 44 missing-package regression

The portable suite includes `tests/test_packages.sh`, which simulates a Fedora
DNF installation where Starship is unavailable and verifies the required
packages still install. On real Fedora 44, verify that the optional extras
message does not abort installation, then log into Niri and confirm that Fish
works with its normal prompt if Starship is missing.

## v1 polish release tests

The portable test suite also validates the terminal setup plan, missing-package
handling, wallpaper non-overwrite behavior, Waybar commands, app settings, GTK
preferences with a fake GSettings service, multi-upgrade backup preservation,
and the persistent uninstall command.

Manual release gates (must run in a REAL Fedora/Niri session):

1. Use the default app selections, then retry installation choosing Chromium
   only, to verify the Super+B browser fallback.
2. Launch both Alacritty and Kitty and check glyph width and icon rendering
   with `fc-match 'Cascadia Mono NF'`.
3. Open Amethyst Settings from Waybar and Super+Shift+S; test network, audio,
   Bluetooth (on hardware), GTK mode and wallpaper switching.
4. Launch third-party apps from Fuzzel, inspect errors in the terminal if they
   quit, and report the exact app name and error.
5. Test GTK3, GTK4/libadwaita, and Qt6 applications. Flatpaks may require
   their own theme configurations.
6. Test install → upgrade → uninstaller and confirm that original config files
   are restored and Fedora/GNOME/packages remain intact.
7. Test the Waybar tray and menu entries, multimedia controls, screenshots,
   suspending, networking and locking on the actual target hardware.

Never describe the release as "fully verified" until these tests pass.
