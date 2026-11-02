#!/usr/bin/env bash
# Limited, reversible GDM greeter branding (official org.gnome.login-screen.logo).
set -Eeuo pipefail
operation="${1:-}"
file='/etc/dconf/db/gdm.d/95-kuhl-logo'
logo='/usr/local/share/kuhl/kuhl-logo.svg'
profile='/etc/dconf/profile/gdm'
case "$operation" in
  install)
    source_file="${2:-}"
    [[ -f "$source_file" ]] || { echo 'Missing Kuhl logo'; exit 1; }
    if [[ -e "$file" ]] && ! sudo grep -Fq '# managed-by: kuhl-os' "$file"; then
      echo "Another administrator owns $file; refusing overwrite." >&2
      exit 1
    fi
    # Preserve any existing GDM dconf profile; only create the GNOME default when absent.
    if sudo test -f "$profile"; then
      if ! sudo grep -Fq 'system-db:gdm' "$profile"; then
        echo "GDM profile exists but lacks system-db:gdm; refusing to edit it." >&2
        exit 1
      fi
    else
      sudo install -d -m 755 /etc/dconf/profile
      printf 'user-db:user\nsystem-db:gdm\nfile-db:/usr/share/gdm/greeter-dconf-defaults\n' | sudo tee "$profile" >/dev/null
      sudo touch /etc/dconf/profile/.kuhl-created-gdm
    fi
    sudo install -d -m 755 /usr/local/share/kuhl /etc/dconf/db/gdm.d
    sudo install -m 644 "$source_file" "$logo"
    printf "# managed-by: kuhl-os\n[org/gnome/login-screen]\nlogo='%s'\n" "$logo" | sudo tee "$file" >/dev/null
    sudo dconf update
    echo 'Installed the Kuhl greeter logo. Other GDM settings were not changed.'
    ;;
  uninstall)
    if sudo test -f "$file" && sudo grep -Fq '# managed-by: kuhl-os' "$file"; then
      sudo rm -f "$file" "$logo"
      sudo dconf update
      echo 'Removed Kuhl-owned login logo.'
    fi
    # Existing profile is left alone to avoid disrupting other customizations.
    ;;
  *) echo 'Usage: gdm-brand.sh install path/to/logo.svg | uninstall' >&2; exit 2;;
esac
