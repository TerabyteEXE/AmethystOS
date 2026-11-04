# AmethystOS logo and branding

The project uses the original geometric purple amethyst crystal image supplied by the AmethystOS creator.

- `assets/branding/amethyst-logo-original.png`: unmodified uploaded image (white/lavender background).
- `assets/branding/amethyst-logo.png`: transparent-background crop of the **same artwork** for dark websites and READMEs. The crystal facets and colors are retained.
- `assets/favicon.png`: small raster favicon derived from the supplied image.
- `assets/apple-touch-icon.png`: small browser/home-screen icon derived from the supplied image.

The static website HTML references this logo directly; the generated keybinding reference also references it through `scripts/build_site.py`. The repository's MIT license covers the software where applicable; do not assume original brand artwork is MIT-licensed without separate permission from the artwork owner.

To regenerate the site: `python3 scripts/build_site.py`.
