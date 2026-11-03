# Kuhl OS v1 RC — upstream code, adaptation and artwork notices

**Kuhl OS is an AI-assisted community Fedora + Niri setup.** This directory documents the origins of source code and assets. Kuhl OS is not an official product of Fedora, Niri, KyleOS, or the artists. The release candidate is not security audited.

## Original MIT-licensed source: KyleOS by Rosenkranz / Person-008

- Repository: https://github.com/Person-008/KyleOS
- Author: Rosenkranz (also Person-008); copyright 2026.
- Software license: MIT, **except the image assets**. The full notice is preserved in `third_party/KyleOS-MIT.txt`.
- **Untouched, copied upstream files** are in `third_party/KyleOS/original/`.
- **Actual Kuhl-deployed configuration files** are under `configs/`; Kuhl starts from the original files rather than just recreating the visual appearance.

| Source in KyleOS | Used in Kuhl | Adaptations |
| --- | --- | --- |
| `root/etc/niri/config.kdl` | `configs/niri/config.kdl` | Relative includes; default US keyboard; generic cursor; Kuhl theme include; original shader preserved |
| `root/etc/niri/layout.kdl` | `configs/niri/layout.kdl` | Only a Kuhl attribution comment |
| `root/etc/niri/binds.kdl` | `configs/niri/binds.kdl` | Arch-specific scripts replaced with Kuhl CLI; shortcut guide and search added; collisions resolved |
| `root/etc/niri/window-rules.kdl` | `configs/niri/window-rules.kdl` | Kept asymmetric shapes; removed personal monitor/app restrictions and private screenshot rules |
| `root/etc/niri/output.kdl` | `configs/niri/output.kdl` | Removed hardcoded HDMI/DP names and geometry |
| `root/etc/niri/autostart.kdl` | `configs/niri/autostart.kdl` | Fedora compatible startup, Kuhl wallpaper manager, no lxsession or third-party awww requirement |
| `root/etc/xdg/waybar/config.jsonc` | `configs/waybar/config.jsonc` | Retains source as a reference; runtime generator adds Kuhl Settings/close controls, scalable layout, and a readable font |
| `root/etc/xdg/waybar/style.css` | `configs/waybar/style.css` | Retains source as a reference; runtime generator creates scale-aware and palette-aware CSS |
| `root/usr/share/rofi/themes/thematic*.rasi` | `configs/rofi/*.rasi` | Preserves the original sources separately; runtime copies are corrected for valid Rasi syntax, available fonts, and lower resolutions |
| `root/etc/thematic/{Frontier,Dyson,Puncture,SlowEnd}/{niri.kdl,rofi.rasi,alacritty.toml,mako.config}` | `configs/upstream/themes/…` | **Original files preserved byte-for-byte; Niri runtime copy fixes one malformed `urgent-color` value (`ff0000` → `#ff0000`) before deployment |

The **original KyleOS theme switcher scripts and Arch installer are not run**. Kuhl's existing installer, user-config backup system, theme manager, searchable keyboard guide and GNOME fallback are retained. Exact source fonts, GNOME/GTK packages and icon sets are not bundled because the upstream source archive does not supply independently reviewed licenses for every third-party dependency.

## PrisonerCoin art — NOT MIT

Original images provided with KyleOS are attributed by its maintainer to PrisonerCoin and governed by **Creative Commons Attribution–NonCommercial–ShareAlike 3.0 (CC BY-NC-SA 3.0)**. This attribution applies to *both* the copied animated `.gif` files, converted static PNG first frames, and original `-thumbnail.png` previews in `assets/wallpapers/third-party/`. The original GIF files are unchanged; the static PNG frames are modifications. Do not sell, relicense as MIT, or use these assets in a commercial distribution without separate authorization.

| Bundled assets | Source artwork | Author/year |
| --- | --- | --- |
| `frontier.gif`, `.png`, `-thumbnail.png` | [Final Frontier](https://www.newgrounds.com/art/view/prisonercoin/final-frontier) | [PrisonerCoin](https://prisonercoin.newgrounds.com/), 2022 |
| `dyson.gif`, `.png`, `-thumbnail.png` | [Dyson Analysis](https://www.newgrounds.com/art/view/prisonercoin/dyson-anaysis) | PrisonerCoin, 2023 |
| `puncture.gif`, `.png`, `-thumbnail.png` | [Puncture](https://www.newgrounds.com/art/view/prisonercoin/puncture) | PrisonerCoin, 2023 |
| `slowend.gif`, `.png`, `-thumbnail.png` | [Slow End](https://www.newgrounds.com/art/view/prisonercoin/slow-end) | PrisonerCoin, 2023 |

- KyleOS license explanation: https://github.com/Person-008/KyleOS#license
- CC BY-NC-SA 3.0 legalcode: https://creativecommons.org/licenses/by-nc-sa/3.0/legalcode
- **Excluded**: Survey (copyright/license permission unclear); upstream screenshots/other illustrative images, generated third-party icons, themes, font binaries and Arch-specific installation scripts.
- For commercial distribution, remove the CC BY-NC-SA images from the archive and change each art theme's `wallpaper` key in `config/themes.json` to your own authorized art. Keep the original creator attribution in historical documentation.

## Other packages (installed from independent repos)

[Fedora Workstation](https://fedoraproject.org/workstation/), [Niri](https://github.com/niri-wm/niri), [Waybar](https://github.com/Alexays/Waybar), [Rofi](https://github.com/davatorium/rofi), [Alacritty](https://github.com/alacritty/alacritty), [Kitty](https://sw.kovidgoyal.net/kitty/), [Mako](https://github.com/emersion/mako), [Fuzzel](https://codeberg.org/dnkl/fuzzel), [Vicinae](https://github.com/vicinaehq/vicinae), [Thunar](https://docs.xfce.org/xfce/thunar/start), [swaybg](https://github.com/swaywm/swaybg), [swaylock](https://github.com/swaywm/swaylock). These tools are external dependencies, each under their own license. Vicinae's optional COPR is third-party and requires opt-in.

`bootstrap.sh` fetches remote code from an editable GitHub branch. Users should read it and verify dependencies before executing it with Bash. These risks are further explained in [SECURITY.md](SECURITY.md).

**RC2 changes:** `scripts/desktop.py`, the generated Waybar layout and GTK/terminal appearance bridge are new Kuhl integration code. Modified styles and keybindings remain credited to the source design; the untouched originals remain in `third_party/KyleOS/original/`.
