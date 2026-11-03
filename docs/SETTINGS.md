# Desktop settings

`kuhl settings` opens the terminal UI. It connects to Fedora's network, sound, Bluetooth and display tools.

`kuhl bar scale 85|100|125|150` changes bar size; `kuhl bar position left|right|top|bottom` changes its position. The default layout is a vertical left sidebar.

`kuhl bar module MODULE on|off` toggles modules: brand, clock, cpu, music, workspaces, network, bluetooth, audio, battery, tray, settings, close.

`kuhl ui scale 110` changes terminal and other supported text size. `kuhl display wizard` configures monitor scaling separately.

`kuhl theme sevens|day|dusk` changes the color palette. `kuhl wallpaper set PATH` uses your own wallpaper.

Preferences are under `~/.local/state/kuhl/`. Existing user-edited dotfiles will be kept rather than silently overwritten. See docs/RECOVERY.md.
