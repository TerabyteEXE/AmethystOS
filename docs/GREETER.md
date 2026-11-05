# AmethystOS login screen — Noctalia Greeter

Noctalia Greeter is a **separate greetd display manager** that replaces the GNOME
GDM login screen; Noctalia Shell is still the desktop UI inside Niri.
This is opt-in because a failed display-manager switch can prevent graphical login.
AmethystOS **does not uninstall GDM or GNOME**.

## Requirements

Fedora Workstation **44+**; working Niri session; working text console (Ctrl+Alt+F3);
`sudo` access; packages `greetd`, `noctalia-greeter`, `accountsservice`.
Fedora does not currently ship the greeter in its official repository. On Fedora
44+ the Noctalia project documents the community-maintained **Terra** repository.
Adding Terra is a separate trust decision: review <https://docs.noctalia.dev/greeter/installation/>
and <https://terrapkg.com/> and enable it yourself before proceeding.

The upstream documented Terra setup is:

```bash
sudo dnf install --nogpgcheck --repofrompath 'terra,https://repos.fyralabs.com/terra$releasever' terra-release
```

**Important:** `--nogpgcheck` skips signature verification for that bootstrap RPM.
Do not run it until you have inspected and chosen to trust that package source.
The AmethystOS installer **never** runs this command or adds Terra for you.

## Installation

From the extracted AmethystOS repo on your installed Fedora PC:

```bash
bash scripts/greeter.sh prepare
```

This installs the greeter from *already enabled* repositories, backs up an existing
`/etc/greetd/config.toml`, points greetd at the correct Noctalia session wrapper,
initializes the greeter account/state, and installs the Amethyst Dark wallpaper
into a system location readable before login. It leaves your current display
manager running and enabled. Existing administrator-written `greeter.toml`
settings are not overwritten.

In your running AmethystOS desktop, open **Noctalia Settings → Security → Noctalia
Greeter → Sync Now** to copy the current Amethyst palette and font to the greeter.
This may prompt for administrator authentication; it is normal. If you later
want automatic syncing, enable **Auto-Sync Greeter** on the same page. The
initial wallpaper is explicitly pinned for a consistent login-screen fallback;
remove the `[appearance.wallpaper]` block from
`/var/lib/noctalia-greeter/greeter.toml` if you'd rather have wallpaper changes
track your Noctalia desktop wallpaper after each sync.

Then switch the login service *for the next boot*:

```bash
bash scripts/greeter.sh activate
sudo reboot
```

Do not run the switch over a remote-only connection. This does not stop your
running graphical session. At the login screen, choose **Niri** if it wasn't
selected automatically. GNOME remains an available session where supported.

## Recovering GNOME's GDM login

If the login UI fails, use `Ctrl+Alt+F3`, log into a text console with your
username and password, then run (from the extracted repo):

```bash
bash scripts/greeter.sh restore
sudo reboot
```

If the repo is unavailable, switch back manually:

```bash
sudo systemctl disable greetd.service
sudo systemctl enable gdm.service
sudo reboot
```

These steps alter **which display manager starts on boot**, not your users,
passwords, or GNOME installation. For debug logs, run:

```bash
systemctl status greetd.service
journalctl -b -u greetd.service --no-pager
```

No automatic changes to PAM, passwordless polkit policies, or active user sessions.
