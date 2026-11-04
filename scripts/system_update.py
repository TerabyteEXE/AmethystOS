#!/usr/bin/env python3
"""Conservative AmethystOS updater.

Updates installed Fedora RPMs/Flatpaks, then optionally refreshes AmethystOS
user configuration from a SHA-pinned archive of the official GitHub repository.
No unattended desktop code execution, no auto-added repos, no boot changes.
"""
from __future__ import annotations
import argparse
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen
import zipfile

REPOSITORY = 'TerabyteEXE/AmethystOS'
COMMIT_URL = f'https://api.github.com/repos/{REPOSITORY}/commits/main'
ARCHIVE_PREFIX = f'https://codeload.github.com/{REPOSITORY}/zip/'
MAX_BYTES = 65 * 1024 * 1024
MAX_UNPACKED = 160 * 1024 * 1024


def source_urls(sha: str) -> tuple[str, str]:
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('GitHub returned an invalid commit identifier')
    return ARCHIVE_PREFIX + sha, f'https://github.com/{REPOSITORY}/commit/{sha}'


def fetch(url: str, limit: int = MAX_BYTES) -> bytes:
    request = Request(url, headers={'User-Agent': 'AmethystOS-updater/1.0',
                                    'Accept': 'application/vnd.github+json'})
    with urlopen(request, timeout=25) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Archive exceeds the size limit; refusing update')
    return data


def latest_commit() -> str:
    response = json.loads(fetch(COMMIT_URL, 128 * 1024))
    sha = response.get('sha', '')
    source_urls(sha)
    return sha


def safely_extract(data: bytes, into: Path, sha: str) -> Path:
    """Extract only normal files within GitHub's single expected archive root."""
    prefix = f'AmethystOS-{sha}/'
    total = 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for item in archive.infolist():
            if not item.filename.startswith(prefix):
                raise ValueError('Archive contains an unexpected root path')
            relative = PurePosixPath(item.filename[len(prefix):])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe path in release archive')
            if not relative.parts or item.is_dir():
                continue
            mode = (item.external_attr >> 16) & 0xffff
            if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                raise ValueError('Archive contains an unsupported file type')
            total += item.file_size
            if total > MAX_UNPACKED:
                raise ValueError('Unpacked archive exceeds the size limit')
            destination = into.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item) as inp, destination.open('wb') as out:
                shutil.copyfileobj(inp, out)
    for required in ('install.sh', 'scripts/deploy.py', 'LICENSE', 'VERSION'):
        if not (into / required).is_file():
            raise ValueError('Official archive missing required file: ' + required)
    return into


def current_version() -> str:
    version = Path.home()/'.local/share/amethystos/VERSION'
    try:
        return version.read_text().strip()
    except OSError:
        return 'unknown (pre-updater installation)'


def confirm(message: str) -> bool:
    if not sys.stdin.isatty():
        print('Interactive confirmation is required. Run this command in a terminal.')
        return False
    try:
        return input(message+' [y/N] ').strip().lower() in ('y', 'yes')
    except (EOFError, KeyboardInterrupt):
        return False


def update_packages() -> int:
    print('\n[1/2] Updating Fedora RPM packages (DNF will show its transaction)...', flush=True)
    status = subprocess.call(['sudo', 'dnf', 'upgrade', '--refresh'])
    if status:
        print('Fedora update failed; no desktop update was attempted.')
        return status
    if shutil.which('flatpak'):
        print('\n[2/2] Updating installed user Flatpaks...', flush=True)
        status = subprocess.call(['flatpak', 'update', '--user'])
        if status:
            print('Flatpak returned a nonzero exit status.')
            return status
    return 0


def update_desktop() -> int:
    print('\nChecking the official AmethystOS repository...', flush=True)
    sha = latest_commit()
    archive_url, review_url = source_urls(sha)
    print(f'Installed version: {current_version()}')
    print('Latest main commit: ' + sha[:12])
    print('Review source: ' + review_url)
    print('The installer will back up and replace managed desktop configurations.')
    print('Personal wallpapers and GNOME remain installed; no boot files are changed.')
    if not confirm('Download this commit and run its reviewed installer?'):
        print('AmethystOS desktop update canceled.')
        return 0
    with tempfile.TemporaryDirectory(prefix='amethystos-update-') as temp:
        root = safely_extract(fetch(archive_url), Path(temp)/'source', sha)
        # Existing user appearance persists. Do not install optional app groups
        # again and do not change the running system's boot configuration.
        cmd = ['bash', str(root/'install.sh'), '--replace', '--no-packages',
               '--apps=', '--non-interactive', '--preserve-appearance']
        print('\nLaunching the AmethystOS desktop installer...', flush=True)
        return subprocess.call(cmd, cwd=root)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Update Fedora and the AmethystOS desktop')
    parser.add_argument('target', nargs='?', choices=('all', 'packages', 'desktop', 'check'), default='all')
    parser.add_argument('--dry-run', action='store_true', help='Print the plan without network or changes')
    args = parser.parse_args(argv)
    if args.dry_run:
        print(f'AmethystOS update plan: {args.target} (no changes)')
        print('Fedora: sudo dnf upgrade --refresh; Flatpak: flatpak update --user')
        print('Desktop: SHA-pinned GitHub source, explicit review + confirmation, backed-up installer')
        return 0
    try:
        if args.target == 'check':
            sha = latest_commit()
            print('Installed version:', current_version())
            print('Main commit:', sha)
            print('Review:', source_urls(sha)[1])
            return 0
        if args.target in ('all', 'packages'):
            if not confirm('Update Fedora and installed Flatpaks?'):
                return 0
            status = update_packages()
            if status:
                return status
        if args.target in ('all', 'desktop'):
            return update_desktop()
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f'AmethystOS update stopped safely: {exc}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
