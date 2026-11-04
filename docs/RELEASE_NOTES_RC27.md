# AmethystOS v1 RC2.7 — Amethyst Home beta

This release improves discoverability and consistency while preserving the
working Fedora/Niri setup, original top bar and both user-provided wallpapers.

## Changes

- Replaces the former flat GTK search with a **Home → category → action**
  flow. Sections: Apps, Learn, Style, Setup, Install, Remove, Update, About,
  System and Power. Up/Down/Enter/Right/Left/Backspace work alongside typed
  search, and navigation can also be done with the mouse.
- Super+Space and Super+D launch **the same Home interface**. Super+Space
  toggles it closed; Escape also closes. Fuzzel remains the fallback.
- Home window is a small floating Niri window using translucent, dark/light
  CSS; Niri 26.04 supports the per-window blur rule used here. This may need
  tuning for lower-performance graphics hardware.
- Calendar and other Waybar panels now share a slightly translucent style,
  display local date / user / service state where available, and offer quick
  settings actions. Different widget clicks switch between panels.
- The Light/Dark wallpapers, shell, installer, theme pipeline, package
  choices, configuration backups, and Settings UI remain in place.
- Rebuilds the site's generated keyboard reference for Super+D's new action.

## Technical limits

- Native GTK rendering, app activation, focus and layer-shell positioning
  **have not been verified in a live Fedora/Niri desktop here**. In particular
  review multimonitor layouts, current nondefault Waybar positions, GTK scaling
  and blurred-window behavior with an older GPU.
- These panels are separate client windows/layer surfaces, not true embedded
  Waybar widgets. GTK-layer-shell is an optional dependency; without it the
  controls open as floating windows.
- This calendar displays local dates, not events from cloud accounts.
- Links in Learn and About open project-owned public pages in the default
  browser. No search query is passed as a shell command.

## Suggested validation before upgrade/release

```bash
bash tests/validate.sh
bash install.sh --dry-run
niri validate
```

From the live Fedora Niri session: test opening Super+Space and Super+D,
Up/Down and Enter, typed search from Home and Apps, switching categories,
ESC and second Super+Space, clock/audio/network/Bluetooth/settings popups,
Light/Dark, multiple monitors and replacing configs with backups.
