"""Metadata-only Codex home audit. No content reads or deletion authority."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat

from setup import Deployment, deployment_lock, read_json, safe, save_json


def linked(path):
    return path.is_symlink() or bool(getattr(path.lstat(), 'st_file_attributes', 0) & 0x400)


def classify(name):
    if name in ('auth.json', 'secrets.json'):
        return 'credentials-preserve'
    if name in ('sessions', 'archived_sessions', 'attachments', 'generated_images', 'memories') or 'sqlite' in name:
        return 'user-history-state-preserve'
    if name == 'visualizations':
        return 'mixed-user-work-and-dependencies-review'
    if name in ('cache', '.tmp', 'plugins', 'vendor_imports', '.sandbox', '.sandbox-bin'):
        return 'application-owned-review-only'
    if name in ('AGENTS.md', 'guides', 'skills', 'profiles', 'config.toml', 'bin'):
        return 'configuration-check-with-installer'
    return 'unknown-ownership-preserve'


def measure(root):
    """Logical regular-file bytes; no links/reparse points, hardlinks deduped per row."""
    size = count = excluded = 0
    errors = []
    seen = set()
    pending = [root]
    while pending:
        path = pending.pop()
        try:
            if linked(path):
                excluded += 1
                continue
            info = path.lstat()
            if stat.S_ISDIR(info.st_mode):
                pending.extend(path.iterdir())
            elif stat.S_ISREG(info.st_mode):
                key = (info.st_dev, info.st_ino)
                if key not in seen:
                    seen.add(key)
                    size += info.st_size
                    count += 1
            else:
                excluded += 1
        except OSError:
            errors.append('metadata-unavailable')
    return {'logical_bytes': size, 'regular_files': count,
            'excluded_entries': excluded, 'errors': len(errors)}


def scan(home):
    home = Path(home).absolute()
    # Also reject linked ancestors, including a linked/missing home.
    safe(home, 'config.toml')
    if not home.is_dir():
        raise ValueError('Codex home is unavailable; not an empty healthy scan')
    rows = []
    for path in sorted(home.iterdir()):
        rows.append({'entry': path.name, 'classification': classify(path.name),
                     **measure(path), 'deletion': 'not-authorized-by-this-audit'})
    return {'schema_version': 1, 'checked_at': datetime.now(timezone.utc).isoformat(),
            'status': 'partial' if any(r['errors'] for r in rows) else 'collected',
            'entries': rows, 'total_logical_bytes': sum(r['logical_bytes'] for r in rows),
            'limit': 'Metadata only; cross-row hardlinks can be counted twice. Logical bytes are not physical allocation, inactivity or proof of safe deletion. No raw file contents.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['scan'])
    parser.add_argument('--home', type=Path)
    parser.add_argument('--state', type=Path)
    args = parser.parse_args()
    dep = Deployment(home=args.home, state=args.state)
    result = scan(dep.home)
    with deployment_lock(dep.state):
        path = safe(dep.state, 'routine-review.json')
        routine = read_json(path, None)
        if not isinstance(routine, dict):
            raise ValueError('Existing private routine state is required')
        routine.setdefault('feedback_loop', {})['codex_storage'] = result
        save_json(path, routine)
    print(json.dumps({'status': result['status'], 'entries': len(result['entries']),
                      'total_logical_bytes': result['total_logical_bytes'], 'deletions': 0}))
    return 1 if result['status'] == 'partial' else 0


if __name__ == '__main__':
    raise SystemExit(main())
