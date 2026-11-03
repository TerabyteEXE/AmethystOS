# Third-party credits and license boundaries

**Kuhl OS v0.8 is AI-assisted. This file documents upstream code inspiration and individually licensed art.** Kuhl is not affiliated with any of the people or projects below.

## KyleOS — design and permitted code adaptations

- Original project: **KyleOS**, created by **Rosenkranz / Person-008** (2026), https://github.com/Person-008/KyleOS
- Code and dotfiles are published under the **MIT License**, **except the images**.
- The original MIT copyright and permission notice are reproduced in [`third_party/KyleOS-MIT.txt`](../third_party/KyleOS-MIT.txt). Kuhl credits KyleOS for the source's top status-line layout, asymmetric Niri window corner geometry, compact launcher appearance and theme-based palettes. The code is adapted for Fedora and Kuhl's existing management tools; KyleOS's Arch installation scripts, personal display rules, lock-screen helper, font files, generated GTK icon/theme directories and commands are **not** installed.
- Kuhl's pre-existing independent scripts retain the original Kuhl license (`LICENSE`). The MIT notice is included as an acknowledgment and condition for source adaptations; it **does not** grant rights to the artwork.

## PrisonerCoin — artwork (NOT MIT)

The following bundled PNG images in `assets/wallpapers/third-party/` are **static first frames converted from the GIF assets in the user-provided KyleOS archive**, which credits original art to **PrisonerCoin**. The conversion from GIF to static PNG is a modification; Kuhl does not claim authorship. Each image remains under **Creative Commons Attribution–NonCommercial–ShareAlike 3.0 (CC BY-NC-SA 3.0)**, not the MIT license. Redistribution or modification of these images must comply with **attribution, NonCommercial, and ShareAlike** terms; do not assume they can be reused for commercial products.

| Packaged static PNG | Original artwork | Original creator | Year |
| --- | --- | --- | --- |
| `frontier.png` | [Final Frontier](https://www.newgrounds.com/art/view/prisonercoin/final-frontier) | [PrisonerCoin](https://prisonercoin.newgrounds.com/) | 2022 |
| `dyson.png` | [Dyson Analysis](https://www.newgrounds.com/art/view/prisonercoin/dyson-anaysis) | PrisonerCoin | 2023 |
| `puncture.png` | [Puncture](https://www.newgrounds.com/art/view/prisonercoin/puncture) | PrisonerCoin | 2023 |
| `slowend.png` | [Slow End](https://www.newgrounds.com/art/view/prisonercoin/slow-end) | PrisonerCoin | 2023 |

- Source collection/attribution: https://github.com/Person-008/KyleOS#license
- Full CC license: https://creativecommons.org/licenses/by-nc-sa/3.0/legalcode
- **Excluded:** the KyleOS `Survey` wallpaper, screenshot/thumbnail, and icons based on `Survey Complete`, because the source README identifies the original artwork as having no confirmed reuse license. We also exclude the other KyleOS preview images, wallpapers thumbnails, fonts, precompiled GTK themes, and massive icon directories to avoid mistakenly relicensing third-party materials.
- The website uses `frontier.png` in a labeled *concept* mockup and lists the required credits.

If you plan to distribute Kuhl OS commercially or without the NonCommercial/ShareAlike obligations, **remove the `assets/wallpapers/third-party/` files and replace their corresponding `wallpaper` values in `config/themes.json` with your own licensed images**. Merely removing credits is not sufficient. You can still use the MIT code.

## External software (installed via Fedora; not bundled)

- [Fedora Workstation](https://fedoraproject.org/workstation/), [Niri](https://github.com/niri-wm/niri), [Waybar](https://github.com/Alexays/Waybar), [Rofi](https://github.com/davatorium/rofi), [Kitty](https://sw.kovidgoyal.net/kitty/), [Mako](https://github.com/emersion/mako), [Fuzzel](https://codeberg.org/dnkl/fuzzel), [Vicinae](https://github.com/vicinaehq/vicinae), [Thunar](https://docs.xfce.org/xfce/thunar/start), [swaybg](https://github.com/swaywm/swaybg), and [swaylock](https://github.com/swaywm/swaylock).
- Each dependency retains its own upstream license. Vicinae is still optional and uses an independently operated third-party COPR if selected.
- Kuhl's one-line installer retrieves live source from `TerabyteEXE/Kuhl-OS` and runs package management commands. Inspect the source and supply chain before running it.
