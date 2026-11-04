# Publishing the AmethystOS website

The site is ordinary static HTML/CSS/JS, served from the **root of the AmethystOS repository**. It needs no build system, package manager, CDN, or server.

1. Commit `index.html`, `install.html`, `wiki/`, `assets/`, and `scripts/build_site.py` on the `main` branch.
2. In the GitHub repository, open **Settings → Pages**.
3. Under **Build and deployment**, select **Deploy from a branch**.
4. Select `main`, folder `/ (root)`, then save.
5. Once deployed, navigate to `https://terabyteexe.github.io/AmethystOS/`.

All internal links are relative so the site works from a GitHub Pages project subdirectory.

## Keep the wiki accurate

Every active shortcut in `payload/niri/keybinds.kdl` appears on the generated `wiki/keybinds.html` page. The plain home page is generated from `site_templates/home.html`. After adding or changing bindings:

```bash
python3 scripts/build_site.py
bash tests/validate.sh
```

`--check` is used by CI to catch stale generated keybinding docs. The homepage, About page, installation guide, and other wiki pages are maintained directly as HTML, so your edits won't be overwritten; edit `scripts/build_site.py` to change the generated keybinding reference.

## Website philosophy

The v1 site uses a Debian-style, documentation-first layout with the rice's near-black background and muted cyan accents. Its CSS is original; Debian website code and imagery were not copied. There are no external fonts, JavaScript frameworks, stock mockups, tracking pixels, or fake desktop screenshots.
