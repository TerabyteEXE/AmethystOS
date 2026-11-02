#!/usr/bin/env python3
"""Install curated compatible GNOME Shell extensions from extensions.gnome.org.

This installer queries the official GNOME extension API. It never patches GNOME
compatibility metadata or installs unsupported versions. It tracks extensions
it installed and leaves preexisting user-managed extensions alone.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

HOST = 'extensions.gnome.org'
ROOT = Path(__file__).resolve().parent.parent
MAX_EXTENSIONS = 20
MAX_DOWNLOAD = 15 * 1024 * 1024


def log(message: str) -> None:
    print(f'[kuhl/extensions] {message}', flush=True)


def shell_version() -> str:
    result = subprocess.run(['gnome-shell', '--version'], text=True,
                            capture_output=True, check=True)
    match = re.search(r'(\d+)(?:\.\d+)?\s*$', result.stdout.strip())
    if not match:
        raise RuntimeError(f'Cannot parse GNOME Shell version: {result.stdout.strip()}')
    return match.group(1)


def read_manifest(path: Path) -> list[tuple[str, str, str]]:
    items = []
    for line_no, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) != 3:
            raise ValueError(f'{path}:{line_no}: expected name, UUID, URL separated by tabs')
        name, uuid, url = [part.strip() for part in parts]
        if not name or not re.fullmatch(r'[\w.-]+@[\w.-]+', uuid):
            raise ValueError(f'{path}:{line_no}: invalid name or UUID')
        parsed = urllib.parse.urlparse(url)
        if (parsed.scheme, parsed.hostname) != ('https', HOST) or parsed.username or parsed.password:
            raise ValueError(f'{path}:{line_no}: URL must use the official GNOME Extensions site')
        if not re.fullmatch(r'/extension/\d+/[\w-]+/?', parsed.path) or parsed.query or parsed.fragment:
            raise ValueError(f'{path}:{line_no}: invalid extension details URL')
        items.append((name, uuid, url))
    return items


def profile_items(profile: str, config_dir: Path) -> list[tuple[str, str, str]]:
    items = read_manifest(config_dir / 'extensions.tsv')
    if profile == 'full':
        items.extend(read_manifest(config_dir / 'effects.tsv'))
    if len(items) > MAX_EXTENSIONS or len({item[1] for item in items}) != len(items):
        raise ValueError('Too many or duplicate extension entries')
    return items


def fetch(url: str, maximum: int) -> bytes:
    request = urllib.request.Request(url, headers={'User-Agent': 'Kuhl-OS/0.2 (compatible GNOME extensions)'})
    with urllib.request.urlopen(request, timeout=25) as response:
        effective = urllib.parse.urlparse(response.geturl())
        if effective.scheme != 'https' or effective.hostname != HOST:
            raise RuntimeError('Download redirected away from extensions.gnome.org')
        blob = response.read(maximum + 1)
    if len(blob) > maximum:
        raise ValueError('Extension download exceeds size limit')
    return blob


def compatible_download(uuid: str, major: str) -> str | None:
    params = urllib.parse.urlencode({'uuid': uuid, 'shell_version': major})
    meta = json.loads(fetch(f'https://{HOST}/extension-info/?{params}', 100_000))
    if meta.get('uuid') not in (None, uuid):
        raise ValueError('GNOME API returned a mismatching extension UUID')
    relative = meta.get('download_url')
    if not relative:
        return None
    parsed = urllib.parse.urlparse(urllib.parse.urljoin(f'https://{HOST}', relative))
    if parsed.scheme != 'https' or parsed.hostname != HOST or not parsed.path.startswith('/download-extension/'):
        raise ValueError('GNOME API returned an unexpected download URL')
    return parsed.geturl()


def inspect_zip(blob: bytes, uuid: str, major: str) -> None:
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        entries = archive.infolist()
        if len(entries) > 650 or sum(entry.file_size for entry in entries) > 65 * 1024 * 1024:
            raise ValueError('Suspiciously large extension archive')
        metadata = json.loads(archive.read('metadata.json'))
        if metadata.get('uuid') != uuid:
            raise ValueError('Extension ZIP has a different UUID')
        if major not in [str(v) for v in metadata.get('shell-version', [])]:
            raise ValueError(f'Extension not declared compatible with GNOME {major}')


def gnome(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(['gnome-extensions', *arguments], text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def installed_by_kuhl(state: Path) -> set[str]:
    if not state.exists():
        return set()
    return {line for line in state.read_text().splitlines() if re.fullmatch(r'[\w.-]+@[\w.-]+', line)}


def write_state(state: Path, uuids: set[str]) -> None:
    state.parent.mkdir(parents=True, exist_ok=True)
    if uuids:
        state.write_text('\n'.join(sorted(uuids)) + '\n', encoding='utf-8')
        state.chmod(0o600)
    else:
        state.unlink(missing_ok=True)


def install(profile: str, config: Path, state: Path) -> int:
    if not shutil.which('gnome-extensions') or not shutil.which('gnome-shell'):
        log('GNOME extension tools unavailable; install gnome-extensions-app then retry.')
        return 1
    major = shell_version()
    log(f'GNOME Shell {major}, installing Kuhl {profile} profile (compatible releases only)')
    added = installed_by_kuhl(state)
    # Switching from Full to Balanced removes only effects installed by Kuhl.
    if profile == 'balanced':
        effects = {item[1] for item in read_manifest(config / 'effects.tsv')}
        for uuid in sorted(added & effects):
            gnome('disable', uuid)
            result = gnome('uninstall', uuid)
            if result.returncode:
                log(f'Could not remove optional effect {uuid}; retry after logging in.')
            else:
                added.remove(uuid)
                log(f'Removed optional effect for Balanced mode: {uuid}')
        write_state(state, added)
    new = skipped = 0
    for name, uuid, details in profile_items(profile, config):
        if gnome('info', uuid).returncode == 0:
            log(f'Already present; leaving user setting unchanged: {name}')
            skipped += 1
            continue
        try:
            url = compatible_download(uuid, major)
            if not url:
                log(f'NOT AVAILABLE for GNOME {major}: {name}; {details}')
                skipped += 1
                continue
            blob = fetch(url, MAX_DOWNLOAD)
            inspect_zip(blob, uuid, major)
            with tempfile.TemporaryDirectory(prefix='kuhl-ext-') as directory:
                path = Path(directory) / (uuid + '.zip')
                path.write_bytes(blob)
                result = gnome('install', str(path))
            if result.returncode:
                log(f'Could not install {name}: {result.stderr.strip()}')
                skipped += 1
                continue
            added.add(uuid)
            write_state(state, added)
            result = gnome('enable', uuid)
            if result.returncode:
                log(f'Installed {name}. Enable it in Extensions after logging back in.')
            else:
                log(f'Installed and enabled {name}.')
            new += 1
        except (OSError, ValueError, RuntimeError, KeyError, json.JSONDecodeError,
                zipfile.BadZipFile, subprocess.CalledProcessError) as exc:
            log(f'Skipped {name}: {exc}. Manual page: {details}')
            skipped += 1
    log(f'Finished: {new} installed; {skipped} pre-existing/unavailable/skipped. Log out/in.')
    return 0


def uninstall(state: Path) -> int:
    if not shutil.which('gnome-extensions'):
        log('GNOME extensions command not found; cannot remove extensions automatically.')
        return 1
    tracked = installed_by_kuhl(state)
    if not tracked:
        log('No Kuhl-installed GNOME extensions found; leaving user extensions alone.')
        return 0
    pending = set()
    for uuid in sorted(tracked):
        gnome('disable', uuid)
        result = gnome('uninstall', uuid)
        if result.returncode:
            pending.add(uuid)
            log(f'Could not uninstall {uuid}: {result.stderr.strip()}')
        else:
            log(f'Removed {uuid}')
    write_state(state, pending)
    return 1 if pending else 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Kuhl OS compatible GNOME extensions')
    parser.add_argument('action', choices=('install', 'uninstall', 'list'))
    parser.add_argument('--profile', choices=('balanced', 'full'), default='full')
    parser.add_argument('--config', type=Path, default=ROOT / 'config')
    parser.add_argument('--state', type=Path, default=Path.home() / '.local/state/kuhl/installed-extensions.txt')
    args = parser.parse_args()
    if args.action == 'list':
        for name, uuid, url in profile_items(args.profile, args.config):
            print(f'{name}\t{uuid}\t{url}')
        return 0
    if args.action == 'install':
        return install(args.profile, args.config, args.state)
    return uninstall(args.state)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        log(f'ERROR: {exc}')
        sys.exit(1)
