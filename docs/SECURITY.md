# Important: AI-assisted code and installation security

**Kuhl OS is experimental and AI-assisted.** It is not audited, reviewed, or guaranteed secure. AI-generated or AI-modified scripts can contain destructive bugs, incorrect assumptions, insecure defaults, weak error handling, or risky installation commands.

Before installing, personally examine `bootstrap.sh`, `install.sh`, `lib/common.sh`, `bin/kuhl`, `scripts/render.py`, `scripts/desktop.py`, `scripts/validate_niri.py`, and the dependency list in `config/choices.json`. Consider testing on a VM or secondary Fedora machine. Inspect the package repository URLs and the COPR provider before enabling third-party packages. Save copies of configuration and personal files *outside the machine* before replacing dotfiles.

The public one-line command uses `curl | bash` for convenience, and its GitHub **main** branch is not pinned to a signed immutable release; the contents can change. To review first, download the repository from GitHub, inspect the scripts and execute `bash install.sh` locally. A hash for a trusted, pinned release would provide stronger protection than following an editable branch.

Run the installer as a **normal user**, not under sudo. The script invokes `sudo dnf` where packages are installed. Kuhl preserves existing configs by default, asks before replacing them, and stores backups at `~/.local/state/kuhl/backups/` when replacing. Backups are not a substitute for full system backups. GNOME is intentionally retained as an alternate login session.

This is a desktop customization layer, **not** a secure-by-design distribution, an audited security product, or a substitute for Fedora security updates. This disclosure also applies to source code generated or modified in later Kuhl releases.
