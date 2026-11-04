# Renaming an existing installation

AmethystOS keeps the same Fedora + Niri desktop base as the previous release. The public GitHub repository name, website links, and all new installer-managed files now use **AmethystOS**.

If you already installed an earlier build, **do not delete your old backups**. Its state files remain where the previous installer placed them; this rebranded release writes new state under `~/.local/state/amethystos-base-v1/`. The new installer does not automatically move, delete, or overwrite the old state.

To upgrade:

1. Rename the GitHub repository to `AmethystOS` and publish this complete project. Verify `bootstrap.sh` is accessible in the new repository.
2. Run the updated installer. When it reports existing dotfiles, review the prompt and choose replacement to make a fresh backup.
3. Log in to the Niri session and check the desktop before removing any older checkout or backup.

The wallpaper picker uses the new saved selection file. Previously selected wallpapers are not deleted; select your preferred image again if needed.

To restore **this release**, run the installed `amethystos-uninstall` tool. It is available after remote installs, and `bash uninstall.sh` from a checkout still works. To restore older releases, use the matching older release and its backup state.

## v1 polish release

Install the update with `--replace` or select replacement in the terminal UI.
All original dotfiles are backed up; repeated upgrades retain the first known
pre-Amethyst backup and archive intermediate releases. Select optional apps
again in the new menu. The new GTK/Qt integration installs Cascadia Mono NF
and coordinates optional GTK appearance preferences with reversible backups.

The two official wallpapers are copied when missing; existing image files and
selection are preserved. The menu launcher settings are available from the
Waybar gear or Super+Shift+S.

## Upgrading from an RC2.2–RC2.4 boot splash

RC2.5 removes the optional Plymouth boot splash installer, GUI control and associated user scripts. During an upgrade, unmodified user-level copies managed by AmethystOS are retired safely; modified copies are preserved. **AmethystOS does not change the active system Plymouth theme, bootloader, or initramfs automatically.**

If you previously enabled the experimental splash and want to restore the old Fedora theme, first inspect the saved choice:

```bash
sudo cat /var/lib/amethystos/previous-plymouth-theme
```

Only if it is the expected theme and you understand the implications of rebuilding your initramfs, restore it manually:

```bash
previous=$(sudo cat /var/lib/amethystos/previous-plymouth-theme)
sudo plymouth-set-default-theme "$previous" -R
```

Rebuilding initramfs requires adequate free space and can affect boot reliability if interrupted. The new installer itself never performs either of these commands.
