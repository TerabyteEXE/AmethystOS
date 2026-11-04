#!/usr/bin/env bash
# Optional, explicit system-level Plymouth theme. Never change bootloader config.
set -Eeuo pipefail
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$HERE/../assets/plymouth/boot-logo.png" ]]; then
  ASSETS="$HERE/../assets/plymouth"
else
  ASSETS="$HERE/assets/plymouth"
fi
THEME=amethystos
DEST=/usr/share/plymouth/themes/$THEME
STATE=/var/lib/amethystos
case "${1:-}" in
  --apply)
    [[ -f /etc/fedora-release ]] || { echo 'This boot theme is Fedora-only.' >&2; exit 1; }
    command -v plymouth-set-default-theme >/dev/null || { echo 'Install Plymouth before enabling a boot theme.' >&2; exit 1; }
    command -v dracut >/dev/null || { echo 'dracut is required to rebuild initramfs.' >&2; exit 1; }
    [[ -f "$ASSETS/boot-logo.png" ]] || { echo 'Missing AmethystOS crystal logo.' >&2; exit 1; }
    echo 'This will install an AmethystOS boot splash and rebuild the initramfs.'
    echo 'It does not change your bootloader, firmware or GNOME login screen.'
    previous=$(plymouth-set-default-theme)
    sudo install -d -m 755 "$DEST" "$STATE"
    if ! sudo test -f "$STATE/previous-plymouth-theme"; then
      printf '%s\n' "$previous" | sudo tee "$STATE/previous-plymouth-theme" >/dev/null
    fi
    sudo install -m 644 "$ASSETS/boot-logo.png" "$DEST/logo.png"
    sudo install -m 644 "$ASSETS/amethystos.plymouth" "$DEST/amethystos.plymouth"
    sudo install -m 644 "$ASSETS/amethystos.script" "$DEST/amethystos.script"
    sudo plymouth-set-default-theme "$THEME" -R
    echo 'AmethystOS boot splash enabled. If your firmware hides Plymouth, visibility can differ.' ;;
  --restore)
    previous=$(sudo cat "$STATE/previous-plymouth-theme" 2>/dev/null || true)
    [[ -n "$previous" ]] || { echo 'Previous Plymouth theme not recorded; no changes made.' >&2; exit 1; }
    sudo plymouth-set-default-theme "$previous" -R
    echo 'Restored previous Plymouth theme:' "$previous" ;;
  --status) plymouth-set-default-theme ;;
  *) echo 'Usage: amethyst-boot [--apply|--restore|--status]' >&2; exit 2 ;;
esac
