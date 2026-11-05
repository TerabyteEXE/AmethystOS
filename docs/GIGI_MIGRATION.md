# Gigi's Rice: Fedora integration and upgrade notes

The reference supplied for this release is **Gigi's Rice** by Gigi (MIT), a Niri + Noctalia **v4.7.7** configuration originally targeting Arch. This is a configuration rebase, not a rewrite or a port to Noctalia v5.

## Version compatibility (read before installing)

- Fedora 44 distributes **Noctalia v5** in official repositories. Its new configuration and command APIs are not compatible with the archived v4 shell.
- Gigi's project explicitly says v4.7.7 is required and the repository is archived.
- The legacy v4.7.7 runtime is available through third-party Fedora sources such as **Terra**. Review the provider and its signing policy first. AmethystOS does not enable external repositories without explicit consent.
- The `--allow-terra` flag opts into a third-party bootstrap command documented by Noctalia legacy. That particular bootstrap uses `--nogpgcheck`; avoid using it if your security policy disallows this.
- If the legacy package is unavailable or broken on your Fedora release, the installer stops before deploying your new desktop configuration. GNOME is not removed.

Noctalia v4 documentation: https://docs.noctalia.dev/noctalia-shell-legacy/getting-started/installation/
Noctalia v5 documentation: https://docs.noctalia.dev/noctalia/getting-started/installation/
Gigi's original repo: https://github.com/deadduck-09/gigis-rice

## Changes to Gigi's original

- **Preserved:** actual Niri modular layout, animation shader, window styling, Noctalia Shell v4 configuration, plugins, terminal, MPV, MPD, rmpc, Yazi, Neovim and Fish configurations.
- **Adjusted for Fedora:** removed Gigi's hard-coded eDP-1 1366×768 monitor config and machine-specific polkit path; removed personal launcher defaults, per-user image paths, unneeded MPD MPRIS auto-start, SDDM wallpaper editing hook, and other custom launch commands that are not available.
- **Amethyst identity:** changed accent tokens to purple, retained Amethyst Dark/Light wallpapers, Fastfetch crystal logo, five named workspaces, and the user's familiar keybinds.
- **Shell separation:** old Amethyst Waybar/Fuzzel/Mako/GTK launcher files are retired only if still unchanged from an Amethyst-managed version. Old user-edited files are preserved; may need manual cleanup.
- **Third-party content:** original media preview videos and Gigi's anime wallpapers are not redistributed. Included plugins may have licenses separate from Gigi's top-level MIT license; see plugin manifests and any bundled `LICENSE` files.

## Installation / recovery

Run `bash install.sh --dry-run` before installation. Upgrade requires replacing the managed configs with backup. `amethystos-uninstall --dry-run` previews safe restoration; `amethystos-uninstall` restores original files if unchanged. Packages are not uninstalled.

If you previously installed legacy Noctalia or a v5 binary, check which `qs` you are running and the version of `noctalia-legacy` before logging in. Never delete your original GNOME session. Use a TTY or GNOME to recover, check `journalctl --user -b`, and run `niri validate`.

## Known limitations

- A live Fedora login has not been tested in this development environment. The portable tests can validate files, installers and migration but cannot guarantee Niri/Noctalia graphics, hardware, shell plugin compatibility, or animations.
- Some plugins rely on separate optional software or remote plugin catalogs; the code is bundled but individual functions may need additional dependencies.
- Noctalia v4 is archived. There is no promise of continued security or compatibility updates; plan a future, tested port to maintained v5 before presenting this as a long-term stable system.

## Fedora 44 package hotfix (RC3.1)

Fedora's image-conversion package is called `ImageMagick` (capital M), not `imagemagick`.
RC3.1 corrects that required dependency and adds a simulated package-install regression test.
The installer also now honors an explicit empty optional-app selection.
The failed DNF transaction occurs before dotfiles are deployed; it does not require a Fedora reinstall.
Noctalia legacy remains a separate third-party dependency requiring explicit approval and testing.
