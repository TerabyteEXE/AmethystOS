# AmethystOS v1 RC2.8 — Compact Home

This is a conservative UI-only follow-up to RC2.7 using the two supplied
Omarchy-style launcher screenshots as the design references.

- **Compact Home**: narrow, centered, simple dark panel with `Go...` input,
  icons, selected-row highlight, category titles and chevrons. Removed the
  large branding header, greeting, item subtitles and footer. Light theme
  has the same geometry with matching colors.
- **Apps view**: a wider single-column search/list like the second reference;
  other categories remain small, with an unobtrusive back control.
- **Keyboard fix**: Backspace and Delete edit text when the entry contains
  text. Backspace on an empty entry navigates back only from a nested section.
  Both the previous entry-level and parent-window keyboard hooks were
  handling Backspace; only the focused widget now handles keys. Arrow keys,
  Enter, Escape, Super+Space toggle, Super+D, typed search and mouse activation
  remain available.
- **No other desktop changes**: wallpapers, Niri, Waybar popups, installer,
  recovery, themes and package selections are not modified.

## Test notes

Run `bash tests/validate.sh`. The new headless regression tests cover menu
sections, filtering, and editing/back-navigation decisions. GTK and Niri live
interaction must still be tested on Fedora because the CI environment may
lack PyGObject and a running compositor.

Verify from the actual desktop: type several words into `Go...`, press
Backspace repeatedly, select and Delete text, type again, use Up/Down and
Enter to open Apps, use Backspace with an empty search to return Home, and
close/reopen using Super+Space.
