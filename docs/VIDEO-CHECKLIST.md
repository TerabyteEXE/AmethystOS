# Matching the video exactly

Reference: https://www.youtube.com/watch?v=8QSJSZdUawk

This release **does not claim to replicate the video's exact steps**, because its transcript and complete extension list could not be retrieved. Kuhl is now structured so those details can be dropped in without redoing the entire installer.

To finish mirroring it, collect these from the video (or paste its commands into the project issue):

1. **Fedora version**, whether it uses Wayland or X11, and any additional Fedora repos required.
2. **Applications installed**, including package source (`dnf`, Flatpak ID, or another source).
3. **Extensions installed in Extension Manager**, and each extension's official link or UUID.
4. **Specific settings** for those extensions (dock position, icons, panel padding, blur, borders, overview animations).
5. **Wallpaper, GTK theme, icon set, and cursor names**.
6. **GDM login/lock screen changes**, if any; distinguish login screen from user lock screen.

Then edit `config/choices.json`, the two `config/*.tsv` extension lists, and settings under the installer. Avoid copying the video's command for an older GNOME extension blindly: GNOME 50 requires supported versions.

No video assets or third-party theme files are repackaged into Kuhl without a usable license and source.
