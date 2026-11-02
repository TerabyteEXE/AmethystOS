# ✳ Kuhl OS v0.5 — Fedora Workstation, made cozy

Kuhl is a repeatable **Fedora GNOME configuration**, not yet an independent Linux distribution. This release includes a text installer, an original default wallpaper, a **Spotlight-style launcher on Super+Space**, a selected set of GNOME extensions, and a command to **capture the extra extensions/apps from your existing desktop**.

Website: https://terabyteexe.github.io/Kuhl-OS/main.html  
Video reference: https://www.youtube.com/watch?v=8QSJSZdUawk

> **Release status: experimental.** Automated script checks pass, but this specific release has not been tested on a physical Fedora 44 GNOME 50 machine. GNOME Shell extensions are third-party code; version support is checked at installation, but functionality still needs a real GNOME Wayland login test. The exact contents of the reference YouTube video have not been verified.

## Install with one command

Upload the **contents** of the `Kuhl-OS/` folder in the ZIP to the `main` branch of your existing GitHub repo, preserving any existing `main.html` and `LICENSE`. Then, on a fully booted and logged-in **Fedora Workstation GNOME** desktop, open Terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/Kuhl-OS/main/bootstrap.sh | bash
```

Review remote installation scripts before running them. The bootstrap downloads the public GitHub `main` archive, then opens the installer menu. Don't run the installer with sudo; it asks for sudo only when needed. It does not support Silverblue, KDE or other ostree systems.

**Already installed Kuhl v0.3 or v0.4?** Upload the updated files, then rerun the command above. It reuses existing app installations and updates the new desktop settings. Save any work before choosing reboot.

## What the installer sets up

- **Base, required:** GNOME Tweaks, Extension Manager, GNOME Extensions app, Kuhl theme assets, Papirus icons, Noto Sans and JetBrains Mono fonts, and Fedora's User Themes extension.
- **Search, required:** [Spotlight](https://extensions.gnome.org/extension/10666/spotlight/), a floating search box for apps, files, system settings and calculations. Kuhl assigns **Super+Space** to Spotlight and moves GNOME's keyboard-layout switching to **Super+Alt+Space** (reverse: **Shift+Super+Alt+Space**).
- **Reference setup, on by default:** ArcMenu, Dash to Dock, Blur my Shell (by aunetx), and Fedora Background Logo with a Kuhl logo overlay. User Themes is required. These are the extensions confirmed from the working Kuhl desktop. GNOME Extensions is a utility, not another extension.
- **Other selectable extensions, off by default:** Just Perfection, AppIndicator, Tiling Assistant, Caffeine and Rounded Window Corners Reborn. Enable these only if you want them.
- **GPU effects:** Blur my Shell is on by default because it is in the reference setup; it can be disabled in the text menu. Rounded Window Corners is optional.
- **Optional apps:** Flatseal, Pika Backup, VLC, GIMP, Inkscape, and LibreOffice. Fedora's regular apps are kept intact.
- **Optional login branding:** Add the Kuhl logo to GDM using supported GNOME system configuration. It does not replace the GDM login wallpaper or authentication greeter.
- **Reboot:** The installer offers to reboot after a successful installation; new extensions may only be activated after a new GNOME session.

There is no bundled AI, background daemon, custom package manager or disabled Fedora security service. Flathub is added to the current user to install Extension Manager and selected optional apps. Extensions are downloaded from `extensions.gnome.org` with compatibility metadata checked against the detected GNOME major version.

## New default wallpaper

`assets/wallpapers/kuhl-default.png` is the **new bundled default** for both light and dark GNOME backgrounds. The older Day and Dusk wallpapers remain bundled as an alternative.

After installation:

```bash
~/.local/bin/kuhl wallpaper default  # new landscape
~/.local/bin/kuhl wallpaper classic  # previous Day/Dusk pair
~/.local/bin/kuhl theme dusk         # dark app and shell appearance
~/.local/bin/kuhl theme day          # light app and shell appearance
```

To customize the default for everyone, replace `assets/wallpapers/kuhl-default.png` with a PNG of your choice, commit it to GitHub and rerun Kuhl. 2560×1440 or higher is recommended. To apply an already-installed new wallpaper without reinstalling, run `kuhl wallpaper default` (full path above if `~/.local/bin` isn't in your `PATH`).

## Capturing your current working setup (important)

You said you installed extra extensions and forgot which. The **capture tool** inventories them without reading your files, history, account tokens or extension-specific preferences:

```bash
~/.local/bin/kuhl capture
```

This creates **`~/kuhl-capture.json`** with:

- Fedora/GNOME version
- enabled/installed GNOME extension UUIDs
- which enabled extensions are missing from Kuhl's current default list
- installed Flatpak application IDs and (when available) user-installed Fedora RPM package names
- a small whitelist of non-private GNOME appearance settings

The JSON does **not** change the installation. **Review it before sharing it**. Upload it in a chat or inspect it locally; then the remaining extensions can be evaluated and incorporated into `config/choices.json` and `config/extensions.tsv` so the next person gets your exact setup automatically. It does not auto-install all of your personal apps onto other people's machines.

For deeper, optional replication of extension preferences (dock positioning, blur intensity, sizes, etc.), you may use:

```bash
~/.local/bin/kuhl capture --with-extension-prefs --overwrite
```

This creates a separate `~/kuhl-capture.extensions.dconf` that **may include private URLs, usernames or other sensitive extension configuration**. Review and redact it before sending or putting it on a public repository. Do not copy it into GitHub unreviewed.

If you're still on Kuhl v0.3, you can run the new capture script **directly from the extracted v0.5 ZIP** using `python3 scripts/capture.py` before updating anything.

## Testing and diagnostics

```bash
bash tests/validate.sh                  # script and simulated GNOME tests
bash install.sh --dry-run              # recommended selections; no changes
bash install.sh --defaults --no-reboot # install without menu or reboot
~/.local/bin/kuhl doctor               # check prerequisites and shortcut
~/.local/bin/kuhl capture              # inventory this desktop
~/.local/bin/kuhl uninstall            # restore tracked preferences
```

The installer records its status in `~/.local/state/kuhl/install.log`. An extension may be installed but not appear active until you log out and back in on GNOME Wayland. Confirm Spotlight is enabled in **Extension Manager**, and that `dconf read /org/gnome/shell/extensions/spotlight/toggle-shortcut` prints `['<Super>space']`. If it doesn't open, check for another launcher bound to that shortcut.

The uninstall restores Kuhl-tracked GNOME settings only when they haven't been edited since Kuhl set them. It restores the Spotlight key when appropriate, removes Kuhl assets and removes only extensions that its installer originally installed. Fedora packages and user-selected apps are retained so unrelated software isn't broken.

## Important limitations

1. **Installed extension names are now captured, but not their settings.** Use `kuhl capture --with-extension-prefs --overwrite` and review the separate settings file to replicate the dock/menu appearance on another machine.
2. **GNOME extensions are not themes for GDM.** This installer supports a small optional GDM login logo only.
3. Compatibility metadata doesn't guarantee zero GNOME Shell bugs; always validate a clean Fedora installation before calling it stable.
4. The website currently describes a four-extension limit, Ctrl+Space and a coming-soon script. Update it to reflect the actual release before advertising Kuhl as ready.

Copyright and licenses of upstream Fedora, GNOME, Flatpak and extensions remain with their authors. Kuhl's theme and wallpaper assets are independent project assets.

## Confirmed installed extensions in the reference desktop (v0.5)

| What you called it | Exact extension / tool | Default |
| --- | --- | --- |
| Background-logo | `background-logo@fedorahosted.org` (Fedora RPM) | On |
| User theme | `user-theme@gnome-shell-extensions.gcampax.github.com` (Fedora RPM) | On |
| Arc menu | `arcmenu@arcmenu.com` (requires `gnome-menus`) | On |
| Blur my shell / aunetx | `blur-my-shell@aunetx` (`aunetx` is its author) | On |
| Dash to dock | `dash-to-dock@micxgx.gmail.com` | On |
| GNOME Shell Extensions | `gnome-extensions-app` (utility, not a shell effect) | Installed |
| Spotlight | `spotlight@nin` (additional requested launcher) | On |

The baseline matches **installed extensions by name**, not your personalized configuration for
ArcMenu, dock position, blur intensity, etc. To reproduce those exact visual choices, run
`kuhl capture --with-extension-prefs --overwrite`, inspect the resulting private dconf file,
and redact secrets or file paths before sharing. This is an experimental build that still
needs a clean Fedora GNOME 50 installation test.
