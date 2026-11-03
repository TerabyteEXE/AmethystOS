# Verification checklist — v1 base

Automated: `bash tests/validate.sh`. On Fedora with `niri` installed, the native Niri KDL parser runs against the staged complete config.

Manual Fedora GNOME/Niri login test (not verified in the development container):
1. On Fedora Workstation, log in to GNOME and install Kuhl from the extracted ZIP. Confirm desktop session **Niri** appears in GDM.
2. Log in to Niri. Check Waybar, Mako, Fuzzel (`Super+Space`) and terminal (`Super+Enter`).
3. Create two terminal windows, scroll between columns, close using `Super+Q`; test workspaces and Niri help overlay.
4. Open `Super+P` power menu and use *Lock* to verify GTKLock.
5. Click Waybar network/audio/Bluetooth/notifications/clipboard controls, including the menu scripts.
6. Add a wallpaper to `~/Pictures/wallpapers/` and use `set-wallpaper`. Log out and back in.
7. Verify `xdg-desktop-portal` OpenURI/file chooser and screen sharing in a Wayland-compatible application.
8. Check correct scaling on laptop/desktop/external monitor, suspend/resume and an X11 application.
9. From GNOME, test `bash install.sh --replace`; inspect backup folder and `bash uninstall.sh` recovery.
10. Reboot and verify GNOME remains available. Repeat after Fedora update.

Known caveats: packaged Nerd font fallback differs slightly from upstream's exact Fira Code Nerd font; source wallpapers are excluded pending rights verification; GPU and portal behavior vary across hardware. Do not mark this stable solely on the CI green checkmark.
