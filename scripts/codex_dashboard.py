"""Opt-in read-only Codex dashboard. No models, transcripts, disk crawl or scheduler."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
import tomllib
from urllib.parse import urlsplit
import uuid

from setup import ROOT, Deployment, atomic
from rtk_dashboard import Collector, DashboardServer, Handler, safe_file

INTERVAL = 10


def read_document(path, kind='json'):
    """Bounded known metadata only; unavailable is never an empty healthy record."""
    try:
        path = safe_file(path)
        with path.open('rb') as stream:
            raw = stream.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError('Metadata too large')
        text = raw.decode('utf-8-sig')
        result = tomllib.loads(text) if kind == 'toml' else json.loads(text)
        if not isinstance(result, dict):
            raise ValueError('Metadata must be an object')
        return result, None
    except (OSError, ValueError, TypeError):
        return {}, 'unavailable'


def text(value):
    return value[:200] if isinstance(value, str) else None


def schedule_label(value):
    try:
        fields = dict(part.split('=', 1) for part in value.removeprefix('RRULE:').split(';'))
        if fields.get('FREQ') == 'DAILY' and set(fields) <= {'FREQ', 'BYHOUR', 'BYMINUTE', 'INTERVAL'} and fields.get('INTERVAL', '1') == '1':
            hour, minute = int(fields['BYHOUR']), int(fields['BYMINUTE'])
            if 0 <= hour < 24 and 0 <= minute < 60:
                return f'매일 {hour:02}:{minute:02}'
    except (AttributeError, ValueError, KeyError):
        pass
    return '사용자 지정 일정 · 앱에서 확인' if value else None


def local_link(value):
    if not isinstance(value, str):
        return None
    try:
        url = urlsplit(value)
        if url.scheme == 'http' and url.hostname == '127.0.0.1' and url.port and 0 < url.port < 65536 and url.path in ('', '/') and not (url.query or url.fragment or url.username or url.password):
            return f'http://127.0.0.1:{url.port}/'
    except ValueError:
        pass
    return None


class Projection:
    def __init__(self, deployment, rtk=None, clock=time.monotonic):
        self.deployment = deployment
        self.rtk = rtk or Collector(deployment.home, deployment.state / 'reports')
        self.clock, self.lock = clock, threading.Lock()
        self.cached, self.checked = None, None
        self.last_rtk = None

    def snapshot(self):
        with self.lock:
            tick = self.clock()
            if self.cached is not None and tick - self.checked < INTERVAL:
                return self.cached
            self.cached = self.collect()
            self.checked = tick
            return self.cached

    def collect(self):
        dep, issues = self.deployment, []
        home, state = dep.home, dep.state

        def load(name, folder=state, kind='json'):
            data, error = read_document(folder / name, kind)
            if error:
                issues.append(name)
            return data, error

        routine, routine_error = load('routine-review.json')
        installed, installed_error = load('installed.json')
        sources, sources_error = load('source-report.json')
        release, release_error = load('release-verification.json')
        closure, _ = load('closure-report.json')
        config, config_error = load('config.toml', home, 'toml')
        manifest, _ = load('manifest.json', dep.source)
        lock, lock_error = load('versions.lock.json', dep.source)
        automation, auto_error = load('automations/trace/automation.toml', home, 'toml')
        agents = config.get('agents', {})
        if not isinstance(agents, dict):
            agents = {}
        owned = installed.get('files', {})
        matches, mismatches = [], []
        if isinstance(owned, dict):
            for key, row in owned.items():
                try:
                    if key == 'config.toml':
                        expected = installed.get('agent_settings', {})
                        ok = bool(expected) and all(agents.get(k) == v for k, v in expected.items())
                    else:
                        ok = hashlib.sha256(safe_file(dep.path(key)).read_bytes()).hexdigest() == row['sha256']
                    (matches if ok else mismatches).append(key)
                except (OSError, ValueError, KeyError, TypeError):
                    mismatches.append(key)
        explorer, explorer_error = load('agents/explorer.toml', home, 'toml')
        pony = next((s for s in lock.get('skills', []) if s.get('name') == 'ponytail'), {})
        skill = dep.personal_skills / 'ponytail/SKILL.md'
        try:
            pony_matches = hashlib.sha256(safe_file(skill).read_bytes()).hexdigest() == pony['files']['SKILL.md']
        except (OSError, ValueError, KeyError):
            pony_matches = None
        try:
            policy = safe_file(dep.personal_skills / 'ponytail/agents/openai.yaml').read_text(encoding='utf-8')
            explicit_only = bool(re.fullmatch(r'\s*policy:\s*\n\s+allow_implicit_invocation:\s*false\s*', policy))
        except (OSError, ValueError):
            explicit_only = None
        try:
            aggregate = self.rtk.snapshot()
            self.last_rtk = {k: aggregate.get(k) for k in ('collected_at', 'summary', 'daily', 'probe', 'arithmetic_difference', 'rtk_record_date_basis', 'history_scope')}
            rtk_status = 'live'
        except (RuntimeError, OSError, ValueError, KeyError, TypeError):
            if self.last_rtk is None:
                saved, _ = read_document(state / 'reports/rtk-efficiency.json')
                self.last_rtk = {k: saved.get(k) for k in ('collected_at', 'summary', 'daily', 'probe', 'arithmetic_difference', 'rtk_record_date_basis', 'history_scope')}
            rtk_status = 'stale' if self.last_rtk.get('collected_at') else 'unavailable'
        rtk = {**self.last_rtk, 'status': rtk_status, 'openai_usage_measured': False,
               'scope': 'TRACE private history including validation calls; earlier shared history is not added.' if self.last_rtk.get('history_scope') == 'trace-private' else 'Shared local RTK history; may include Claude, Codex, fixtures and other versions.'}
        rtk['daily'] = rtk.get('daily')[-90:] if isinstance(rtk.get('daily'), list) else []
        findings = routine.get('unresolved_findings', {})
        rows = sources.get('results')
        data = {
            'schema_version': 1,
            'installation': {'version': text(installed.get('version')), 'source_version': text(manifest.get('version')),
                             'owned_total': len(owned) if owned and not installed_error else None,
                             'matched': len(matches) if owned and not installed_error else None,
                             'mismatch_count': len(mismatches) if owned and not installed_error else None,
                             'last_verified_at': text(routine.get('last_verification', {}).get('checked_at')),
                             'verification_scope': 'Current file fingerprints, not a fresh full lifecycle or session test.'},
            'routine': {'status': None if auto_error else text(automation.get('status')),
                        'schedule': None if auto_error else schedule_label(automation.get('rrule')),
                        'last_source_collection': text(routine.get('last_source_collection')),
                        'last_review': text(routine.get('last_substantive_review')),
                        'last_application': text(routine.get('last_policy_application')),
                        'last_successful_collection': text(routine.get('last_successful_collection')),
                        'last_project_scan': text(routine.get('maintenance_cadence', {}).get('last_project_scan')),
                        'cadence': text(routine.get('maintenance_cadence', {}).get('policy')),
                        'source_count': len(rows) if isinstance(rows, list) else None,
                        'source_success': sum(row.get('status') == 'fetched' for row in rows) if isinstance(rows, list) else None,
                        'pending_count': len(sources['pending']) if isinstance(sources.get('pending'), list) else None,
                        'source_checked_at': text(sources.get('checked_at'))},
            'agents': {'parent_model_default': text(config.get('model')), 'parent_effort_default': text(config.get('model_reasoning_effort')),
                       'child_model': text(agents.get('default_subagent_model')), 'child_effort': text(agents.get('default_subagent_reasoning_effort')),
                       'max_children': agents.get('max_concurrent_threads_per_session') if type(agents.get('max_concurrent_threads_per_session')) is int else None,
                       'explorer_model': text(explorer.get('model')), 'explorer_effort': text(explorer.get('model_reasoning_effort')),
                       'live_count': None, 'invocations': None, 'config_available': not config_error,
                       'explorer_available': not explorer_error, 'read_only_isolation_enforced': False},
            'ponytail': {'available': skill.is_file(), 'pinned_hash_matches': pony_matches, 'explicit_only': explicit_only,
                         'version': text(pony.get('version')), 'commit': text(pony.get('commit')),
                         'invocations': None, 'measured_savings': None},
            'rtk': rtk,
            'publication': {'status': text(release.get('status')), 'tag': text(release.get('tag')),
                            'checked_at': text(release.get('checked_at')), 'commit': text(release.get('commit'))},
            'runtime': {'cli_last_observed': text(closure.get('cli')), 'checked_at': text(closure.get('checked_at'))},
            'links': {'disk_map': local_link(routine.get('dashboard_links', {}).get('disk_map'))},
            'findings': [{'id': text(k), 'status': text(v.get('status'))} for k, v in list(findings.items())[:30]] if isinstance(findings, dict) else [],
            'unavailable_sources': issues,
            'actual_openai_tokens': None, 'actual_cache_hit_rate': None,
        }
        comparable = {**data, 'rtk': {k: v for k, v in rtk.items() if k != 'collected_at'}}
        data['revision'] = hashlib.sha256(json.dumps(comparable, sort_keys=True).encode()).hexdigest()
        data['observed_at'] = datetime.now(timezone.utc).isoformat()
        return data


class CodexHandler(Handler):
    content_security_policy = Handler.content_security_policy + "; img-src 'self' data:"

    def do_GET(self):
        authority = f'127.0.0.1:{self.server.server_port}'
        if self.headers.get('Host') != authority or self.headers.get('Origin') not in (None, 'http://' + authority) or self.headers.get('Sec-Fetch-Site') == 'cross-site':
            return self.send_body(403, b'{"error":"Access refused"}', 'application/json')
        parsed = urlsplit(self.path)
        if parsed.query or parsed.fragment or parsed.scheme or parsed.netloc:
            return self.send_body(404, b'{"error":"Not found"}', 'application/json')
        try:
            if parsed.path == '/favicon.ico':
                return self.send_body(204, b'', 'image/x-icon')
            if parsed.path == '/api/health':
                return self.send_body(200, json.dumps({'viewer': 'TRACE Codex dashboard', 'instance_id': self.server.instance_id, 'pid': os.getpid()}).encode(), 'application/json')
            if parsed.path == '/api/dashboard':
                return self.send_body(200, json.dumps(self.server.collector.snapshot(), ensure_ascii=False).encode(), 'application/json; charset=utf-8')
            if parsed.path in ('/', '/codex-dashboard.html'):
                template = safe_file(self.server.source / 'templates/reports/codex-dashboard.template.html').read_text(encoding='utf-8')
                if template.count('__CODEX_DASHBOARD_DATA__') != 1:
                    raise ValueError('Invalid template')
                payload = json.dumps(self.server.collector.snapshot(), ensure_ascii=False).replace('</', '<\\/')
                return self.send_body(200, template.replace('__CODEX_DASHBOARD_DATA__', payload).encode(), 'text/html; charset=utf-8')
            assets = {'/assets/dashboard.css': ('codex-dashboard.css', 'text/css; charset=utf-8'),
                      '/assets/PretendardVariable.woff2': ('assets/PretendardVariable.woff2', 'font/woff2')}
            if parsed.path in assets:
                name, mime = assets[parsed.path]
                return self.send_body(200, safe_file(self.server.source / 'templates/reports' / name).read_bytes(), mime)
            return self.send_body(404, b'{"error":"Not found"}', 'application/json')
        except Exception:
            return self.send_body(503, b'{"error":"Metadata unavailable; retain previous display"}', 'application/json')


def make_server(deployment, port=0, collector=None):
    server = DashboardServer(('127.0.0.1', port), CodexHandler)
    server.source = deployment.source
    server.instance_id = uuid.uuid4().hex
    server.collector = collector or Projection(deployment)
    return server


def write_ready(path, value):
    path = safe_file(path)
    if path.exists():
        old, error = read_document(path)
        if error or old.get('viewer') != 'TRACE Codex dashboard' or not re.fullmatch(r'[0-9a-f]{32}', old.get('instance_id', '')):
            raise ValueError('Unmanaged readiness file refused')
    atomic(path, (json.dumps(value) + '\n').encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path)
    parser.add_argument('--state', type=Path)
    parser.add_argument('--personal-skills', type=Path)
    parser.add_argument('--port', type=int, default=47812)
    parser.add_argument('--ready-file', type=Path)
    args = parser.parse_args()
    server = None
    try:
        dep = Deployment(home=args.home, state=args.state, personal_skills=args.personal_skills)
        (dep.state / 'reports').mkdir(parents=True, exist_ok=True)
        server = make_server(dep, args.port)
        ready = {'viewer': 'TRACE Codex dashboard', 'url': f'http://127.0.0.1:{server.server_port}/',
                 'pid': os.getpid(), 'instance_id': server.instance_id, 'poll_interval_ms': INTERVAL * 1000}
        write_ready(args.ready_file or dep.state / 'reports/codex-dashboard-ready.json', ready)
        print(json.dumps(ready), flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    except Exception:
        print('{"status":"failed","error":"Dashboard unavailable or port in use"}', flush=True)
        return 1
    finally:
        if server:
            server.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
