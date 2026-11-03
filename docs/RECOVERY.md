# Kuhl Recovery

**GNOME stays installed.** If Niri freezes or a new setup refuses to launch, log out and select GNOME from GDM. Use a text console with `Ctrl+Alt+F3` when the graphical session is frozen. The installer does not remove GNOME or modify your Fedora bootloader.

### Inspect a failed Niri session

```bash
niri validate
kuhl doctor
cat ~/.local/state/kuhl/install.log
```

The installation validates all six staged Niri theme configurations before touching dotfiles. If validation fails after deployment, it leaves files in place for diagnosis rather than silently deleting earlier managed files.

### Go back to previous configs

```bash
kuhl uninstall
```

This restores backed-up pre-Kuhl files and removes new Kuhl-managed files **only if their contents match Kuhl's last recorded hash**. It never destroys user-edited configs, and it leaves original backups at `~/.local/state/kuhl/backups/`. RPMs, third-party repositories, and files Kuhl didn't create remain.

### If your existing config survived installation

Kuhl deliberately does not replace existing Niri/Waybar/Kitty/Mako/Rofi/Fuzzel configs by default. To get the new Niri rice, review them first, and run:

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
```

In the Kuhl terminal menu, select **Replace existing desktop settings (with backups)**, then type `REPLACE` at the separate confirmation. Allow the native validator to pass, and log out and back into Niri. Older shortcuts differ: Ctrl+Super+K is now keyboard help; moving a window up is Super+Shift+K. Lock is Super+Alt+L.

### Small VM storage

If DNF says the root filesystem has insufficient space, do not remove arbitrary system files. Check `df -h /`, use `sudo dnf clean all` for cached RPMs, and consider enlarging the VM disk. Kuhl's installer now gives a low-space warning before DNF.

## v1.0 RC2 scaling/settings recovery

If scaling is wrong but you can open the terminal, run:

```bash
kuhl display reset
kuhl ui reset
kuhl bar reset
```

If the display is unusable, return to GNOME at the login screen, or press **Ctrl+Alt+F3** for a text console. As your **normal user**, edit `~/.config/niri/output.kdl` to remove only the output scale blocks. Check the configuration with `niri validate` before logging back into Niri. The managed-file protection may then require a reinstall with the explicit replacement-and-backups choice to restore Kuhl management.

GTK color-scheme and icon-theme preferences may carry into GNOME because they are stored per user. `kuhl uninstall` attempts to restore the original values only if you have not changed them since Kuhl applied them. GTK / other app configurations edited manually are protected.
