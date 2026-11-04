# Optional applications

The AmethystOS terminal installer includes essential Niri services regardless
of your selection. You may choose Firefox, Chromium, everyday apps, office/mail,
creative software, development tools, media apps, and gaming helpers.

The list is intentionally limited to packages expected in the enabled Fedora
repositories and does not enable RPM Fusion or COPR automatically. Optional
apps that are unavailable are skipped with an explicit warning. In particular,
Steam and proprietary media codecs require separate user research and consent.

App configuration themes can vary:

- GTK3: adw-gtk3, selected through GTK settings / GSettings.
- GTK4/libadwaita: GNOME color-scheme preference.
- Qt6: qt6ct and the Niri QT_QPA_PLATFORMTHEME setting.
- Electron / Flatpak: may use their own runtime, launch arguments and theme.

The user-installed recovery tool `amethystos-uninstall` removes managed
dotfiles, not DNF packages (to avoid removing applications you use elsewhere).
To diagnose a failed app, launch it in Alacritty and run `amethyst-doctor`.
