# Security and risk notice

AmethystOS is experimental and AI-assisted. Its installer and scripts have **not** undergone an independent security audit. Do your own research; review source code and dependencies before running it, especially the remote bootstrap command.

What the installer does: asks `sudo` for Fedora `dnf install`; downloads packages from Fedora's configured repositories; copies only the dotfiles in `payload/` into the current user's home; validates the Niri KDL before deployment; and backs up anything it replaces.

What it does **not** do: run `curl | sudo bash` internally, enable third-party COPR repos, run the upstream Arch/AUR scripts, change GNOME or GDM, overwrite `/etc`, change your default login shell, or install development dependencies unrelated to the desktop.

Safest workflow: read the ZIP first, run `bash install.sh --dry-run`, back up important files, then try Fedora in a VM or spare system. Use `bash uninstall.sh` to restore managed settings; user-modified files are never silently overwritten. The bootstrap downloads the `main` branch, which changes over time; pin a Git commit yourself if reproducibility is critical.

Starship and other visual desktop extras are optional. A missing Starship
package never triggers automatic third-party repository configuration.
Review the package manifest in `scripts/packages.sh` before installing.
