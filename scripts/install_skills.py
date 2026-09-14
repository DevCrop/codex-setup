#!/usr/bin/env python3
"""Install pinned upstream skills through the official helper; never overwrite."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def linked(path):
    return path.is_symlink() or (path.exists() and bool(getattr(path.lstat(), 'st_file_attributes', 0) & 0x400))


def hashes(directory):
    result = {}
    for path in sorted(directory.rglob('*')):
        if linked(path):
            raise ValueError('Skill contains a symbolic link: ' + str(path))
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home', type=Path)
    parser.add_argument('--check', action='store_true', help='Verify existing installations without network access')
    args = parser.parse_args()
    home = (args.codex_home or Path(os.environ.get('CODEX_HOME', Path.home() / '.codex'))).expanduser().absolute()
    if not home.is_dir() or any(linked(p) for p in [home, *home.parents]):
        raise ValueError('Codex home must be an existing real directory')
    if linked(home / 'skills'):
        raise ValueError('Refusing linked skills directory')
    helper = home / 'skills/.system/skill-installer/scripts/install-skill-from-github.py'
    lock = json.loads((Path(__file__).resolve().parents[1] / 'versions.lock.json').read_text(encoding='utf-8'))
    output = []
    for skill in lock['skills']:
        destination = home / 'skills' / skill['name']
        if linked(destination):
            raise ValueError('Refusing linked skill destination')
        if destination.exists():
            if not destination.is_dir() or hashes(destination) != skill['files']:
                raise ValueError('Existing skill differs from pinned files; preserve and resolve conflict: ' + skill['name'])
            output.append({'skill': skill['name'], 'status': 'verified', 'files': len(skill['files'])})
            continue
        if args.check:
            raise ValueError('Missing skill: ' + skill['name'])
        if not helper.is_file():
            raise ValueError('Install the official skill-installer system skill first')
        # Same-filesystem staging permits an atomic directory rename. The helper
        # handles temporary download cleanup; this context removes our staging.
        with tempfile.TemporaryDirectory(prefix='.trace-skill-', dir=home / 'skills') as staging:
            subprocess.run([sys.executable, str(helper), '--repo', skill['repository'],
                            '--path', skill['path'], '--ref', skill['commit'],
                            '--name', skill['name'], '--dest', staging], check=True)
            candidate = Path(staging) / skill['name']
            if hashes(candidate) != skill['files']:
                raise ValueError('Downloaded files differ from reviewed lock: ' + skill['name'])
            if destination.exists():
                raise ValueError('Skill appeared during installation; refusing overwrite')
            candidate.rename(destination)
        output.append({'skill': skill['name'], 'status': 'installed', 'files': len(skill['files'])})
    print(json.dumps({'ok': True, 'skills': output}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}), file=sys.stderr)
        sys.exit(1)
