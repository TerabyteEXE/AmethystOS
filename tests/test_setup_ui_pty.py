#!/usr/bin/env python3
"""Exercise the actual arrow-key+Space installer TUI inside a PTY.

Unlike a stdin-pipe test, this uses an application-cursor-key sequence as
emitted by a terminal after curses enables keypad mode.
"""
import json
import os
from pathlib import Path
import pty
import select
import signal
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def test() -> None:
    with tempfile.TemporaryDirectory(prefix='amethyst-ui-test-') as tmp:
        result = Path(tmp) / 'choices.json'
        pid, fd = pty.fork()
        if pid == 0:
            os.environ['TERM'] = 'xterm-256color'
            os.execvp(sys.executable, [sys.executable, str(ROOT / 'scripts/setup_ui.py'), '--output', str(result)])
        try:
            def drain(seconds):
                end = time.monotonic() + seconds
                while time.monotonic() < end:
                    readable, _, _ = select.select([fd], [], [], .03)
                    if readable:
                        try:
                            os.read(fd, 65536)
                        except OSError:
                            return

            drain(.5)
            # Pick Firefox, ArrowDown to Chromium, pick Chromium.
            for keys in [b' ', b'\x1bOB', b' ']:
                os.write(fd, keys)
                drain(.22)
            os.write(fd, b'\r')
            drain(.3)
            os.write(fd, b'y\n')
            drain(.2)
            deadline = time.monotonic() + 5
            status = None
            while time.monotonic() < deadline:
                finished, raw = os.waitpid(pid, os.WNOHANG)
                if finished:
                    status = os.waitstatus_to_exitcode(raw)
                    break
                drain(.1)
            if status is None:
                raise AssertionError('Installer menu did not exit after confirmation')
            assert status == 0, f'menu exited with status {status}'
            plan = json.loads(result.read_text())
            assert plan['groups'] == ['chromium', 'firefox'], plan
            print('[ok] Arrow-key, Space and Enter terminal checklist')
        finally:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                pass
            os.close(fd)


if __name__ == '__main__':
    test()
