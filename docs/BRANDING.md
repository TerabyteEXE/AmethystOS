# AmethystOS logo and branding

The project uses the original geometric purple amethyst crystal image supplied by the AmethystOS creator.

- `assets/branding/amethyst-logo-original.png`: unmodified uploaded image (white/lavender background).
- `assets/branding/amethyst-logo.png`: transparent-background crop of the **same artwork** for dark websites and READMEs. The crystal facets and colors are retained.
- `assets/favicon.png`: small raster favicon derived from the supplied image.
- `assets/apple-touch-icon.png`: small browser/home-screen icon derived from the supplied image.

The website references this logo from `scripts/build_site.py` and `site_templates/home.html`; do not edit the generated HTML directly. The repository's MIT license covers the software where applicable; do not assume original brand artwork is MIT-licensed without separate permission from the artwork owner.

To regenerate the site: `python3 scripts/build_site.py`.
