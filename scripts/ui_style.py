#!/usr/bin/env python3
"""AmethystOS GUI appearance/scale helpers. No GTK import for portable tests.

Native Wayland clients handle per-monitor DPI; this layer scales AmethystOS's
own controls and captions in application-logical pixels, not compositor pixels.
"""
from __future__ import annotations
import json
from pathlib import Path

PERCENTAGES = (100, 115, 125, 150, 175)
STATE_NAME = '.local/state/amethystos-base-v1/appearance.json'


def appearance(home: Path | None = None) -> tuple[str, int]:
    home = Path.home() if home is None else Path(home)
    try:
        data = json.loads((home / STATE_NAME).read_text(encoding='utf-8'))
        theme = data.get('theme', 'dark')
        theme = theme if theme in ('dark', 'light') else 'dark'
        scale = int(data.get('scale', 100))
        scale = scale if scale in PERCENTAGES else 100
        return theme, scale
    except (OSError, ValueError, TypeError, OverflowError, AttributeError):
        return 'dark', 100


def px(size: float, percent: int) -> int:
    """Use one rounding rule for readable UI sizes."""
    return max(1, round(size * percent / 100))


def window_size(width: int, height: int, percent: int,
                work_width: int = 1920, work_height: int = 1080) -> tuple[int, int]:
    """Scale moderately and stay within the monitor's usable area."""
    multiplier = 1 + (percent / 100 - 1) * .56
    return (min(round(width * multiplier), max(260, int(work_width * .88))),
            min(round(height * multiplier), max(245, int(work_height * .85))))


def workarea_size(gdk) -> tuple[int, int]:
    try:
        display = gdk.Display.get_default()
        monitor = display.get_primary_monitor() if display else None
        if monitor:
            area = monitor.get_workarea()
            if area.width > 0 and area.height > 0:
                return area.width, area.height
        screen = gdk.Screen.get_default()
        if screen:
            return max(1, screen.get_width()), max(1, screen.get_height())
    except (AttributeError, TypeError, RuntimeError):
        pass
    return 1920, 1080


def css_rules(surface: str, percent: int) -> str:
    """Only scope overrides to Amethyst widgets, keeping the original palette."""
    if percent not in PERCENTAGES:
        percent = 100
    p = lambda n: f'{px(n, percent)}px'
    if surface == 'launcher':
        return f'''
/* AmethystOS UI scale: {percent}%. */
window#amethyst-launcher {{ font-size: {p(14)}; }}
#amethyst-home-search {{ font-size: {p(14)}; min-height: {p(28)}; padding: {p(7)} {p(9)}; }}
#amethyst-home-item {{ padding: {p(9)} {p(9)}; }}
#amethyst-home-row-title {{ font-size: {p(14)}; }}
#amethyst-home-title {{ font-size: {p(13)}; }}
#amethyst-home-chevron {{ font-size: {p(15)}; }}
#amethyst-home-back {{ font-size: {p(18)}; min-width: {p(28)}; min-height: {p(28)}; }}
#amethyst-launcher-results row {{ min-height: {p(34)}; }}
'''
    if surface == 'settings':
        return f'''
/* AmethystOS UI scale: {percent}%. */
window#amethyst-settings {{ font-size: {p(15)}; }}
window#amethyst-settings label#amethyst-brand {{ font-size: {p(18)}; }}
window#amethyst-settings label#amethyst-tagline {{ font-size: {p(12)}; letter-spacing: 0px; }}
window#amethyst-settings stacksidebar row {{ padding: {p(8)} {p(10)}; min-height: {p(28)}; }}
window#amethyst-settings button {{ min-height: {p(34)}; padding: {p(5)} {p(12)}; }}
window#amethyst-settings combobox button {{ min-height: {p(34)}; }}
window#amethyst-settings switch {{ min-height: {p(24)}; min-width: {p(45)}; }}
window#amethyst-settings headerbar {{ min-height: {p(46)}; }}
'''
    if surface == 'popup':
        return f'''
/* AmethystOS UI scale: {percent}%. */
window#amethyst-bar-popup {{ font-size: {p(14)}; }}
#amethyst-popup-title {{ font-size: {p(16)}; }}
#amethyst-popup-muted {{ font-size: {p(13)}; }}
window#amethyst-bar-popup button {{ min-height: {p(32)}; padding: {p(7)} {p(12)}; font-size: {p(14)}; }}
window#amethyst-bar-popup calendar {{ font-size: {p(14)}; }}
'''
    if surface == 'gallery':
        return f'''
/* AmethystOS UI scale: {percent}%. */
window#amethyst-wallpaper-gallery {{ font-size: {p(14)}; }}
window#amethyst-wallpaper-gallery button {{ min-height: {p(34)}; font-size: {p(14)}; padding: {p(7)} {p(12)}; }}
window#amethyst-wallpaper-gallery iconview {{ font-size: {p(13)}; }}
'''
    raise ValueError('Unknown AmethystOS UI surface: ' + surface)


def install_override(gtk, gdk, surface: str, percent: int):
    """Apply the sizing layer after the base theme, scoped to this process."""
    provider = gtk.CssProvider()
    provider.load_from_data(css_rules(surface, percent).encode('utf-8'))
    screen = gdk.Screen.get_default()
    if screen is not None:
        gtk.StyleContext.add_provider_for_screen(
            screen, provider, gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
    return provider
