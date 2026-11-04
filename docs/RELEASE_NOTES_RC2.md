# AmethystOS v1 RC2 — Desktop integration and installer polish

This update keeps the known-working upstream Niri layout while improving its supporting applications and first-run experience.

## Changes

- Seven-stage terminal installer with a keyboard-driven optional-software menu. Application choices come from a curated list of Fedora packages, not arbitrary external installer scripts.
- Reversible GTK theme preferences, bundled Qt6 theme configuration, an Amethyst Settings menu and desktop launcher. GTK, Qt, Electron and Flatpak applications do not all share the same theming mechanism; some third-party apps may still need separate configuration.
- Monospaced font settings aligned to Fedora's Cascadia Mono NF package, plus adjusted sizes for Alacritty, Kitty, launcher and Waybar.
- Waybar tray, settings button, and repaired notification, audio, network and clipboard actions. Settings failures can be inspected in `~/.cache/amethystos/launch.log`.
- Both AmethystDark.png and AmethystLight.png copied on installation without overwriting existing images. Fresh desktops default to the dark wallpaper; previous wallpaper choices are preserved.
- Persistent `amethystos-uninstall` command with safeguards for changed files. Backups from the original pre-Amethyst installation are retained even through repeated replacements.
- Installer now asks permission to replace existing dotfiles *before* invoking DNF.

## Installation and recovery

Use `bash install.sh --dry-run` to inspect the plan, or `bash install.sh` for a normal setup. Upgrades can be initiated with `bash install.sh --replace`, or the replace option inside the interactive terminal setup. Log out of Fedora, select Niri, and log back in.

After installation:

- `amethyst-settings` — desktop settings, including GTK appearance and wallpapers.
- `amethyst-doctor` — checks and recent Amethyst Settings launch errors.
- `amethystos-uninstall --dry-run` — inspect restore actions.
- `amethystos-uninstall` — restore the original, tracked user configurations.

The uninstaller leaves GNOME, DNF packages and personal wallpapers installed. It will refuse to remove tracked configurations that were changed after the last installation, to avoid data loss.

## Release verification

Portable installer, package, website, theme, wallpaper, config-protection and multi-upgrade restore tests passed. Native Niri config parsing and graphical Fedora tests **could not be run in the build environment**. Before marking this as stable v1, test a real Fedora/Niri login, portals/screen sharing, application launchers, Waybar click targets, audio/Bluetooth, display scaling, and restore on the target hardware.

This project contains AI-assisted code and has not been independently security-audited. Review scripts, especially the one-line remote bootstrap, before executing them.

## RC2.1: interactive setup correction

- Fix the installer crashing with `io.UnsupportedOperation: File or stream is not seekable` when run using `curl ... | bash`. Read and write `/dev/tty` through separate streams instead of an `r+` text stream.
- Resolve the duplicate `8` menu option: number 8 now selects gaming apps, number 9 selects backup-and-replace, and 10 controls GTK appearance.
- Add a pseudo-terminal integration test that simulates piped stdin and verifies the saved install plan. No system packages are installed during the test.

The fix changes only setup and tests; desktop configs, wallpapers, GNOME fallback, and recovery behavior are unchanged.
