# Upstream Gigi's Rice (new AmethystOS desktop base)

- Source: https://github.com/deadduck-09/gigis-rice — Gigi, MIT, copyright 2026. See `LICENSE.gigi` and `third_party/gigis-rice/LICENSE`.
- Config: Niri + Noctalia Shell v4.7.7 (archived upstream). Exact original Niri config is copied under `third_party/gigis-rice/niri` for comparison; the installed Fedora config is under `payload/niri`.
- Original Gigi colors adapted to Amethyst purple, original Amethyst wallpapers retained; no upstream anime wallpapers or preview videos redistributed.
- Separate Noctalia plugins retain their own manifest licenses and files. Do not assume the MIT license on Gigi's repository supersedes the individual dependencies or artwork licenses.
- Fedora boot/session and package installation remains owned by AmethystOS; Gigi's Arch-only installer is not used.
- See `docs/GIGI_MIGRATION.md` for compatibility requirements and exact alterations.
