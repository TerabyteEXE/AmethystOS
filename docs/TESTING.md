# Testing protocol

`bash tests/validate.sh` performs shell syntax checks, Python compilation, manifest and HTML content checks, menu default serialization, and isolated config generation / safe overwrite / theme / uninstall checks. It does not need Fedora or root. If Niri is installed, it also runs the native Niri parser against both themes. GitHub Actions has a dedicated Fedora 44 Niri validation job.

**On a clean Fedora 44/45 Workstation guest:**

Before testing the graphical session, run `python3 scripts/validate_niri.py` to verify both Day and Dusk in isolated temporary directories using Fedora's own Niri binary. No user configs are modified.

1. Save a VM snapshot; confirm GNOME can log in and that `bash install.sh --dry-run` changes nothing.
2. Run the TUI installer with defaults. Sign out and log in to Niri from GDM.
3. Verify Super+Space opens Fuzzel, Kitty/Thunar launch, Waybar's Niri workspaces update and mouse/touchpad controls work.
4. Test `kuhl theme day`, `kuhl theme dusk` and wallpaper choices while in Niri; check Waybar reload and Mako styling.
5. Test PipeWire volume, NetworkManager, Bluetooth (if present), X11 apps through Xwayland-satellite, screen sharing via xdg-desktop-portal-gnome, notifications and suspend/lock.
6. Enable Vicinae in an interactive run, explicitly consent to COPR, sign back into Niri and retest Super+Space and file search.
7. Test idempotence: rerun installer, manually edit a Kuhl config, rerun and ensure edit is preserved; then test explicit `--replace-configs` backups.
8. Test `kuhl uninstall`, verify managed unmodified files are removed/restored and personal files unchanged; confirm GNOME still works.

The build environment cannot execute these real-GUI tests. Do not label a build “stable” solely because CI passes.
