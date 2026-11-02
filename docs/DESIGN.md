# Design & technical decisions (v0.2)

Kuhl is a Fedora Workstation styling and GNOME-extension collection, not a Fedora derivative image yet. It keeps Fedora's security defaults, update system and core apps unchanged. Everything runs in the ordinary user session.

## Palette

Day: warm cream, sage and muted peach. Dusk: slate blue, lavender and a moonlit amber accent. Kuhl ships original 2560 × 1440 Day and Dusk wallpapers, plus CSS themes in `assets/themes` that import GNOME's own Shell stylesheet and override only a few UI selectors. The imports keep default shell styling for controls not explicitly customized. Shell theme compatibility still needs real GNOME 50 testing.

The visual style is not a full replacement for GTK4/libadwaita. Kuhl uses the normal GNOME light/dark mode and warm orange accent; Papirus and adw-gtk3 bring consistency to icons and older apps.

## Extensions

Instead of a fixed four-extension cap, `full` installs a small set of seven vetted third-party GNOME extensions, in addition to Fedora's User Themes package: Dash to Dock, Just Perfection, AppIndicator, Tiling Assistant, Caffeine, Blur my Shell and Rounded Window Corners Reborn. `balanced` skips the two GPU effects, while `none` skips all third-party GNOME extensions.

The GNOME extensions downloader verifies each extension's declared GNOME Shell major version and UUID before handing it to `gnome-extensions`. It only downloads from HTTPS `extensions.gnome.org`; it records the UUIDs it installed for removal, never uninstalling unrelated user extensions. Unsupported versions are skipped. All GNOME extensions execute in the Shell process, so too many incompatible modifications can still cause bugs.

## Launcher

The website's Ctrl+Space floating search is still a design concept. v0.2 uses GNOME's Overview search shortcut, which is far more resilient than custom search UI and requires no daemon. Apps/settings are searchable; file search depends on provider/indexer state.

## Recovery

User GNOME settings are backed up before changing them; the first original values survive reinstalls, and uninstall restores only values not subsequently changed by the user. Kuhl does not delete Fedora DNF dependencies on uninstall. The included shell themes are removed only if their Kuhl marker is present. Extension switching back to balanced removes only Kuhl-installed effects.
