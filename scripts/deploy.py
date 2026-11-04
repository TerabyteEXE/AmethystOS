#!/usr/bin/env python3
"""AmethystOS base: stage, validate, deploy, and restore the upstream dotfiles.

No commands are run as root. Existing files are never deleted without a backup.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payload"
CONFIG_DIRS = (
    "niri", "waybar", "fuzzel", "kitty", "alacritty", "mako", "niri-lock",
    "gtk-3.0", "gtk-4.0", "qt6ct", "btop", "cava", "fastfetch",
    "starship", "fish",
)
EXTRA_FILES = (
    "powermenu", "set-wallpaper", "clipboard-history", "mako-history",
    "notification-history", "amethystos-uninstall", "amethyst-settings", "amethyst-doctor", "amethyst-browser",
    "amethyst-theme", "amethyst-scale", "amethyst-boot",
    "amethyst-launcher", "amethyst-hub", "amethyst-bar", "amethyst-wallpapers",
    "amethyst-software", "amethyst-calendar",
)
SUFFIXES = {".sh", ".kdl", ".css", ".ini", ".toml", ".json", ".jsonc", ".conf", ".fish", ".desktop"}


def log(*message: object) -> None:
    print("[amethystos]", *message, flush=True)


def expand_placeholders(base: Path, home: Path) -> None:
    for p in base.rglob("*"):
        if p.is_file() and (p.suffix in SUFFIXES or p.name in ("config", "colors.conf")):
            try:
                txt = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if "__HOME__" in txt:
                p.write_text(txt.replace("__HOME__", str(home)), encoding="utf-8")


def sources() -> list[tuple[Path, Path]]:
    mapping = [(PAYLOAD / name, Path(".config") / name) for name in CONFIG_DIRS]
    mapping.append((PAYLOAD / "xdg-desktop-portal/niri-portals.conf", Path(".config/xdg-desktop-portal/niri-portals.conf")))
    # Keep a self-contained uninstaller after the one-command bootstrap archive is removed.
    mapping.append((ROOT / "scripts/deploy.py", Path(".local/share/amethystos/deploy.py")))
    mapping.append((ROOT / "scripts/desktop_prefs.py", Path(".local/share/amethystos/desktop_prefs.py")))
    mapping.append((ROOT / "scripts/appearance.py", Path(".local/share/amethystos/appearance.py")))
    for script in ("bar_config.py", "wallpaper_gui.py", "calendar_gui.py", "software.py"):
        mapping.append((ROOT / "scripts" / script, Path(".local/share/amethystos") / script))
    mapping.append((ROOT / "scripts/boot_theme.sh", Path(".local/share/amethystos/boot_theme.sh")))
    mapping.append((ROOT / "assets/themes", Path(".local/share/amethystos/themes")))
    mapping.append((ROOT / "assets/plymouth", Path(".local/share/amethystos/assets/plymouth")))
    mapping.extend((source,Path(".local/share/applications") / source.name)
                   for source in sorted((PAYLOAD / "applications").glob("*.desktop")))
    mapping.extend((PAYLOAD / "local-bin" / name, Path(".local/bin") / name) for name in EXTRA_FILES)
    return mapping


def digest_path(path: Path) -> str:
    sha = hashlib.sha256()
    if path.is_file():
        sha.update(path.read_bytes())
    elif path.is_dir():
        for f in sorted(x for x in path.rglob("*") if x.is_file()):
            sha.update(str(f.relative_to(path)).encode())
            sha.update(f.read_bytes())
    return sha.hexdigest()


def stage_files(stage: Path, home: Path) -> list[tuple[Path, Path]]:
    entries = []
    for source, dest in sources():
        if not source.exists():
            raise FileNotFoundError(f"Missing bundled file: {source}")
        target = stage / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, symlinks=False)
        else:
            shutil.copy2(source, target)
        entries.append((target, home / dest))
    expand_placeholders(stage, home)
    for path in (stage / ".config/niri/autostart.sh", stage / ".config/niri-lock/lock.sh"):
        path.chmod(0o755)
    for path in (stage / ".config/waybar/scripts").glob("*.sh"):
        path.chmod(0o755)
    for path in (stage / ".local/bin").iterdir():
        path.chmod(0o755)
    return entries


def validate(stage: Path, require_niri: bool) -> None:
    niri = shutil.which("niri")
    if not niri:
        if require_niri:
            raise RuntimeError("Niri is not installed: run the full installer first")
        log("Niri not installed; native parser validation skipped")
        return
    config = stage / ".config/niri/config.kdl"
    # --config is accepted by niri validate and resolves relative includes.
    result = subprocess.run([niri, "validate", "--config", str(config)], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Niri config rejected:\n" + (result.stdout + result.stderr))
    log("Niri configuration validated")


def install(home: Path, replace: bool, dry_run: bool, require_niri: bool) -> None:
    home = home.resolve()
    state_dir = home / ".local/state/amethystos-base-v1"
    with tempfile.TemporaryDirectory(prefix="amethystos-stage-") as temp:
        stage = Path(temp)
        entries = stage_files(stage, home)
        validate(stage, require_niri)
        collisions = [str(dest.relative_to(home)) for _, dest in entries if dest.exists() or dest.is_symlink()]
        if collisions and not replace:
            raise RuntimeError("Existing configuration detected. Re-run with --replace after reviewing backups:\n" + "\n".join(" • " + c for c in collisions))
        if dry_run:
            log("Dry run: would install", len(entries), "configuration paths")
            if collisions:
                log("Dry run: would back up", len(collisions), "existing paths")
            return
        if state_dir.exists() and not replace:
            raise RuntimeError("Existing AmethystOS state found; use --replace to reinstall safely")
        # Preserve the ORIGINAL user configuration across repeated AmethystOS
        # upgrades. Earlier versions replaced state.json and only backed up the
        # previously installed Amethyst files; that made uninstall undo just
        # one upgrade instead of returning to the pre-Amethyst desktop.
        previous = {}
        prev_file = state_dir / "state.json"
        if prev_file.is_file():
            prev = json.loads(prev_file.read_text(encoding="utf-8"))
            previous = {e["path"]: e for e in prev.get("entries", [])}
        runid = time.strftime("%Y%m%d-%H%M%S") + f"-{os.getpid()}"
        backup_dir = state_dir / "backups" / runid
        backup_dir.mkdir(parents=True, exist_ok=False)
        changed: list[tuple[Path, Path | None]] = []
        records = []
        try:
            for source, dest in entries:
                rel = dest.relative_to(home)
                dest.parent.mkdir(parents=True, exist_ok=True)
                backup: Path | None = None
                if dest.exists() or dest.is_symlink():
                    backup = backup_dir / rel
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(dest), str(backup))
                changed.append((dest, backup))
                if source.is_dir():
                    shutil.copytree(source, dest, symlinks=False)
                else:
                    shutil.copy2(source, dest)
                # The latest replaced Amethyst version remains archived in the
                # current run, while the restore target stays the user's
                # original (if this path was already managed).
                baseline_backup = previous[str(rel)]["backup"] if str(rel) in previous else (
                    str(backup.relative_to(home)) if backup else None)
                records.append({"path": str(rel), "backup": baseline_backup,
                                "sha256": digest_path(dest)})
            state = {"version":"1.0-base", "created":runid, "entries":records}
            state_tmp = state_dir / "state.json.tmp"
            state_tmp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
            state_tmp.replace(state_dir / "state.json")
        except Exception:
            for dest, backup in reversed(changed):
                if dest.is_dir() and not dest.is_symlink():
                    shutil.rmtree(dest)
                elif dest.exists() or dest.is_symlink():
                    dest.unlink()
                if backup and backup.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(backup), str(dest))
            raise
        log(f"Installed {len(records)} paths; backups: {backup_dir}")


def restore(home: Path, dry_run: bool) -> None:
    state_file = home / ".local/state/amethystos-base-v1/state.json"
    if not state_file.is_file():
        raise RuntimeError("No managed AmethystOS install was found")
    state = json.loads(state_file.read_text(encoding="utf-8"))
    entries = state["entries"]
    modified = [e["path"] for e in entries if (home/e["path"]).exists() and digest_path(home/e["path"])!=e["sha256"]]
    if modified:
        raise RuntimeError("Refusing to overwrite modified user configurations:\n" + "\n".join(" • " + p for p in modified))
    for e in reversed(entries):
        path = home / e["path"]
        backup = home / e["backup"] if e["backup"] else None
        if dry_run:
            log("Would restore", e["path"])
            continue
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        elif path.exists() or path.is_symlink():
            path.unlink()
        if backup and backup.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(backup), str(path))
    if not dry_run:
        state_file.unlink()
    log("Restoration completed" if not dry_run else "Dry-run restoration completed")


def main():
    parser = argparse.ArgumentParser(description="Deploy or restore the AmethystOS desktop")
    parser.add_argument("action", choices=("install","restore"))
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--require-niri", action="store_true")
    parser.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        if args.action == "install":
            install(args.home, args.replace, args.dry_run, args.require_niri)
        else:
            restore(args.home, args.dry_run)
    except Exception as exc:
        print("[amethystos] ERROR:", exc, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
