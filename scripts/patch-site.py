#!/usr/bin/env python3
"""Apply a tightly scoped copy/installer update to the existing Kuhl main.html.

Keeps website layout/CSS/JavaScript intact. Must be run locally and committed.
"""
import sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else 'main.html')
if not path.exists():
    sys.exit(f'Missing {path}. Keep the original website file and run from the repo root.')
src = path.read_text(encoding='utf-8')
if 'kuhl.example/install.sh' not in src:
    sys.exit('Installer placeholder not found. This site may already be updated; no changes made.')

replacements = {
    'Four or fewer.': 'Full or balanced. Pick the extensions your PC needs.',
    "The planned setup trims optional apps without removing Fedora’s essential tools.":
        "The current setup adds only a few theme packages and leaves Fedora’s default apps alone.",
    'Extensions are what breaks when GNOME updates, so the list stays short.':
        'Full uses seven compatible add-ons; Balanced uses five. Kuhl skips extensions that do not support your GNOME version.',
    'Ctrl+Space opens one search box for apps, files and settings.':
        'Ctrl+Space opens GNOME Overview search for apps, settings and supported files. The floating box below is a design preview.',
    'When the Kuhl setup script is released, follow its instructions to apply the theme, launcher and lean app defaults.':
        'Run the installer below to apply Kuhl wallpapers, Day/Dusk themes, icons and GNOME search. No core Fedora applications are removed.',
    'Kuhl’s setup script and app-removal steps are still planned, not available yet. The command shown is only an example — do not run it.':
        'Kuhl v0.2 is a Fedora desktop customization script, not an independent ISO. Install from the GitHub repository and review the code first.',
    'aria-label="Future installation terminal example"':
        'aria-label="Kuhl OS installation instructions"',
    '<span>● preview</span>': '<span>● v0.2</span>',
    '''<span class="comment"># The installation script is coming soon.</span>
 <span class="comment"># Example only — do not run this command:</span>
 <span class="prompt">$</span> curl -fsSL kuhl.example/install.sh | bash
 <span class="comment"># Check back for the official release. ✳</span>''':
        '''<span class="comment"># Start with Fedora Workstation 44 (GNOME).</span>
 <span class="prompt">$</span> sudo dnf install -y git
 <span class="prompt">$</span> git clone https://github.com/TerabyteEXE/Kuhl-OS.git
 <span class="prompt">$</span> cd Kuhl-OS
 <span class="prompt">$</span> bash install.sh --theme dusk --profile full''',
    '<span>Not published yet · demo only</span><button type="button" id="copy-example">Copy example</button>':
        '<span>Available on GitHub · review before running</span><button type="button" id="copy-example">Copy commands</button>',
    "const sample = '# Example only — not a published installer:\\n# curl -fsSL kuhl.example/install.sh | bash';":
        "const sample = 'sudo dnf install -y git\\ngit clone https://github.com/TerabyteEXE/Kuhl-OS.git\\ncd Kuhl-OS\\nbash install.sh --theme dusk --profile full';",
    "announce('Example copied. This is not a working installer.');":
        "announce('Kuhl install commands copied.');",
    "'Example copied. This is not a working installer.' : 'Clipboard unavailable. Select the example in the terminal.'":
        "'Kuhl install commands copied.' : 'Clipboard unavailable. Select the commands in the terminal.'",
}

# Validate ALL expected patterns before writing a single byte.
missing = [key[:90] for key in replacements if key not in src]
if missing:
    sys.exit('Website changed; patch aborted without edits. Missing:\n' + '\n'.join(missing))
for before, after in replacements.items():
    src = src.replace(before, after)
backup = path.with_name(path.name + '.pre-kuhl.bak')
if backup.exists():
    sys.exit(f'Backup already exists at {backup}; move it aside first. No changes made.')
backup.write_bytes(path.read_bytes())
path.write_text(src, encoding='utf-8')
print(f'Updated {path} without changing page layout. Original backed up: {backup}')
