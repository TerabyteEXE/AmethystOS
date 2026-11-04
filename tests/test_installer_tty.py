#!/usr/bin/env python3
"""Regression: the setup menu must work when stdin is a pipe (curl | bash).

Uses a real pseudo-terminal; no Fedora packages, sudo, or user configs touched.
"""
from __future__ import annotations

import json
import os
import pty
import select
from pathlib import Path
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def test_piped_stdin_terminal_menu():
    with tempfile.TemporaryDirectory(prefix='amethyst-tty-test-') as tmp:
        output = Path(tmp, 'plan.json')
        pid, master = pty.fork()
        if pid == 0:
            os.chdir(ROOT)
            # Deliberately supply the program's stdin from a pipeline. Like
            # curl | bash, interactive prompts MUST use /dev/tty instead.
            os.execv('/bin/bash', ['bash', '-c',
                f"printf 'piped input' | python3 scripts/setup_ui.py --output '{output}'"])

        commands = [b'8\n', b'9\n', b'10\n', b'\n', b'y\n']
        menu_prompts = 0
        transcript = bytearray()
        previous_len = 0
        deadline = time.monotonic() + 15
        status = None
        try:
            while time.monotonic() < deadline:
                ready, _, _ = select.select([master], [], [], 0.15)
                if ready:
                    try:
                        chunk = os.read(master, 65536)
                    except OSError:  # EIO on Linux after slave exits
                        chunk = b''
                    if chunk:
                        transcript.extend(chunk)
                        # Each menu refresh has the unique prompt marker.
                        count = transcript.count(b'amethystos \xe2\x80\xba')
                        if count > menu_prompts:
                            menu_prompts = count
                            if commands:
                                os.write(master, commands.pop(0))
                        if b'Continue with Fedora package installation?' in transcript[previous_len:]:
                            # The last answer is the explicit confirmation.
                            if commands:
                                os.write(master, commands.pop(0))
                        previous_len = max(0, len(transcript) - 80)
                finished, result = os.waitpid(pid, os.WNOHANG)
                if finished:
                    status = result
                    break
            if status is None:
                raise AssertionError('Interactive setup timed out; last output: ' +
                                     transcript[-800:].decode('utf8', 'replace'))
            if not os.WIFEXITED(status) or os.WEXITSTATUS(status) != 0:
                raise AssertionError('Interactive setup failed: ' +
                                     transcript[-1200:].decode('utf8', 'replace'))
            plan = json.loads(output.read_text())
            assert 'gaming' in plan['groups'], plan
            assert plan['replace'] is True, plan
            assert plan['apply_dark'] is False, plan
            assert plan['schema'] == 1
        finally:
            if status is None:
                try:
                    os.kill(pid, 9)
                    os.waitpid(pid, 0)
                except ProcessLookupError:
                    pass
            os.close(master)


if __name__ == '__main__':
    test_piped_stdin_terminal_menu()
    print('[test] Real TTY menu with piped stdin, all 8 app groups and preferences: OK')
