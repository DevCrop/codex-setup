"""Codex-only agent-desktop entry point; no shell, retries or output logging."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

PINNED_SHA256 = '409e58cbdd6aed47e29771ffa60bc122a9843505a227af488cded85215943988'


def state_location(home):
    if os.name == 'nt':
        base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local'))
    elif sys.platform == 'darwin':
        base = Path.home() / 'Library/Application Support'
    else:
        base = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state'))
    return base / 'TRACE-Setup' / hashlib.sha256(str(home).encode()).hexdigest()[:16]


def checked_path(path):
    path = Path(path).absolute()
    for item in (path, *path.parents):
        if item.is_symlink() or (item.exists() and getattr(item.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Linked component path refused')
    return path


def runtime(home):
    state = checked_path(state_location(home) / 'components/agent-desktop')
    receipt = checked_path(state / 'runtime.json')
    record = json.loads(receipt.read_text(encoding='utf-8'))
    binary = checked_path(state / 'runtime/agent-desktop.exe')
    if record.get('owner') != 'TRACE Codex agent-desktop' or record.get('home') != str(home):
        raise ValueError('Component ownership mismatch')
    if (record.get('path') != str(binary) or record.get('sha256') != PINNED_SHA256
            or hashlib.sha256(binary.read_bytes()).hexdigest() != PINNED_SHA256):
        raise ValueError('agent-desktop runtime hash mismatch')
    sessions = checked_path(state / 'sessions')
    env = {k: v for k, v in os.environ.items() if not k.startswith('AGENT_DESKTOP_')}
    env['AGENT_DESKTOP_HOME'] = str(sessions)
    return binary, env


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        raise ValueError('Supply an explicit agent-desktop command')
    # Bind the installed skill to its own home, never to a foreign shell's HOME.
    home = Path(__file__).absolute().parents[3]
    if home.name != '.codex' and not (home / 'skills/codex-agent-desktop/scripts/desktop.py').is_file():
        raise ValueError('Run the installed Codex skill, not its source checkout')
    binary, env = runtime(home)
    return subprocess.call([str(binary), *argv], env=env)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
