#!/usr/bin/env python3
"""Generate the keybinding reference from the Niri config.
Other HTML pages are maintained directly and are not overwritten by this tool.
Run: python3 scripts/build_site.py (or --check to detect a stale keybinding page).
No external packages or internet access are required.
"""
from __future__ import annotations
import argparse
import html
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GITHUB='https://github.com/TerabyteEXE/AmethystOS'
INSTALL='curl -fsSL https://raw.githubusercontent.com/TerabyteEXE/AmethystOS/main/bootstrap.sh | bash'
UPSTREAM='https://github.com/youngcoder45/New-Niri-minimal-dots'

def escape(x): return html.escape(x,quote=True)

def nav(rel,active):
    menu=[('Home',rel+'index.html','home'),('Install',rel+'install.html','install'),('Documentation',rel+'wiki/index.html','wiki'),('Keybindings',rel+'wiki/keybinds.html','keys')]
    links=''.join(f'<a href="{u}"'+(' aria-current="page"' if id==active else '')+f'>{t}</a>' for t,u,id in menu)
    return f'''<header class="topbar"><div class="wrap nav-inner">
<a href="{rel}index.html" class="brand" aria-label="AmethystOS home"><img class="brand-icon" src="{rel}assets/branding/amethyst-logo.png" alt="" width="36" height="36">AmethystOS</a>
<button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="site-nav">Menu</button>
<nav id="site-nav" class="navlinks" data-navlinks aria-label="Main navigation">{links}<a class="nav-github" href="{GITHUB}" target="_blank" rel="noopener noreferrer">GitHub ↗</a></nav>
</div></header>'''

def page(title,description,rel,active,body):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0c1014"><meta name="description" content="{escape(description)}">
<title>{escape(title)} — AmethystOS</title><link rel="icon" href="{rel}assets/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{rel}assets/apple-touch-icon.png">
<link rel="stylesheet" href="{rel}assets/site.css"><script src="{rel}assets/site.js" defer></script></head>
<body><a class="skip-link" href="#content">Skip to content</a>
{nav(rel,active)}<main id="content">{body}</main>
<footer class="footer"><div class="wrap footer-inner"><div>
<p><strong>AmethystOS</strong> · An independent Fedora + Niri desktop project. Not affiliated with Fedora, Niri, or Omarchy.</p>
<p>Adapted from <a href="{UPSTREAM}">New Niri Minimal Dots</a> (MIT). AI-assisted, experimental, and not independently security-audited. Review the source before installation.</p></div>
<div class="footer-links"><a href="{rel}wiki/index.html">Documentation</a><a href="{rel}wiki/troubleshooting.html">Support</a><a href="{GITHUB}">Source code</a></div>
</div></footer></body></html>'''

def code_block(content,id,title='Terminal'):
    return f'''<div class="code-box"><div class="code-head"><span>{escape(title)}</span><button type="button" class="copy-btn" data-copy="{escape(id)}" aria-label="Copy command">Copy</button></div><pre id="{escape(id)}"><code>{escape(content)}</code></pre></div>'''

def linkpanel(text, desc, url):
    return f'<a class="link-panel" href="{url}"><div><h3>{text}</h3><p>{desc}</p></div><span class="arr" aria-hidden="true">↗</span></a>'

def sidebar(active):
    items=[('Start here','index.html','home'),('Installation','../install.html','install'),('Keybindings','keybinds.html','keys'),('Customization','customization.html','custom'),('Troubleshooting','troubleshooting.html','trouble')]
    return '<aside class="side-nav" aria-label="Wiki pages"><p class="side-label">Documentation</p>'+''.join(f'<a class="'+('active' if ident==active else '')+f'" href="{u}">{t}</a>' for t,u,ident in items)+'</aside>'

def doc_page(title,sub,active,body):
    return page(title,sub,'../','keys' if active=='keys' else 'wiki',f'''<div class="wrap"><div class="page-title"><p class="eyebrow">AmethystOS / Documentation</p><h1>{escape(title)}</h1><p class="lead">{escape(sub)}</p></div>
