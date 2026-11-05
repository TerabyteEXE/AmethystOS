#!/usr/bin/env bash
# AmethystOS opt-in login screen switch: Fedora GDM <-> greetd + Noctalia Greeter.
# This script deliberately never stops the currently running graphical login.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
STATE=/var/lib/amethystos/greeter
GREETD_CONFIG=/etc/greetd/config.toml
usage() {
  cat <<'HELP'
AmethystOS Noctalia Greeter (Fedora 44+)
  bash scripts/greeter.sh prepare   Install prerequisites from enabled DNF repos and stage Amethyst wallpaper
  bash scripts/greeter.sh activate  Enable Noctalia Greeter on NEXT BOOT (does not stop this session)
  bash scripts/greeter.sh restore   Restore previous login manager on NEXT BOOT
  bash scripts/greeter.sh status    Show installed greeter and enabled display manager

Noctalia Greeter may need the community Terra repository. This script NEVER
adds a third-party repository automatically. See docs/GREETER.md before running.
Use Ctrl+Alt+F3 to access a text console if your login screen fails.
HELP
}
check_system() {
  [[ -r /etc/os-release ]] || { echo 'Cannot identify Fedora.' >&2; exit 1; }
  # shellcheck disable=SC1091
  source /etc/os-release
  [[ ${ID:-} == fedora && ${VERSION_ID%%.*} =~ ^[0-9]+$ && ${VERSION_ID%%.*} -ge 44 ]] || {
    echo 'Requires Fedora 44 or newer.' >&2; exit 1;
  }
  command -v systemctl >/dev/null || { echo 'systemd is required.' >&2; exit 1; }
}
require_user() { [[ $EUID -ne 0 ]] || { echo 'Run as your normal user, not root.' >&2; exit 2; }; }
current_dm() {
  local unit
  unit=$(readlink -f /etc/systemd/system/display-manager.service 2>/dev/null || true)
  if [[ -n $unit ]]; then basename "$unit"; else echo none; fi
}
prepare() {
  require_user; check_system
  if ! dnf -q repoquery --available noctalia-greeter >/dev/null 2>&1 || \
     [[ -z $(dnf -q repoquery --available --qf '%{name}' noctalia-greeter 2>/dev/null | grep -x noctalia-greeter || true) ]]; then
    if ! rpm -q noctalia-greeter >/dev/null 2>&1; then
      echo 'Noctalia Greeter is not available in your enabled DNF repositories.' >&2
      echo 'Review the Fedora/Terra installation instructions in docs/GREETER.md.' >&2
      exit 1
    fi
  fi
  sudo dnf install -y greetd noctalia-greeter accountsservice
  local wrapper helper
  wrapper=$(command -v noctalia-greeter-session || true)
  helper=$(command -v noctalia-greeter-apply-appearance || true)
  [[ -n $wrapper && -n $helper && $wrapper == /usr/* ]] || {
    echo 'Missing system-installed Noctalia Greeter wrapper/helper. No display manager switched.' >&2
    exit 1
  }
  sudo install -d -m 0755 "$STATE"
  if [[ ! -e "$STATE/original-greetd.toml" && -e $GREETD_CONFIG ]]; then
    sudo cp -a "$GREETD_CONFIG" "$STATE/original-greetd.toml"
  fi
  # Packages can use a different greeter user; preserve the existing account if configured.
  local greeter_user=greeter
  if [[ -f $GREETD_CONFIG ]]; then
    greeter_user=$(python3 - "$GREETD_CONFIG" <<'PY'
import sys,tomllib
with open(sys.argv[1], 'rb') as f: data=tomllib.load(f)
print(data.get('default_session',{}).get('user','greeter'))
PY
)
  fi
  id "$greeter_user" >/dev/null 2>&1 || { echo "Missing greetd user: $greeter_user" >&2; exit 1; }
  local newconfig
  newconfig=$(mktemp)
  python3 - "$GREETD_CONFIG" "$wrapper" "$greeter_user" > "$newconfig" <<'PY'
import pathlib,re,sys
path=pathlib.Path(sys.argv[1]); wrapper=sys.argv[2]; account=sys.argv[3]
s=path.read_text() if path.exists() else ''
block='[default_session]\ncommand = "'+wrapper+'"\nuser = "'+account+'"\n'
pattern=r'(?ms)^\[default_session\]\s*\n.*?(?=^\[|\Z)'
if re.search(pattern,s): s=re.sub(pattern,lambda m: block+'\n',s,count=1)
else: s=s.rstrip()+'\n\n'+block
print('# Managed by AmethystOS greeter integration. Original backed up in /var/lib/amethystos/greeter/\n'+s)
PY
  sudo install -m 0644 "$newconfig" "$GREETD_CONFIG"
  rm -f "$newconfig"
  sudo env GREETER_USER="$greeter_user" "$helper" --setup-system
  # Login wallpaper is stored outside $HOME, which is not readable by greetd.
  sudo install -m 0644 "$ROOT/assets/wallpapers/AmethystDark.png" /var/lib/noctalia-greeter/amethyst-dark.png
  # Only manage our own greeter.toml; preserve an administrator's existing edits.
  if [[ ! -f /var/lib/noctalia-greeter/greeter.toml ]] || \
       sudo grep -q '^# AmethystOS managed initial greeter appearance' /var/lib/noctalia-greeter/greeter.toml; then
    sudo tee /var/lib/noctalia-greeter/greeter.toml >/dev/null <<'TOML'
# AmethystOS managed initial greeter appearance
[session]
default = "Niri"
[appearance]
hide_logo = true
theme_mode = "dark"
font_family = "Noto Sans"
[appearance.wallpaper]
path = "/var/lib/noctalia-greeter/amethyst-dark.png"
fill_mode = "crop"
[clock]
enabled = true
position = "above-panel"
time_format = "{:%I:%M %p}"
[output]
use_synced_settings = false
TOML
    sudo chmod 0644 /var/lib/noctalia-greeter/greeter.toml
    sudo chown "$greeter_user:$(id -gn "$greeter_user")" /var/lib/noctalia-greeter/greeter.toml
  else
    echo 'Existing custom greeter.toml preserved; customize it manually if desired.'
  fi
  echo 'Prepared. Log in to Niri and sync the palette via Noctalia Settings → Security → Greeter → Sync Now.'
  echo 'Then run bash scripts/greeter.sh activate. Your running session will not be stopped.'
}
activate() {
  require_user; check_system
  command -v noctalia-greeter-session >/dev/null || { echo 'Run prepare first.' >&2; exit 1; }
  [[ -f $GREETD_CONFIG ]] || { echo 'Missing /etc/greetd/config.toml. Run prepare.' >&2; exit 1; }
  grep -q 'noctalia-greeter-session' "$GREETD_CONFIG" || { echo 'greetd is not configured for Noctalia.' >&2; exit 1; }
  local active
  active=$(current_dm)
  [[ $active == greetd.service ]] && { echo 'greetd is already enabled.'; return; }
  case "$active" in
    gdm.service|gdm3.service|sddm.service|lightdm.service|none) ;;
    *) echo "Unknown current display manager: $active; refusing to change it." >&2; exit 1;;
  esac
  sudo install -d -m 0755 "$STATE"
  if [[ ! -f $STATE/previous-dm ]]; then printf '%s\n' "$active" | sudo tee "$STATE/previous-dm" >/dev/null; fi
  if [[ $active != none ]]; then sudo systemctl disable "$active"; fi
  if ! sudo systemctl enable greetd.service; then
    echo 'Could not enable greetd; restoring old service selection.' >&2
    [[ $active == none ]] || sudo systemctl enable "$active"
    exit 1
  fi
  echo 'Noctalia Greeter enabled for the next boot; the current session is still running.'
  echo 'Reboot when ready. Recovery: Ctrl+Alt+F3 → login → bash scripts/greeter.sh restore → reboot.'
}
restore() {
  require_user; check_system
  [[ -f $STATE/previous-dm ]] || { echo 'No saved previous display manager. Cannot choose safely.' >&2; exit 1; }
  local prior
  prior=$(sudo cat "$STATE/previous-dm")
  case "$prior" in gdm.service|gdm3.service|sddm.service|lightdm.service) ;;
    *) echo "Saved manager is $prior; restore manually." >&2; exit 1;; esac
  sudo systemctl disable greetd.service || true
  sudo systemctl enable "$prior"
  echo "$prior restored for next boot. Reboot when ready. No packages or settings were deleted."
}
case "${1:-}" in
  prepare) prepare;; activate) activate;; restore) restore;;
  status) printf 'Current display manager: %s\n' "$(current_dm)"; command -v noctalia-greeter-session || true;;
  -h|--help|help|'') usage;;
  *) usage >&2; exit 2;;
esac
