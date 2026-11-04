# Website and CI maintenance

- `index.html`, `about.html`, `install.html` and the informational wiki pages are hand-maintained HTML.
- `wiki/keybinds.html` is generated from `payload/niri/keybinds.kdl`. Run `python3 scripts/build_site.py` after changing bindings.
- `bash tests/validate.sh` validates source, direct links, CLI behavior, and backups.
- Keep **one** repository root when pushing to GitHub; never upload an `AmethystOS-main` directory inside itself.
- The default installer copies the official images only when each filename is missing; existing images and saved wallpaper selections are preserved.
- Niri-native validation requires Fedora/Niri; CI on a generic Ubuntu runner does not replace a real Fedora graphical test.
