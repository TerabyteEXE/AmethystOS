# AmethystOS · Noctalia v5 migration

This release replaces the archived Quickshell-based Noctalia v4 with the native
**Noctalia v5** shell available through Fedora's standard repositories.
The two versions **do not automatically migrate** their settings. The Niri
compositor, window rules, and workspace shortcuts remain based on the
previous working desktop.

## Before installing

1. Back up your home directory or take a VM snapshot.
2. Log into GNOME when upgrading an existing desktop, and close the old v4
   shell before switching sessions.
3. Use `bash install.sh --dry-run` to check bundled files. Then install and
   choose **Back up and replace existing configs**.
4. Log out; choose **Niri**. Fedora's `noctalia` v5 will start as the shell.

AmethystOS's deploy tool archives your old `~/.config/noctalia` directory and
other managed paths. Restoration uses `amethystos-uninstall`, refuses to
overwrite modified files, and does not remove Fedora packages. The old v4
RPM may remain installed; it will not be auto-started by the new Niri config.

## Config differences

| v4 | v5 |
|---|---|
| `~/.config/noctalia/settings.json` | `~/.config/noctalia/config.toml` |
| `~/.config/noctalia/colorschemes/` | `~/.config/noctalia/palettes/` |
| `qs -c noctalia-shell ipc call ...` | `noctalia msg ...` |
| Quickshell QML plugins | Require v5-compatible native plugin versions |

Your existing v4 plugins are not deployed into v5. The original upstream license
remains in the repository. Fedora's signed repositories supply the v5 package;
no third-party Terra source is enabled by the new installer.

## Recovery

From GNOME or a terminal:

```bash
amethystos-uninstall --dry-run
amethystos-uninstall
```

This restores your pre-Amethyst managed dotfiles when unmodified, but cannot
guarantee all external package/version changes will be reversed. For a full
machine rollback, restore your VM snapshot or system backup.

Official docs: https://docs.noctalia.dev/noctalia/getting-started/installation/
