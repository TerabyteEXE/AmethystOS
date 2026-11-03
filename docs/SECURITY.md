# Security notice

Kuhl OS is an **AI-assisted community desktop project**, not a security-audited distribution or a replacement kernel. It customizes Fedora Workstation.

- Read `bootstrap.sh`, `install.sh`, `scripts/`, and `third_party/niri-dotfiles/` before running anything.
- `curl ... | bash` executes code from the repository owner and can change between installs; review or pin a tag/commit when possible.
- Core packages come from Fedora repositories. Vicinae is an **optional third-party COPR** requiring separate confirmation.
- Never run the installer as root. The only sudo operations should be reviewed Fedora package installations.
- Existing configs are preserved by default; replacement needs `REPLACE` confirmation and creates backups.
- This configuration is experimental. Test it in a VM or spare installation and keep GNOME as a fallback.
- Review upstream and dependency licenses individually before redistribution.
- Report vulnerabilities privately to the repository maintainer; do not post credentials.
