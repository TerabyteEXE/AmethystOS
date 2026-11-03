# Recovery and uninstall — Kuhl OS 0.6.1

Kuhl keeps stock Fedora Workstation and GNOME installed. The Niri compositor is a separate login session.

**If you cannot enter Niri:** log out or reboot to the login screen, open GDM's session menu, select GNOME, and sign in. Do not remove GNOME until Niri is proven stable. If both sessions fail, use a TTY (`Ctrl+Alt+F3`) and log in there.

1. Inspect `~/.local/state/kuhl/install.log` and run `niri validate` from a terminal.
2. Run `kuhl doctor`; make sure `~/.config/niri/config.kdl` is Kuhl-managed or intentionally custom.
3. If a previous custom config blocked Kuhl, the installer intentionally skipped it. Back it up, then run `bash install.sh --replace-configs` from the downloaded source. Your original is copied to `~/.local/state/kuhl/backups/`.
4. To exit Niri with confirmation, press `Super+Shift+E`.

**Uninstall:** `kuhl uninstall` restores previously replaced config files only when the deployed Kuhl files are unchanged. Files you manually edited are left alone. Uninstall does not remove Fedora RPMs, Flatpaks, COPR repositories, wallpapers, backups, GNOME extensions, or system security settings.

**Optional package/repo cleanup:** Review `dnf history` before removing any packages installed by Kuhl because other programs may depend on them. If you explicitly enabled Vicinae, inspect `dnf copr list` and disable that COPR manually if you no longer trust or want it. Kuhl never reverses package transactions automatically.

**Legacy note:** Kuhl 0.5 used GNOME extensions and dconf changes. Kuhl 0.6 does not automatically reverse them. Recover v0.5 with its original uninstall procedure, not the 0.6 Niri uninstaller. Do not wipe `.local/state/kuhl` without checking backup history.
