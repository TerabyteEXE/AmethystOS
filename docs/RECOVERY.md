# Kuhl Frontier recovery

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

Kuhl deliberately does not replace existing Niri/Waybar/Kitty/Mako/Rofi/Fuzzel configs by default. To get the new Frontier look, review them first, and run:

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
```

In the Kuhl terminal menu, select **Replace existing desktop settings (with backups)**, then type `REPLACE` at the separate confirmation. Allow the native validator to pass, and log out and back into Niri. Older shortcuts differ: Ctrl+Super+K is now keyboard help; moving a window up is Super+Shift+K. Lock is Super+Alt+L.

### Small VM storage

If DNF says the root filesystem has insufficient space, do not remove arbitrary system files. Check `df -h /`, use `sudo dnf clean all` for cached RPMs, and consider enlarging the VM disk. Kuhl's installer now gives a low-space warning before DNF.
