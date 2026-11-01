"""Install/verify the optional Codex-only desktop skill; leave global/Claude config alone."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import urllib.request

from setup import Deployment, ROOT, atomic, default_state, deployment_lock, read_json, safe, save_json


SOURCE = ROOT / 'components/agent-desktop'


class SkillDeployment(Deployment):
    """Reuse owned lifecycle for one skill root, with no agent/config ownership."""
    def desired(self):
        return {entry['target']: safe(self.source, entry['source']).read_bytes()
                for entry in self.manifest['files']}


def locations(home):
    home = Path(home).expanduser().absolute()
    state = default_state(home) / 'components/agent-desktop'
    # Validate every ancestor, not just existing leaf files.
    safe(home, 'skills/codex-agent-desktop/SKILL.md')
    safe(state, 'runtime.json')
    return home, state


def deployment(home, state, source=SOURCE):
    return SkillDeployment(source, home / 'skills/codex-agent-desktop', state,
                           state / 'unused-personal-skill-root')


def checked_binary(data, pin):
    if hashlib.sha256(data).hexdigest() != pin['binary_sha256']:
        raise ValueError('Pinned native binary hash mismatch')
    return data


def download(pin):
    with urllib.request.urlopen(pin['url'], timeout=45) as response:
        archive = response.read(8 * 1024 * 1024 + 1)
    if len(archive) > 8 * 1024 * 1024 or hashlib.sha256(archive).hexdigest() != pin['archive_sha256']:
        raise ValueError('Release archive size/hash mismatch')
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as bundle:
        members = bundle.getmembers()
        if len(members) != 1 or members[0].name != 'agent-desktop.exe' or not members[0].isfile() or members[0].size > 16 * 1024 * 1024:
            raise ValueError('Unexpected native archive contents')
        return checked_binary(bundle.extractfile(members[0]).read(), pin)


def verify_runtime(home, state, pin):
    record = read_json(safe(state, 'runtime.json'), {})
    binary = safe(state, 'runtime/agent-desktop.exe')
    if record.get('owner') != 'TRACE Codex agent-desktop' or record.get('home') != str(home) or record.get('path') != str(binary):
        raise ValueError('Runtime ownership mismatch')
    data = checked_binary(binary.read_bytes(), pin)
    if record.get('sha256') != hashlib.sha256(data).hexdigest() or record.get('version') != pin['version']:
        raise ValueError('Runtime receipt differs from reviewed pin')
    return {'status': 'pass', 'version': record['version'], 'sha256': record['sha256']}


def install_runtime(home, state, pin, binary_source=None):
    binary = safe(state, 'runtime/agent-desktop.exe')
    receipt = safe(state, 'runtime.json')
    journal = safe(state, 'runtime-pending.json')
    expected = {'owner': 'TRACE Codex agent-desktop', 'home': str(home),
                'version': pin['version'], 'path': str(binary),
                'sha256': pin['binary_sha256'], 'source': pin['url'],
                'archive_sha256': pin['archive_sha256']}
    pending = read_json(journal)
    if pending is not None and pending != expected:
        raise ValueError('Runtime journal conflict')
    if binary.exists() and receipt.exists() and pending is None:
        return verify_runtime(home, state, pin)
    if (binary.exists() or receipt.exists()) and pending is None:
        raise ValueError('Unowned/incomplete runtime; no matching journal, preserve and inspect')
    if receipt.exists() and read_json(receipt) != expected:
        raise ValueError('Runtime receipt changed during interrupted installation')
    data = checked_binary(binary.read_bytes(), pin) if binary.exists() else (
        checked_binary(Path(binary_source).read_bytes(), pin) if binary_source else download(pin))
    if pending is None:
        save_json(journal, expected)
    if not binary.exists():
        atomic(binary, data)
    if not receipt.exists():
        save_json(receipt, expected)
    result = verify_runtime(home, state, pin)
    # Only the exact journal created by this owned transaction is retired.
    if read_json(journal) != expected:
        raise ValueError('Concurrent runtime journal change')
    journal.unlink()
    return result


def install(home, state, binary_source=None, source=SOURCE):
    dep = deployment(home, state, source)
    if any(row['action'] == 'conflict' for row in dep.plan()):
        raise ValueError('User-modified skill conflict; nothing installed')
    pin = dep.manifest['upstream']
    install_runtime(home, state, pin, binary_source)
    result = dep.apply()
    result['runtime'] = verify_runtime(home, state, pin)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'install', 'verify', 'rollback', 'recover', 'uninstall'])
    parser.add_argument('--home', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')))
    parser.add_argument('--binary', type=Path, help='Reuse an exact reviewed binary instead of downloading')
    args = parser.parse_args()
    if os.name != 'nt' or platform.machine().lower() not in ('amd64', 'x86_64'):
        raise ValueError('This integration is reviewed only for native Windows x64')
    home, state = locations(args.home)
    with deployment_lock(state):
        dep = deployment(home, state)
        if args.command == 'install':
            result = install(home, state, args.binary)
        elif args.command == 'verify':
            result = dep.verify()
            result['runtime'] = verify_runtime(home, state, dep.manifest['upstream'])
        elif args.command == 'recover':
            runtime_pending = safe(state, 'runtime-pending.json').exists()
            if runtime_pending:
                if not safe(state, 'runtime/agent-desktop.exe').exists():
                    raise ValueError('Interrupted before binary write; run install to complete the pinned runtime')
                install_runtime(home, state, dep.manifest['upstream'])
            if safe(state, 'pending.json').exists():
                result = dep.restore('pending.json')
            elif runtime_pending:
                result = {'status': 'runtime-recovered', 'next': 'Run install to complete/verify the skill'}
            else:
                raise ValueError('No pending component transaction')
        elif args.command == 'rollback':
            result = dep.restore('previous.json')
        else:
            result = getattr(dep, args.command)()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int((isinstance(result, dict) and result.get('status') == 'fail')
               or (isinstance(result, list) and any(row['action'] == 'conflict' for row in result)))


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