<div class="doc-shell">{sidebar(active)}<article class="doc-content">{body}</article></div></div>''')

# Website pages are hand-maintained. The old landing page template is archival only.
# Deprecated home template is preserved as site_templates/home.legacy.html.
home=''  # The homepage is now directly maintained in index.html.

install_body=f'''<div class="wrap"><div class="page-title"><p class="eyebrow">AmethystOS / Setup</p><h1>Install AmethystOS.</h1><p class="lead">Start with Fedora Workstation. Add AmethystOS as a separate Niri session. Keep GNOME available if you need it.</p></div><div class="doc-shell">
<aside class="side-nav"><p class="side-label">On this page</p><a href="#requirements">Requirements</a><a href="#command">One-command setup</a><a href="#manual">Manual install</a><a href="#after">After installation</a><a href="#restore">Restore or remove</a><a href="wiki/index.html">Open wiki ↗</a></aside>
<article class="doc-content"><h2 id="requirements">Before you start</h2><ul>
<li><strong>Fedora Workstation</strong>, an internet connection, sudo privileges, and enough storage for the Niri desktop packages. The installer checks that at least 1 GiB is free on <span class="inline-code">/</span> before installing.</li>
<li><strong>Use a normal user account.</strong> The installer requests sudo only when installing packages. Do not launch it as root.</li>
<li><strong>Make a backup.</strong> Existing dotfiles prompt before replacement and are backed up, but you should keep your own backup of important data.</li>
<li><strong>This isn't a new operating-system image.</strong> Install Fedora normally first; AmethystOS adds a session rather than replacing your OS.</li></ul>
<h2 id="command">One-command setup</h2><p>On Fedora, open Terminal and paste the command below. It fetches the repository's current <span class="inline-code">main</span> branch, so read the <a href="{GITHUB}/blob/main/bootstrap.sh">bootstrap script</a> first.</p>
{code_block(INSTALL,'install-command','Fedora Terminal')}
<div class="note"><strong>Security:</strong> This command executes remotely downloaded code. It isn't pinned to a release commit. Review the source, and use the manual method below if you prefer inspecting files first.</div>
<div class="steps"><div class="step"><span class="no">1</span><div><h3>Check the environment</h3><p>The installer checks Fedora, permissions, disk space and repository files.</p></div></div><div class="step"><span class="no">2</span><div><h3>Install the desktop</h3><p>DNF installs Niri, Waybar, Fuzzel, notifications and supporting packages. Optional apps such as Starship don't block setup when unavailable.</p></div></div><div class="step"><span class="no">3</span><div><h3>Configure safely</h3><p>When existing dotfiles are found, choose whether to replace them after creating a recoverable backup.</p></div></div><div class="step"><span class="no">4</span><div><h3>Finish and log in</h3><p>The installer validates the Niri configuration before deploying it. Log out, choose Niri at your login screen and sign back in.</p></div></div></div>
<h2 id="manual">Manual installation</h2><p>To inspect the project before running any code:</p>
{code_block('git clone https://github.com/TerabyteEXE/AmethystOS.git\ncd AmethystOS\nless bootstrap.sh\nless install.sh\nbash install.sh --dry-run\nbash install.sh','manual-command','Fedora Terminal')}
<p>Local testing can be run with <span class="inline-code">bash tests/validate.sh</span>. The included native Niri parser runs only where Niri is installed.</p>
<h2 id="after">After installation</h2><ul><li>At login, select <strong>Niri</strong> using the session selector (often a gear icon).</li><li>Press <span class="inline-code">Super + Enter</span> to open the terminal or <span class="inline-code">Super + Space</span> for the launcher.</li><li>Press <span class="inline-code">Super + Shift + /</span> to display Niri's built-in hotkey overlay.</li><li>For all configured shortcuts, open the <a href="wiki/keybinds.html">keybinding reference</a>.</li></ul>
<h2 id="restore">Backups and recovery</h2><p>AmethystOS stores backup state at <span class="inline-code">~/.local/state/amethystos-base-v1/</span>. If you need your previous desktop settings, use the repository's restore script:</p>
{code_block('cd AmethystOS\nbash uninstall.sh','restore-command','From a local repository checkout')}
<p>Run the clone command from the manual installation section first if you installed remotely and no longer have the repository directory. The restore script avoids deleting configs that you've modified since installation. It does not uninstall Fedora packages or remove GNOME.</p>
<div class="note">Having trouble? Start with the <a href="wiki/troubleshooting.html">troubleshooting guide</a>. Never delete <span class="inline-code">~/.config/niri</span> without checking backups.</div>
</article></div></div>'''

wiki_home=f'''<h2>Welcome to the wiki</h2>
<p>The basics of the AmethystOS desktop, from first login to customizing the Niri configuration. This site documents the actual v1 base instead of features planned for future releases.</p>
<div class="doc-card-grid">
<a class="doc-card" href="../install.html"><h3>Installation ↗</h3><p>System requirements, one command, manual setup and recovery.</p></a>
<a class="doc-card" href="keybinds.html"><h3>Keybindings ↗</h3><p>Search every active shortcut in the shipped Niri configuration.</p></a>
<a class="doc-card" href="customization.html"><h3>Customization ↗</h3><p>Wallpaper, Waybar, launcher, and Niri's configuration files.</p></a>
<a class="doc-card" href="troubleshooting.html"><h3>Troubleshooting ↗</h3><p>Solutions for installation, black screens, and broken desktop components.</p></a>
</div>
<h2>Get started in a minute</h2><p>After logging into the Niri session, these shortcuts will get you moving:</p>
<table class="key-table"><tbody>
<tr><td><span class="kbd">Super + Enter</span></td><td>Open Alacritty terminal</td></tr>
<tr><td><span class="kbd">Super + Space</span></td><td>Open Fuzzel application launcher</td></tr>
<tr><td><span class="kbd">Super + Q</span></td><td>Close the focused window</td></tr>
<tr><td><span class="kbd">Super + H / L</span></td><td>Move between columns</td></tr>
<tr><td><span class="kbd">Super + O</span></td><td>Show workspace overview</td></tr>
<tr><td><span class="kbd">Super + Shift + /</span></td><td>Open built-in hotkey overlay</td></tr>
</tbody></table>
<h2>What AmethystOS installs</h2>
<p>Niri handles the window layout. Waybar displays desktop status. Fuzzel launches apps, Mako handles notifications, swaybg displays wallpapers, and Alacritty is the default terminal.</p>
<p>Fedora keeps managing packages, user accounts, hardware, and updates. AmethystOS does not replace Fedora's system services or default login manager.</p>
<h2>Project transparency</h2>
<p>The desktop files were adapted from <a href="{UPSTREAM}">New Niri Minimal Dots by Aditya Verma</a> under MIT, with the original notice in <span class="inline-code">LICENSE.upstream</span>. Fedora-specific changes are described in <span class="inline-code">docs/UPSTREAM.md</span>.</p>
<p>The installer and documentation were created with AI assistance. They have not received an independent security audit. Use them with the same care you would use any third-party Linux setup script.</p>'''

custom=f'''<h2>Where the configuration lives</h2>
<p>The install places Niri and application configuration in your home directory. Niri uses the KDL format and can reload changes to its configuration. <a href="https://niri-wm.github.io/niri/Configuration%3A-Introduction.html">Official Niri documentation ↗</a></p>
<table class="key-table"><tbody>
<tr><td><span class="inline-code">~/.config/niri/</span></td><td>Layouts, keybindings, window rules and session startup</td></tr>
<tr><td><span class="inline-code">~/.config/waybar/</span></td><td>Panel modules and CSS styling</td></tr>
<tr><td><span class="inline-code">~/.config/fuzzel/</span></td><td>Application launcher appearance</td></tr>
<tr><td><span class="inline-code">~/.config/mako/</span></td><td>Notification settings</td></tr>
<tr><td><span class="inline-code">~/.config/alacritty/</span></td><td>Default terminal theme</td></tr>
</tbody></table>
<h2>Changing keybindings</h2><p>Edit <span class="inline-code">~/.config/niri/keybinds.kdl</span>. The site's <a href="keybinds.html">reference</a> is generated from the repository's default file, not your personal edits.</p>
{code_block('niri validate','niri-validate','In a Niri installation')}
<p>Run the validator after changes; it reports invalid syntax and configuration errors.</p>
<h2>Wallpaper</h2><p>AmethystOS includes an original minimal wallpaper, <strong>Amethyst Still</strong>. The installer only copies it for fresh installations that have no existing images in <span class="inline-code">~/Pictures/wallpapers/</span>; your own wallpapers take precedence.</p>
<p>Open the wallpaper picker in a terminal:</p>{code_block('~/.local/bin/set-wallpaper','wallpaper-picker','Niri Terminal')}
<p>Or copy your own JPEG, PNG or WebP files into <span class="inline-code">~/Pictures/wallpapers/</span> and use the same picker.</p>
<h2>Adjusting the bar</h2><p>Edit <span class="inline-code">~/.config/waybar/style.css</span> for colors and font sizes. The module configuration is in <span class="inline-code">~/.config/waybar/config.jsonc</span> and related <span class="inline-code">modules/</span> files. Restart Waybar after editing:</p>
{code_block('pkill -x waybar\nwaybar >/dev/null 2>&1 &','waybar-restart','Niri Terminal')}
<div class="note"><strong>Tip:</strong> Keep a backup of your modified config. Re-running the installer may ask whether to replace it with the repository defaults.</div>'''

trouble=f'''<h2>Start with these checks</h2><p>If something doesn't work, start by checking the Niri configuration and your session logs. If the graphical session is unusable, log out and choose GNOME at the login screen.</p>
{code_block('niri validate\njournalctl --user -b -p warning --no-pager | tail -n 80','diagnostics','Fedora Terminal')}
<h2>DNF says “No match for argument: starship”</h2><p>This was an early installer error. The current base keeps Starship optional. If you see it stop the installation, make sure you've downloaded the newest repository version. You do not need Starship to run Niri.</p>
<h2>Niri doesn't appear at login</h2><p>Check that Fedora's Niri package is installed and that the installer completed the package stage. Log out completely and look for the session selection control in your login manager. AmethystOS does not change the default GNOME session for you.</p>
<h2>Black screen or frozen desktop</h2><p>Use a text console with <span class="inline-code">Ctrl + Alt + F3</span> if one is available, or return to GNOME. Older GPUs and virtual-machine graphics acceleration can affect Wayland sessions. Try Niri on supported hardware and inspect your session logs; do not delete desktop configurations blindly.</p>
<h2>Waybar or launcher is missing</h2><p>Start the component from a terminal to read errors:</p>
{code_block('waybar\nfuzzel','bar-troubleshoot','Run individually for diagnostic output')}
<p>Waybar and Fuzzel need a running Wayland session; they won't work from an ordinary GNOME terminal in the same way as when launched under Niri.</p>
<h2>I want my old dotfiles back</h2><p>From a local copy of the AmethystOS repository, use <span class="inline-code">bash uninstall.sh</span> to restore files tracked by the installer, as long as they haven't been modified since deployment. Installed packages remain.</p>
<h2>About security</h2><p>The installer obtains source code from GitHub over HTTPS and executes it. The one-command shortcut follows the current main branch, not a fixed checksum. Inspect <a href="{GITHUB}/blob/main/bootstrap.sh">bootstrap.sh</a>, <a href="{GITHUB}/blob/main/install.sh">install.sh</a>, and the files under <span class="inline-code">scripts/</span> before installing, especially on a primary machine.</p>
<p>AmethystOS is AI-assisted and not independently security audited. Keep backups and test before deployment. See <a href="{GITHUB}/blob/main/docs/SECURITY.md">SECURITY.md</a> for the maintained security notes.</p>
<h2>Upstream and licensing</h2><p>Source rice: <a href="{UPSTREAM}">New Niri Minimal Dots</a> by Aditya Verma (MIT). The code license does not automatically grant rights to every artwork found in an upstream repository; AmethystOS does not distribute upstream wallpapers of unverified origin.</p>
'''

# Parse the actual, non-commented single-line bindings shipped by AmethystOS.
# Multiline key actions are not currently present in the default config.
pat=re.compile(r'^\s*([A-Za-z0-9_+]+)\s+[^{}]*\{\s*([^{}]+?)\s*\}\s*$')

def keys():
    bindings=[]
    for lineno,raw in enumerate((ROOT/'payload/niri/keybinds.kdl').read_text().splitlines(),1):
        if raw.lstrip().startswith('//'): continue
        m=pat.match(raw)
        if m:
            combo,action=m.groups()
            # comments and lines that are not keybindings cannot pass the regex.
            if combo in ('binds',): continue
            bindings.append((combo,action.strip().rstrip(';'),lineno))
    return bindings

def describe(action,combo):
    defaults={
        'show-hotkey-overlay':'Show the built-in shortcut overlay',
        'toggle-overview':'Toggle workspace overview',
        'close-window':'Close the focused window',
        'focus-column-left':'Focus the column on the left',
        'focus-column-right':'Focus the column on the right',
        'focus-window-up':'Focus the window above',
        'focus-window-down':'Focus the window below',
        'focus-workspace-up':'Go to previous workspace',
        'focus-workspace-down':'Go to next workspace',
        'move-column-left':'Move column left',
        'move-column-right':'Move column right',
        'move-window-up':'Move window up',
        'move-window-down':'Move window down',
        'focus-column-first':'Focus first column',
        'focus-column-last':'Focus last column',
        'move-column-to-first':'Move column to first position',
        'move-column-to-last':'Move column to last position',
        'focus-monitor-left':'Focus monitor to left',
        'focus-monitor-right':'Focus monitor to right',
        'focus-monitor-up':'Focus monitor above',
        'focus-monitor-down':'Focus monitor below',
        'move-column-to-monitor-left':'Move column to left monitor',
        'move-column-to-monitor-right':'Move column to right monitor',
        'move-column-to-monitor-up':'Move column to monitor above',
        'move-column-to-monitor-down':'Move column to monitor below',
        'move-column-to-workspace-up':'Move column to previous workspace',
        'move-column-to-workspace-down':'Move column to next workspace',
        'move-workspace-up':'Move workspace up',
        'move-workspace-down':'Move workspace down',
        'consume-or-expel-window-left':'Take or release window on the left',
        'consume-or-expel-window-right':'Take or release window on the right',
        'consume-window-into-column':'Add window to this column',
        'expel-window-from-column':'Remove window from this column',
        'switch-preset-column-width':'Cycle column widths',
        'switch-preset-window-height':'Cycle window heights',
        'reset-window-height':'Reset window height',
        'maximize-column':'Maximize the column',
        'fullscreen-window':'Toggle fullscreen window',
        'expand-column-to-available-width':'Expand column into remaining width',
        'center-visible-columns':'Center visible columns',
        'toggle-window-floating':'Float / tile focused window',
        'switch-focus-between-floating-and-tiling':'Switch between floating and tiled windows',
        'toggle-column-tabbed-display':'Toggle tabbed column layout',
        'screenshot':'Select screenshot region',
        'screenshot-screen':'Screenshot all screens',
        'screenshot-window':'Screenshot focused window',
        'toggle-keyboard-shortcuts-inhibit':'Toggle keyboard shortcut capture',
        'quit':'Exit Niri (confirmation)',
        'power-off-monitors':'Turn off displays',
    }
    main=action.split(' ',1)[0]
    if main in defaults: return defaults[main]
    for start,template in [('focus-workspace','Go to workspace {}'),('move-column-to-workspace','Move column to workspace {}')]:
        if action.startswith(start+' '): return template.format(action.split(' ',1)[1])
    if main=='set-column-width':return ('Reduce' if '-' in action else 'Increase')+' column width by 10%'
    if main=='set-window-height':return ('Reduce' if '-' in action else 'Increase')+' window height by 10%'
    if main.startswith('spawn'):
        if 'alacritty' in action:return 'Open Alacritty terminal'
        if 'fuzzel' in action:return 'Open application search (Fuzzel)'
        if 'nautilus' in action:return 'Open file manager'
        if 'amethyst-browser' in action or 'firefox' in action:return 'Open selected browser'
        if 'kitty' in action:return 'Open Kitty terminal'
        if 'amethyst-settings' in action:return 'Open Amethyst Settings'
        if 'set-wallpaper' in action:return 'Choose a wallpaper'
        if 'powermenu' in action:return 'Open power menu'
        if 'orca' in action:return 'Toggle screen reader'
        if 'wpctl set-volume' in action:return 'Raise volume' if '0.1+' in action else 'Lower volume'
        if 'wpctl set-mute' in action:return 'Mute/unmute microphone' if 'SOURCE' in action else 'Mute/unmute audio'
        if 'playerctl play-pause' in action:return 'Play / pause media'
        if 'playerctl stop' in action:return 'Stop media'
        if 'playerctl previous' in action:return 'Previous track'
        if 'playerctl next' in action:return 'Next track'
        if 'brightnessctl' in action:return 'Increase brightness' if '+10%' in action else 'Decrease brightness'
        return 'Run '+action
    return action.replace('-',' ').capitalize()

def category(action,combo):
    if combo.startswith(('XF86Audio','XF86Mon')):return 'Media & hardware'
    if action.startswith(('spawn','spawn-sh')):
        return 'Media & hardware' if ('wpctl' in action or 'playerctl' in action or 'brightnessctl' in action) else ('System' if 'powermenu' in action or 'orca' in action else 'Applications')
    if action.startswith(('screenshot',)) or action.startswith(('quit','power-off-monitors','toggle-keyboard-shortcuts-inhibit','show-hotkey-overlay')):return 'System'
    if action.startswith(('focus','toggle-overview')):return 'Navigation'
    if 'workspace' in action:return 'Workspaces'
    return 'Windows & layout'

def display_key(k):
    parts=k.split('+'); mapping={'Mod':'Super','Return':'Enter','Slash':'/','BracketLeft':'[','BracketRight':']','Comma':',','Period':'.','Minus':'-','Equal':'=','Page_Down':'Page Down','Page_Up':'Page Up','Ctrl':'Ctrl','XF86AudioRaiseVolume':'Volume Up','XF86AudioLowerVolume':'Volume Down','XF86AudioMute':'Audio Mute','XF86AudioMicMute':'Mic Mute','XF86AudioPlay':'Play/Pause','XF86AudioStop':'Stop','XF86AudioPrev':'Previous Track','XF86AudioNext':'Next Track','XF86MonBrightnessUp':'Brightness Up','XF86MonBrightnessDown':'Brightness Down','Print':'Print Screen'}
    return ' + '.join(mapping.get(x,x) for x in parts)

def generate_keys():
    bindings=keys(); assert len(bindings)>70, 'Keybindings parse unexpectedly incomplete'
    sections=['Applications','Navigation','Workspaces','Windows & layout','Media & hardware','System']
    grouped={x:[] for x in sections}
    for combo,action,line in bindings:
        c=category(action,combo)
        grouped[c].append((combo,action,line))
    full=''
    for c,items in grouped.items():
        if not items:continue
        rows=''.join('<tr data-key-row data-category="'+escape(c)+'"><td><span class="kbd">'+escape(display_key(k))+'</span></td><td>'+escape(describe(action,k))+'</td></tr>' for k,action,_ in items)
        full+=f'<section class="key-group" data-key-group><h2>{escape(c)} <span style="font-size:12px;color:var(--soft);font-weight:400">/ {len(items)}</span></h2><table class="key-table"><tbody>{rows}</tbody></table></section>'
    buttons='<button class="filter-btn" type="button" data-filter="all" aria-pressed="true">All</button>'+''.join('<button class="filter-btn" type="button" data-filter="'+escape(c)+'" aria-pressed="false">'+escape(c)+'</button>' for c in grouped)
    body=f'''<p>This reference contains every active single-line shortcut defined in <span class="inline-code">payload/niri/keybinds.kdl</span> for this release. Press <span class="kbd">/</span> to search. <strong>Super</strong> is Niri's normal Mod key on a regular session.</p>
