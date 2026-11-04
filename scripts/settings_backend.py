#!/usr/bin/env python3
"""Pure, testable command mapping for the AmethystOS Settings GTK interface.

No shell interpolation, elevated privileges, or side effects occur here.
"""
from __future__ import annotations

PAGES = ('home', 'appearance', 'bar', 'devices', 'desktop', 'software', 'system')
ALIASES = {
    'menu':'home', 'settings':'home', '': 'home',
    'wallpaper':'appearance', 'wallpapers':'appearance',
    'scaling':'appearance', 'light':'appearance', 'dark':'appearance',
    'network':'devices', 'audio':'devices', 'bluetooth':'devices',
    'display':'desktop', 'workspaces':'desktop', 'calendar':'desktop',
    'updates':'software', 'install':'software', 'remove':'software',
    'keys':'system', 'diagnostics':'system', 'boot':'system',
}
MODULES = ('cpu', 'memory', 'battery', 'player', 'bluetooth', 'clipboard', 'tray')
DENSITIES = ('compact', 'normal', 'roomy')
POSITIONS = ('top', 'bottom')
SCALES = (100, 115, 125, 150, 175)


def page_for(value: str) -> str:
    page = ALIASES.get(value, value)
    if page not in PAGES:
        raise ValueError(f'Unknown settings page: {value}')
    return page


def bar_action(action: str, value: str) -> tuple[str, str]:
    options = {'position':POSITIONS, 'density':DENSITIES, 'toggle':MODULES}
    if action not in options or value not in options[action]:
        raise ValueError(f'Invalid top bar setting: {action} {value}')
    return action, value


def appearance_action(kind: str, value: str) -> tuple[str, str]:
    if kind == 'theme' and value in ('dark','light'):
        return kind, value
    if kind == 'scale' and value in ('auto', *(str(s) for s in SCALES)):
        return kind, value
    raise ValueError(f'Invalid appearance setting: {kind} {value}')
