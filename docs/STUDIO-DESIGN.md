# Kuhl OS Studio — visual and interaction specification

## Direction
A single rounded floating capsule centered along the top of the screen, low-contrast charcoal surfaces, gentle gold indicators, monospaced utility text, terminal windows with modest radii and 13px gaps. Inspired visually by supplied screenshots of a minimal Niri rice; all source code and CSS are independently authored. No unlicensed reference wallpaper or code is distributed.

| Token | Dusk | Day |
|---|---|---|
| Background | `#2c2c2c` | `#eae4d8` |
| Capsule | `#302e2c` | `#f3eee4` |
| Surface elevation | `#423d35` | `#e2d8c8` |
| Text | `#e9e2d5` | `#353631` |
| Accent | `#e4c977` | `#8b7950` |

There is deliberately no default generated wallpaper. In a polished release, an artist-made original Kuhl wallpaper can replace the solid background; until then the OS is fully usable.

## Main flows

- `Super + Space`: launcher (Vicinae if installed, Fuzzel otherwise)
- `Ctrl + Super + K`: searchable keyboard atlas (standalone floating Kitty window)
- `Super + D`: Kuhl control center (themes, wallpaper, diagnostics, apps, power)
- `Super + Shift + T`: theme selection
- `Super + Shift + P`: power/sleep/logout with explicit confirmation for reboot/poweroff
- `Super + H/J/K/L`: navigate, `Super + Shift + H/J/K/L`: move

## Performance rules
No wallpaper animation, compositing blur, giant icon packs beyond the selected theme, constant background scripts, live polling for updates or new WebKit/Electron UI. Rendering is performed by Niri, Waybar, Kitty, Mako, and Fuzzel. Python only runs when using the control center/guide or during setup.

## Adding wallpapers later

```bash
kuhl wallpaper set ~/Pictures/kuhl-dusk-original.png
kuhl wallpaper reset
```

The original Kuhl images remain optional for compatibility and are **not** part of the new design reference.
