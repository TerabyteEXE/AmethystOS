# Renaming an existing installation

AmethystOS keeps the same Fedora + Niri desktop base as the previous release. The public GitHub repository name, website links, and all new installer-managed files now use **AmethystOS**.

If you already installed an earlier build, **do not delete your old backups**. Its state files remain where the previous installer placed them; this rebranded release writes new state under `~/.local/state/amethystos-base-v1/`. The new installer does not automatically move, delete, or overwrite the old state.

To upgrade:

1. Rename the GitHub repository to `AmethystOS` and publish this complete project. Verify `bootstrap.sh` is accessible in the new repository.
2. Run the updated installer. When it reports existing dotfiles, review the prompt and choose replacement to make a fresh backup.
3. Log in to the Niri session and check the desktop before removing any older checkout or backup.

The wallpaper picker uses the new saved selection file. Previously selected wallpapers are not deleted; select your preferred image again if needed.

To restore **this release** use `bash uninstall.sh` from an AmethystOS checkout. To restore older releases, use the matching older release and its backup state.
