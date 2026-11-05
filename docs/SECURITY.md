# Security and risk notice

AmethystOS is experimental and AI-assisted. Its installer and scripts have **not** undergone an independent security audit. Do your own research; review source code and dependencies before running it, especially the remote bootstrap command.

What the installer does: asks `sudo` for Fedora `dnf install`; downloads packages from Fedora's configured repositories; copies only the dotfiles in `payload/` into the current user's home; validates the Niri KDL before deployment; and backs up anything it replaces.

What it does **not** do: run `curl | sudo bash` internally, enable third-party COPR repos, run the upstream Arch/AUR scripts, remove GNOME or alter GDM, overwrite `/etc`, change your default login shell, or install development dependencies unrelated to the desktop.

Safest workflow: read the ZIP first, run `bash install.sh --dry-run`, back up important files, then try Fedora in a VM or spare system. Use `bash uninstall.sh` to restore managed settings; user-modified files are never silently overwritten. The bootstrap downloads the `main` branch, which changes over time; pin a Git commit yourself if reproducibility is critical.

Starship and other visual desktop extras are optional. A missing Starship
package never triggers automatic third-party repository configuration.
Review the package manifest in `scripts/packages.sh` before installing.

## New v1 polish controls

The terminal interface offers Fedora package groups; no package names from user
input are interpolated into shell commands. The default dark appearance option
updates the current user's GNOME GSettings colors and icon preferences so GTK
apps follow a consistent dark style in Niri. These settings are backed up and
reverted on uninstall only while they match the last value AmethystOS wrote.
Turn off this option in the terminal GUI or use `--no-theme` to avoid modifying
GNOME appearance preferences. Some Qt, Flatpak and Electron apps use their own
appearance controls. The installer does not promise to make third-party apps
secure or repair unknown runtime crashes.

The persistent `amethystos-uninstall` command restores original dotfiles but
retains installed Fedora packages and personal wallpapers to avoid data loss.
Always test restore before relying on a newer release.


## Optional login-screen integration

`bash scripts/greeter.sh prepare/activate` is an **explicit opt-in**, separate
from `install.sh`. It installs Fedora packages from configured repositories,
backs up and updates `/etc/greetd/config.toml`, and changes the enabled display
manager on *the next boot*, without uninstalling GNOME. The optional Terra
repository must be enabled manually and is not trusted automatically. Read
[docs/GREETER.md](GREETER.md) for the complete safety and recovery procedure.
