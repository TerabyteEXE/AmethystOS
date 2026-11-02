# Capture the setup you want everyone to get

The best source of truth is the working Kuhl machine, not guessed extensions or a screenshot.

1. In Fedora Terminal run `gnome-extensions list --enabled` to inspect the currently active extensions.
2. Run `~/.local/bin/kuhl capture` (or `python3 scripts/capture.py` from this repo) to create `~/kuhl-capture.json`.
3. Review the JSON. It contains extension IDs, installed Flatpak app IDs, a GNOME version and a few appearance settings, not personal documents.
4. Compare `extra_enabled_extensions` with `config/extensions.tsv` and `config/effects.tsv`.
5. For each approved extra extension, find the *official* extensions.gnome.org page and exact UUID. Add it to the TSV and to `config/choices.json`, with clear human-readable description. Check whether it conflicts with existing extensions.
6. If you want your precise per-extension preferences (e.g. dock position), use `kuhl capture --with-extension-prefs` to generate a **separate private .dconf**. Manually audit every setting and remove personal strings before publishing a curated preset. Do not blindly import an entire user's dconf database on someone else's system.
7. Test installation on a clean Fedora virtual machine, reboot/sign out, check `gnome-extensions list --enabled`, test Super+Space, light/dark themes, default wallpaper, and `kuhl uninstall`.

The video reference alone is not enough to confirm app lists and settings. Keep versioned, reviewed manifests instead of relying on a mutable tutorial.
