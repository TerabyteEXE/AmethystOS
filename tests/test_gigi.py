#!/usr/bin/env python3
"""Portable AmethystOS rebase integration checks (no OS changes)."""
import hashlib, json, os, pathlib, shutil, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import deploy

def check():
    P=ROOT/'payload'
    # Reset must not leave calls to deleted RC2 GTK appearance helper scripts.
    for name in ('install.sh', 'uninstall.sh'):
        installer=(ROOT/name).read_text()
        assert 'scripts/desktop_prefs.py' not in installer, name
        assert 'scripts/appearance.py' not in installer, name
    config=(P/'niri/config.kdl').read_text()
    assert 'include "./modules/keybinds.kdl"' in config
    assert 'include "./noctalia.kdl"' in config
    assert 'workspace "five"' in config
    assert '1366x768' not in (P/'niri/modules/output.kdl').read_text()
    kb=(P/'niri/modules/keybinds.kdl').read_text()
    for x in ('Super+W repeat=false { close-window; }', 'Super+Space', 'Ctrl+Super+K', 'Super+1', 'Super+5'):
        assert x in kb,x
    assert 'helium-browser' not in kb
    assert 'qs -c noctalia-shell' in kb
    assert 'spawn-sh-at-startup "command -v qs' in (P/'niri/modules/autostarts.kdl').read_text()
    assert not (P/'waybar').exists() and not (P/'fuzzel').exists() and not (P/'mako').exists()
    s=json.loads((P/'noctalia/settings.json').read_text())
    assert s['colorSchemes']['predefinedScheme']=='Amethyst'
    assert s['hooks']['wallpaperChange']==''
    assert s['appLauncher']['pinnedApps'][0]=='kitty'
    assert s['plugins']['autoUpdate'] is False
    assert '/home/gigi/' not in (P/'noctalia/settings.json').read_text()
    assert (P/'noctalia/plugins/keybind-cheatsheet/Main.qml').exists()
    assert (P/'noctalia/plugins/clipper/Main.qml').exists()
    assert (P/'noctalia/colorschemes/Amethyst/Amethyst.json').exists()
    assert (ROOT/'LICENSE.gigi').read_bytes()==(ROOT/'third_party/gigis-rice/LICENSE').read_bytes()
    assert len(list((P/'niri/modules').glob('*.kdl')))>=9
    for w in ('AmethystDark.png','AmethystLight.png'): assert (ROOT/'assets/wallpapers'/w).stat().st_size>100000
    for pkg in ('noctalia-legacy', 'AMETHYSTOS_ALLOW_TERRA', '--nogpgcheck'):
        assert pkg in (ROOT/'scripts/packages.sh').read_text()

    with tempfile.TemporaryDirectory() as temp:
        home=pathlib.Path(temp)/'home'; niri=home/'.config/niri'; niri.mkdir(parents=True)
        (niri/'config.kdl').write_text('user original niri\n')
        try: deploy.install(home,replace=False,dry_run=False,require_niri=False)
        except RuntimeError: pass
        else: raise AssertionError('Existing Niri config was overwritten without opt-in')
        assert (niri/'config.kdl').read_text()=='user original niri\n'
        deploy.install(home,replace=True,dry_run=True,require_niri=False)
        assert not (home/'.config/noctalia').exists()
        deploy.install(home,replace=True,dry_run=False,require_niri=False)
        assert (home/'.config/noctalia/plugins/keybind-cheatsheet/Main.qml').is_file()
        assert (home/'.local/bin/amethyst-keys').stat().st_mode & 0o111
        assert (home/'.config/niri/config.kdl').read_text()!='user original niri\n'
        # Repeat upgrade and verify original backup remains accessible
        deploy.install(home,replace=True,dry_run=False,require_niri=False)
        state=json.loads((home/'.local/state/amethystos-base-v1/state.json').read_text())
        rec=next(e for e in state['entries'] if e['path']=='.config/niri')
        assert rec['backup']
        # A changed file must NEVER be deleted by the uninstaller.
        file=home/'.config/niri/modules/keybinds.kdl';file.write_text(file.read_text()+'// personal change\n')
        try:deploy.restore(home,dry_run=False)
        except RuntimeError:pass
        else:raise AssertionError('Uninstall overwrote modified user configuration')
        file.write_text((P/'niri/modules/keybinds.kdl').read_text())
        deploy.restore(home,dry_run=False)
        assert (niri/'config.kdl').read_text()=='user original niri\n'
        assert not (home/'.config/noctalia').exists()
    print('[ok] Rebase configuration, installer backups, upgrade and restore')

def test_migration():
    # Simulate the previous RC2.10 managed Waybar paths and user's original bar.
    with tempfile.TemporaryDirectory() as temp:
        home=pathlib.Path(temp)/'home';state=home/'.local/state/amethystos-base-v1';state.mkdir(parents=True)
        bar=home/'.config/waybar';bar.mkdir(parents=True)
        (bar/'style.css').write_text('old amethyst bar')
        h=hashlib.sha256();h.update(b'style.css');h.update(b'old amethyst bar')
        backup=state/'backups/old/.config/waybar';backup.mkdir(parents=True)
        (backup/'style.css').write_text('my pre-amethyst bar')
        json.dump({'entries':[{'path':'.config/waybar','backup':str(backup.relative_to(home)),'sha256':h.hexdigest()}]},(state/'state.json').open('w'))
        deploy.install(home,replace=True,dry_run=False,require_niri=False)
        assert (bar/'style.css').read_text()=='my pre-amethyst bar'
        assert not any(e['path']=='.config/waybar' for e in json.loads((state/'state.json').read_text())['entries'])
        deploy.restore(home,dry_run=False)
        assert (bar/'style.css').read_text()=='my pre-amethyst bar'
    print('[ok] Old Waybar migrated without losing pre-Amethyst backup')

if __name__=='__main__':check();test_migration()
