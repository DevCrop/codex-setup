"""Explicit local RTK backup; no repair, source writes, scheduler or raw-row export."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from setup import Deployment, atomic, deployment_lock, read_json, safe, save_json
from rtk_dashboard import safe_file


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sqlite(tool, database, sql):
    result = subprocess.run([str(tool), '-readonly', str(database)],
                            input='.timeout 5000\n.bail on\n' + sql + '\n',
                            capture_output=True, text=True, encoding='utf-8', timeout=30)
    if result.returncode:
        # Do not export database paths, SQL, stderr or command rows.
        raise ValueError('SQLite check/backup failed; preserve previous backup')
    return result.stdout.strip().splitlines()


def backup(database, tool, tool_sha256, state):
    database, tool, state = map(safe_file, (database, tool, state))
    if not database.is_file() or not tool.is_file() or digest(tool) != tool_sha256:
        raise ValueError('Missing database or unverified SQLite tool')
    if any(ord(c) < 32 for c in str(database) + str(state)):
        raise ValueError('Control characters in SQLite paths refused')
    version = subprocess.run([str(tool), '-version'], capture_output=True,
                             text=True, encoding='utf-8', timeout=10)
    match = re.match(r'(\d+)\.(\d+)\.(\d+)\b', version.stdout)
    if version.returncode or not match or tuple(map(int, match.groups())) < (3, 51, 3):
        raise ValueError('Reviewed SQLite 3.51.3+ required')
    folder = safe_file(state / 'rtk-db-backup')
    if database == folder or folder in database.parents:
        raise ValueError('Source database overlaps backup scope')
    with deployment_lock(folder):
        receipt_path = safe(folder, 'receipt.json')
        receipt = read_json(receipt_path, {})
        if not isinstance(receipt, dict) or (receipt_path.exists() and
                (not isinstance(receipt.get('current'), dict) or
                 not re.fullmatch(r'[0-9a-f]{64}', receipt['current'].get('sha256', '')))):
            raise ValueError('Unowned backup receipt refused')
        for name in ('current', 'previous'):
            target = safe(folder, name + '.db')
            saved = receipt.get(name)
            if target.exists() and (not isinstance(saved, dict) or digest(target) != saved.get('sha256')):
                raise ValueError('Unowned or modified backup refused')
            if saved and not target.is_file():
                raise ValueError('Recorded backup missing')
        # Read-only checks and the SQLite online backup API see committed WAL data.
        # Never copy the live DB file alone, change its pragmas, or remove sidecars.
        health = sqlite(tool, database, 'PRAGMA query_only=ON;\nPRAGMA quick_check;\nPRAGMA journal_mode;')
        if len(health) != 2 or health[0] != 'ok':
            raise ValueError('Source integrity failed; preserve previous backup')
        with tempfile.TemporaryDirectory(prefix='candidate-', dir=folder) as temp:
            candidate = safe_file(Path(temp) / 'backup.db')
            sqlite(tool, database, '.backup ' + json.dumps(candidate.as_posix(), ensure_ascii=False))
            checked = sqlite(tool, candidate, 'PRAGMA integrity_check;\nSELECT COUNT(*) FROM commands;')
            if len(checked) != 2 or checked[0] != 'ok' or not checked[1].isdigit():
                raise ValueError('Backup integrity/schema failed; preserve previous backup')
            current = {'checked_at': datetime.now(timezone.utc).isoformat(),
                       'sha256': digest(candidate), 'bytes': candidate.stat().st_size,
                       'commands': int(checked[1]), 'integrity': 'ok',
                       'sqlite_version': match.group(0), 'sqlite_sha256': tool_sha256,
                       'source_journal_mode': health[1]}
            if receipt.get('current', {}).get('sha256') == current['sha256']:
                return {'status': 'unchanged', **receipt['current'],
                        'verified_at': current['checked_at'],
                        'previous_retained': bool(receipt.get('previous')),
                        'source_opened_readonly': True, 'automatic_restore': False}
            # Failed collection/validation never rotates a good recovery point.
            previous = receipt.get('current')
            if previous:
                atomic(safe(folder, 'previous.db'), safe(folder, 'current.db').read_bytes())
            atomic(safe(folder, 'current.db'), candidate.read_bytes())
            save_json(safe(folder, 'receipt.json'), {'current': current, 'previous': previous})
            return {'status': 'pass', **current, 'previous_retained': bool(previous),
                    'source_opened_readonly': True, 'automatic_restore': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--sqlite', type=Path, required=True)
    parser.add_argument('--sqlite-sha256', required=True)
    parser.add_argument('--home', type=Path)
    parser.add_argument('--state', type=Path)
    args = parser.parse_args()
    try:
        result = backup(args.database, args.sqlite, args.sqlite_sha256,
                        Deployment(home=args.home, state=args.state).state)
    except (OSError, ValueError, subprocess.SubprocessError):
        print(json.dumps({'status': 'failed', 'error': 'RTK backup unavailable; retain previous recovery point'}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
