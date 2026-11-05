# AmethystOS branding and cat (Noctalia v5)

- Bar center: official `noctalia/bongocat:cat` widget, enabled in config.toml.
- The plugin is fetched from Noctalia's official source when online. It is not
  bundled as untrusted precompiled code; input-reactive mode can require evtest
  and input permissions. Other animation modes are available in plugin settings.
- The control-center and launcher bar icons use the project Amethyst logo.
- `amethyst-settings.desktop` already uses `Icon=amethystos` with the bundled icon.
- The owl/Noctalia branding *inside the upstream Noctalia Settings window* is
  part of upstream UI, not overridden by a supported branding configuration.
  Replacing it would require maintaining a Noctalia fork; we deliberately do
  not patch vendor code in a stable installer.
- Users with Noctalia GUI overrides in `~/.local/state/noctalia/settings.toml`
  may need to remove the conflicting widget/bar keys there or use the Settings
  UI. Keep a backup; do not blindly delete unrelated personalized settings.
