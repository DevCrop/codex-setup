"""Owner-native installed-plugin refresh and bounded global skill inventory."""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess

from setup import Deployment, read_json, save_json, deployment_lock
from rtk_dashboard import safe_file

POLICY = 'reviewed-existing-software-v1'


def native(cli, args, run=subprocess.run):
    result = run([cli, 'plugin', *args], capture_output=True, text=True,
                 encoding='utf-8', timeout=120)
    if result.returncode or len(result.stdout) > 8_000_000:
        raise ValueError('Native plugin owner operation failed; raw output withheld')
    return json.loads(result.stdout)


def installed(cli, run=subprocess.run):
    rows = native(cli, ['list', '--json'], run).get('installed')
    if not isinstance(rows, list) or len(rows) > 1000:
        raise ValueError('Installed plugin inventory unavailable')
    identities = [r.get('pluginId') for r in rows]
    if len(set(identities)) != len(rows) or any(not isinstance(k, str) or
            not re.fullmatch(r'[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+', k) for k in identities):
        raise ValueError('Invalid plugin identity')
    return rows


def safe_component(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+', value) or value in ('.', '..'):
        raise ValueError('Invalid package path component')
    return value


def skill_files(root):
    root = safe_file(root)
    if not root.is_dir():
        raise ValueError('Skill root unavailable')
    result, visited = [], 0
    for directory, dirs, files in os.walk(root, followlinks=False):
        visited += 1
        if visited > 3000:
            raise ValueError('Skill metadata tree exceeds budget')
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__')
                   and not (Path(directory)/d).is_symlink()
                   and not (getattr((Path(directory)/d).lstat(), 'st_file_attributes', 0) & 0x400)]
        if 'SKILL.md' in files:
            p = safe_file(Path(directory)/'SKILL.md')
            with p.open('rb') as stream:
                raw = stream.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ValueError('Skill metadata file exceeds budget')
            result.append({'name': p.parent.name, 'sha256': hashlib.sha256(raw).hexdigest()})
    return sorted(result, key=lambda r: (r['name'], r['sha256']))


def plugin_root(dep, row):
    source = row.get('source', {})
    if source.get('source') == 'local':
        return safe_file(source['path'])
    # This layout is verified on this client, not an installation/write contract.
    # A different owner layout is unavailable, never permission to search caches.
    return safe_file(dep.home/'plugins/cache'/safe_component(row['marketplaceName'])/
                     safe_component(row['name'])/safe_component(row['version']))


def summarize(dep, rows):
    plugins = []
    for row in rows:
        item = {k: row.get(k) for k in ('pluginId', 'name', 'marketplaceName', 'version', 'enabled', 'authPolicy')}
        try:
            root = plugin_root(dep, row)
            manifest = json.loads((safe_file(root/'.codex-plugin/plugin.json')).read_text(encoding='utf-8'))
            skills = skill_files(root/'skills') if (root/'skills').is_dir() else []
            item.update(manifest_matches=manifest.get('version') == row.get('version'),
                        display_name=manifest.get('interface', {}).get('displayName') or row.get('name'),
                        skill_count=len(skills), skill_fingerprints=skills, status='observed')
            if not item['manifest_matches']:
                item['status'] = 'version-conflict'
        except (OSError, ValueError, KeyError, TypeError):
            item.update(status='unavailable', manifest_matches=None, skill_count=None)
        plugins.append(item)
    local = []
    for label, root in [('personal', dep.personal_skills), ('system', dep.home/'skills/.system')]:
        try:
            files = skill_files(root)
            local.append({'scope':label, 'status':'observed', 'skills':files, 'count':len(files)})
        except (OSError, ValueError):
            local.append({'scope':label, 'status':'unavailable', 'count':None})
    return {'plugins':plugins, 'local_skills':local,
            'plugin_count':len(plugins), 'enabled_count':sum(p['enabled'] is True for p in plugins),
            'skill_count':sum(p.get('skill_count') or 0 for p in plugins)+sum(r.get('count') or 0 for r in local),
            'unavailable_count':sum(p['status'] != 'observed' for p in plugins)+sum(r['status'] != 'observed' for r in local)}


def allowed(routine, host=None):
    auth = routine.get('maintenance_authorization', {}).get('software_updates', {})
    return (auth.get('policy') == POLICY and auth.get('automation_id') == 'trace'
            and auth.get('host_identity') == (host or platform.node()) and bool(auth.get('approved_on')))


def protected_settings(dep):
    import tomllib
    config = tomllib.loads((dep.home/'config.toml').read_text(encoding='utf-8-sig'))
    selected = {k:config.get(k) for k in ('model', 'model_reasoning_effort', 'approval_policy', 'sandbox_mode',
                                        'permissions', 'mcp_servers', 'hooks', 'agents')}
    return hashlib.sha256(json.dumps(selected, sort_keys=True, default=str).encode()).hexdigest()


