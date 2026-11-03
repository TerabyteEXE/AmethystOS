# Kuhl OS — release gate

Before labeling this stable v1:

- [ ] Fedora 44 fresh Workstation install succeeds using public one-line bootstrap command
- [ ] `bash tests/validate.sh` passes in GitHub Actions
- [ ] `python3 scripts/validate_niri.py` passes using real Fedora Niri binary
- [ ] Niri graphical login works on a real AMD/Intel machine (and a 3D-capable VM)
- [ ] Super+Space, Super+Enter, Super+D, Ctrl+Super+K, Super+Q all work
- [ ] Network/audio/Bluetooth settings launch from terminal Control Center
- [ ] Waybar vertical modules, position/scale controls and close icon function
- [ ] Wallpaper, themes and monitor scaling function after restarting Niri
- [ ] Screen sharing/portals, idle locking and suspend tested
- [ ] Existing Niri config replacement creates backups; uninstall restores them
- [ ] No upstream wallpaper or unreviewed packages are distributed
- [ ] `index.html` is correct and deployment URL points at your published repo

Until then this is a **beta**, not a verified stable 1.0 release.