<input class="key-search" type="search" placeholder="Search keys or actions (e.g. screenshot, workspace...)" aria-label="Search keyboard shortcuts" data-key-search>
<div class="key-controls" aria-label="Filter keybindings">{buttons}</div>
<p class="result-count" data-result-count>{len(bindings)} shortcuts</p>
{full}<div class="no-results" data-no-results>No shortcuts matched. Try another search term.</div>
<div class="note"><strong>Source of truth:</strong> The bindings above were generated from the included <span class="inline-code">payload/niri/keybinds.kdl</span>. Your own local changes won't be reflected until this documentation is regenerated. Use <span class="kbd">Super + Shift + /</span> for Niri's in-session hotkey overlay.</div>'''
    return doc_page('Keybindings','Search the shortcuts that actually ship with AmethystOS.', 'keys', body)

# Hand-edited pages (including About) are the source of truth. Rebuilding docs
# must never discard the maintainer's website edits. Only this page is generated.
files={
 'wiki/keybinds.html':generate_keys(),
}

p=argparse.ArgumentParser()
p.add_argument('--check',action='store_true',help='Check keybinding reference matches the Niri source without modifying files')
args=p.parse_args()
for rel,content in files.items():
    destination=ROOT/rel
    if args.check:
        if not destination.exists() or destination.read_text()!=content:
            raise SystemExit(f'Website file missing or stale: {rel}; run python3 scripts/build_site.py')
    else:
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text(content)
print(f'Keybinding reference OK: {len(keys())} Niri shortcuts')
