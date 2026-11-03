# The Kuhl keyboard workflow

Niri uses **scrollable tiling**: a new app occupies a column, and columns scroll horizontally instead of shrinking endlessly. Hold **Super** (Windows key on most PC keyboards).

| Shortcut | Action |
|---|---|
| Super + Space | Search. Vicinae if opted in; Fuzzel otherwise |
| Super + Enter or T | Open Kitty terminal |
| Super + E | Open Thunar file manager |
| Super + H / L | Focus left / right column |
| Super + J / K | Focus lower / upper window |
| Super + Ctrl + H / L | Move active column left / right |
| Super + Ctrl + J / K | Move active window down / up |
| Super + R | Cycle column width |
| Super + Shift + R | Cycle window height |
| Super + F | Maximize column |
| Super + Shift + F | Fullscreen window |
| Super + V | Toggle floating window |
| Super + 1–5 | Focus workspace 1–5 |
| Super + Shift + 1–5 | Move column to workspace |
| Super + Shift + Q | Close window |
| Super + Shift + L | Lock |
| Super + Shift + E | Quit Niri, with confirmation |
| Super + Shift + / | Niri shortcut overlay |
| Print | Screenshot |

Quick tip: `kuhl theme day` or `kuhl theme dusk` from Kitty changes Kuhl-managed colors. You can edit `~/.config/niri/config.kdl` to personalize shortcuts; Kuhl will detect your edit and preserve the file on subsequent installations.
