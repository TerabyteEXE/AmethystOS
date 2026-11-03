# Kuhl Frontier 1.0-rc1 testing plan

1. `bash tests/validate.sh` — static/bash/python manifest checks, generated keys check, isolated deployment, modified-file preservation and uninstall.
2. On **Fedora with Niri installed**: `python3 scripts/validate_niri.py` — *real* Niri parser validates all six themes in a temporary folder. It does not change personal configs.
3. For developers: `bash install.sh --dry-run` previews defaults. For end users: the one-command installer opens the Kuhl terminal menu; enable **Replace existing desktop settings (with backups)** and type `REPLACE` if you want to apply the rice over an existing Niri/Kuhl configuration.
4. On the login screen, enter Niri. Verify the full-width status bar, Rofi launcher Super+Space, shortcut guide Ctrl+Super+K, control center Super+D, graphical theme gallery Super+Shift+T, Super+Shift+P power choices, keyboard actions, and wallpaper set/reset.
5. Test safe recovery: GNOME login works, `kuhl doctor` reports all expected binaries, and `kuhl uninstall` restores unchanged tracked configs.
6. On a real AMD/NVIDIA GPU, test GPU acceleration, suspend/lock/unlock, screenshots, dual displays, network and Bluetooth tray, volume/media keys and screen sharing with XDG portals. This cannot be simulated by the static tests.

A working screenshot of the desktop is **not** bundled; the website preview is an illustration of intended layout. Do not represent it as live proof until personally tested.