def refresh(dep, cli, routine, rows, run=subprocess.run, now=None):
    now = now or datetime.now(timezone.utc)
    if not allowed(routine):
        raise ValueError('Exact host software-update authority required')
    auth = routine['maintenance_authorization']['software_updates']
    enrolled = set(auth.get('installed_plugin_ids', []))
    old = routine.get('software_updates', {})
    fresh = dict(old.get('owner_checks', {}))
    old_inventory = {p['pluginId']:p for p in old.get('inventory', {}).get('plugins', [])}
    current_inventory = {p['pluginId']:p for p in summarize(dep, rows)['plugins']}
    protected = protected_settings(dep)
    expected = {r['pluginId']:r.get('enabled') for r in rows}
    outcomes = []
    for row in rows:
        key = row['pluginId']
        if key not in enrolled:
            outcomes.append({'pluginId':key,'status':'new-identity-needs-review'})
            continue
        if not row.get('enabled'):
            outcomes.append({'pluginId':key,'status':'disabled-preserved'})
            continue
        if row.get('source', {}).get('source') == 'local':
            # App/runtime owns the available source; do not reinstall unchanged payloads.
            outcomes.append({'pluginId':key,'status':'owner-source','version':row.get('version')})
            continue
        previous = fresh.get(key, {})
        try:
            recent = datetime.fromisoformat(previous['checked_at']) > now-timedelta(hours=24)
        except (KeyError, TypeError, ValueError):
            recent = False
        unchanged_content = (current_inventory[key].get('status') == 'observed' and
            current_inventory[key].get('skill_fingerprints') == old_inventory.get(key, {}).get('skill_fingerprints'))
        if recent and previous.get('version') == row.get('version') and unchanged_content:
            outcomes.append({'pluginId':key,'status':'reused-current-owner-check','version':row['version']})
            continue
        try:
            result = native(cli, ['add', key, '--json'], run)
            if result.get('pluginId') != key or result.get('authPolicy') != row.get('authPolicy'):
                raise ValueError('Owner identity/auth policy changed; review required')
            manifest_path = safe_file(Path(result['installedPath'])/'.codex-plugin/plugin.json')
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            if manifest.get('version') != result.get('version'):
                raise ValueError('Owner receipt and installed manifest differ')
            fresh[key] = {'version':result['version'],'checked_at':now.isoformat(),
                          'manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest()}
            outcomes.append({'pluginId':key,'status':'owner-verified','before':row.get('version'),
                             'version':result['version'],'changed':row.get('version') != result['version']})
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
            outcomes.append({'pluginId':key,'status':'failed-preserved','action':'Inspect native owner response; do not retry unchanged or edit cache'})
            break
    after = installed(cli, run)
    if {r['pluginId']:r.get('enabled') for r in after} != expected or protected_settings(dep) != protected:
        raise ValueError('Protected settings or enabled/plugin scope changed; preserve and inspect owner result')
    last_owner_refresh=max((v.get('checked_at','') for v in fresh.values()),default=None)
    return {'owner_checks':fresh,'outcomes':outcomes,'inventory':summarize(dep, after),
            'last_owner_refresh':last_owner_refresh,'last_verification':now.isoformat(),
            'status':'attention' if any(r['status'] in ('failed-preserved','new-identity-needs-review') for r in outcomes) else 'verified'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['collect','refresh-plugins'])
    for flag in ('home','state','personal-skills'):
        parser.add_argument('--'+flag,type=Path)
    parser.add_argument('--codex',help='Explicit supported Codex CLI executable; otherwise command discovery')
    args=parser.parse_args()
    dep=Deployment(home=args.home,state=args.state,personal_skills=args.personal_skills)
    cli=args.codex or shutil.which('codex')
    if not cli:
        raise ValueError('Codex CLI unavailable')
    path=dep.state/'routine-review.json'
    with deployment_lock(dep.state):
        routine=read_json(path,{})
        now=datetime.now(timezone.utc).isoformat()
        try:
            rows=installed(cli)
            if args.command=='refresh-plugins':
                result=refresh(dep,cli,routine,rows)
            else:
                result={**routine.get('software_updates',{}),'inventory':summarize(dep,rows)}
        except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError):
            current=read_json(path,{})
            current['software_updates']={**current.get('software_updates',{}),'status':'failed',
                'last_attempt':now,'error':'Native owner/inventory operation failed; inspect current state before retry'}
            save_json(path,current)
            print(json.dumps({'status':'failed','previous_evidence_retained':True}))
            return 1
        result['last_inventory_collection']=now
        if result['inventory']['unavailable_count']:
            result['status']='attention'
        current=read_json(path,{})
        current['software_updates']=result
        result['last_attempt']=now
        if result.get('status') == 'verified' and not result['inventory']['unavailable_count']:
            result['last_successful_owner_refresh']=result.get('last_owner_refresh')
        save_json(path,current)
    print(json.dumps({'status':result.get('status','collected'),'plugin_count':result['inventory']['plugin_count'],
                      'skill_count':result['inventory']['skill_count'],'unavailable_count':result['inventory']['unavailable_count'],
                      'outcomes':result.get('outcomes',[])},ensure_ascii=False))
    return 1 if result.get('status')=='attention' or result['inventory']['unavailable_count'] else 0


if __name__=='__main__':
    raise SystemExit(main())
