> Historical note for Kuhl v0.6.1, not current v1.0 RC1.

# Kuhl OS v0.6.1 — Niri parsing fix

The v0.6 sample Niri config contained invalid KDL: `keyboard { numlock }`.
The corrected configuration puts bare flags on individual lines (and expands
other compact sections for readability). Fedora/CI now uses **Niri's own parser**
for the two original Day and Dusk themes in an isolated temporary directory before installation.

If your previous installation printed a successful rollback with `[removed]`
messages, you can extract this updated ZIP and run `bash install.sh` again on
Fedora Workstation. Already installed packages don't need to be removed.

If you need a quick fix in a checked-out old project, edit
`configs/niri/config.kdl` to put `numlock` on its own line, then retry.

Do not manually create the live `~/.config/niri/config.kdl` until you've
validated the staged config; `niri validate` reports the active config.

**Note:** The native config check runs on Fedora with Niri installed; local
static tests on other operating systems are not a substitute for native validation.
