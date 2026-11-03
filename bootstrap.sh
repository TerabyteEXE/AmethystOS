#!/usr/bin/env bash
# One-command entry point. Source: https://github.com/TerabyteEXE/Kuhl-OS
set -Eeuo pipefail
URL="https://github.com/TerabyteEXE/Kuhl-OS/archive/refs/heads/main.tar.gz"
TMP=$(mktemp -d)
trap 'rm -rf -- "$TMP"' EXIT
command -v curl >/dev/null || { echo 'curl required' >&2; exit 1; }
command -v tar >/dev/null || { echo 'tar required' >&2; exit 1; }
if [[ $(id -u) -eq 0 ]]; then echo 'Do not run as root' >&2; exit 2; fi
printf 'Fetching the Kuhl OS source from GitHub...\n'
curl --proto '=https' --tlsv1.2 -fsSL --retry 2 "$URL" -o "$TMP/source.tgz"
# Reject path traversal/absolute paths and nonstandard links in the fetched archive.
python3 - "$TMP/source.tgz" "$TMP" <<'PY'
import pathlib, sys, tarfile
archive, dest = sys.argv[1:]
with tarfile.open(archive, 'r:gz') as tf:
    for m in tf.getmembers():
        p=pathlib.PurePosixPath(m.name)
        if p.is_absolute() or '..' in p.parts or not (m.isdir() or m.isfile()):
            sys.exit('Unsafe archive member: ' + m.name)
    tf.extractall(dest, filter='data')
PY
PROJECT="$TMP/Kuhl-OS-main"
[[ -f "$PROJECT/install.sh" ]] || { echo 'Installer missing from release archive' >&2; exit 1; }
bash "$PROJECT/install.sh" "$@"
