# Updating your existing Kuhl website

Your GitHub Pages site `main.html` is not included in the release ZIP, since the existing site is already in your GitHub repository and should not be overwritten accidentally.

After copying the files into a clone of your existing repo, run:

```bash
python3 scripts/patch-site.py main.html
```

This optional site patch updates placeholder install instructions, including the Copy button if the expected HTML structure matches. It creates a backup and stops if the site has changed too much. The rest of the visual design stays intact.

If the site patch cannot identify the layout, manually edit these claims in your website:

- Four or fewer extensions → use two presets: Full (seven third-party extensions plus User Themes) and Balanced (five third-party extensions plus User Themes).
- Coming-soon installer → `git clone https://github.com/TerabyteEXE/Kuhl-OS.git && cd Kuhl-OS && bash install.sh --profile full` (written as separate shell commands in a code block).
- Ctrl+Space search → clarify it opens native GNOME Overview search, not the floating website demo launcher.
- The setup is a **Fedora Workstation customization script**, not a bootable ISO.

The project should not advertise a finished Fedora ISO until a separately tested bootable image exists.
