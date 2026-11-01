"""Opt-in TRACE health/drift/recovery checks. Never changes live user settings."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import platform
import queue
import secrets
import shutil
import subprocess
import tempfile
import threading
import time
import tomllib
import urllib.error
import urllib.request

from setup import Deployment, digest, read_json, safe, save_json

POLICY = 'paths-mcp-drift-monthly-recovery-v1'
SETTING_KEYS = ('model', 'model_reasoning_effort', 'approval_policy', 'sandbox_mode')
PROBE_PROTOCOL = '2025-11-25'
LEGACY_PROTOCOLS = ('2025-03-26', '2025-06-18', PROBE_PROTOCOL)
MODERN_PROTOCOL = '2026-07-28'
METADATA_LIMIT = 1048576
PROBE_VALIDATOR = 'bounded-metadata-v2'


def rpc_result(reply, request_id):
    """Accept only a matching successful JSON-RPC response, never a notification."""
    if (not isinstance(reply, dict) or reply.get('jsonrpc') != '2.0'
            or type(reply.get('id')) is not int or reply['id'] != request_id
            or 'error' in reply or 'method' in reply
            or not isinstance(reply.get('result'), dict)):
        return None
    return reply['result']


def initialize_result(reply):
    result = rpc_result(reply, 1)
    if (result is None or result.get('protocolVersion') not in LEGACY_PROTOCOLS
            or result.get('resultType', 'complete') != 'complete'):
        return None
    info = result.get('serverInfo')
    if (not isinstance(result.get('capabilities'), dict) or not isinstance(info, dict)
            or not all(isinstance(info.get(k), str) for k in ('name', 'version'))):
        return None
    return result


def modern_params():
    return {'_meta': {'io.modelcontextprotocol/protocolVersion': MODERN_PROTOCOL,
                     'io.modelcontextprotocol/clientCapabilities': {},
                     'io.modelcontextprotocol/clientInfo': {'name': 'TRACE-readonly-health', 'version': '1'}}}


def cache_metadata(result):
    return (type(result.get('ttlMs')) in (int, float) and result['ttlMs'] >= 0
            and result.get('cacheScope') in ('public', 'private'))


def discover_result(reply):
    result = rpc_result(reply, 0)
    if (result is None or result.get('resultType') != 'complete'
            or not isinstance(result.get('supportedVersions'), list)
            or not result['supportedVersions']
            or not all(isinstance(v, str) for v in result['supportedVersions'])
            or not isinstance(result.get('capabilities'), dict) or not cache_metadata(result)):
        return None
    return result


def rpc_error(reply, request_id):
    if (not isinstance(reply, dict) or reply.get('jsonrpc') != '2.0'
            or type(reply.get('id')) is not int or reply['id'] != request_id
            or 'result' in reply or 'method' in reply):
        return None
    error = reply.get('error')
    if not isinstance(error, dict) or type(error.get('code')) is not int or not isinstance(error.get('message'), str):
        return None
    return error


def tools_result(reply, modern=False):
    result = rpc_result(reply, 2)
    if result is None or not isinstance(result.get('tools'), list):
        return None
    if result.get('resultType', 'complete') != 'complete':
        return None
    if modern and (result.get('resultType') != 'complete' or not cache_metadata(result)):
        return None
    for tool in result['tools']:
        if (not isinstance(tool, dict) or not isinstance(tool.get('name'), str)
                or not isinstance(tool.get('inputSchema'), dict)
                or tool['inputSchema'].get('type') != 'object'):
            return None
    if 'nextCursor' in result and not isinstance(result['nextCursor'], str):
        return None
    return result


def bounded_http_body(response, deadline):
    raw = bytearray()
    while time.monotonic() < deadline:
        chunk = response.read1(min(65536, METADATA_LIMIT + 1 - len(raw)))
        if not chunk:
            return raw
        raw.extend(chunk)
        if len(raw) > METADATA_LIMIT:
            raise OverflowError
    raise TimeoutError('Metadata deadline exceeded')


def http_initialize_reply(response, deadline, request_id=1):
    """Read bounded metadata; SSE completes at the matching event, without EOF.

    read1 performs at most one socket read, so live keep-alive streams return
    available events immediately. The caller's socket timeout also bounds a
    stalled read; the deadline prevents continuing an indefinitely active stream.
    """
    content_type = response.headers.get('Content-Type', '').split(';', 1)[0].strip().lower()
    if content_type == 'application/json':
        return json.loads(bounded_http_body(response, deadline))
    if content_type != 'text/event-stream':
        raise ValueError('Unsupported response content type')
    pending = b''
    data = []
    total = 0
    skip_lf = False
    while time.monotonic() < deadline:
        chunk = response.read1(min(65536, METADATA_LIMIT + 1 - total))
        if not chunk:
            raise ValueError('No matching complete SSE response')
        total += len(chunk)
        if total > METADATA_LIMIT:
            raise OverflowError
        pending += chunk
        # SSE uses CRLF, LF or CR line endings, including split CRLF chunks.
        while pending:
            if skip_lf:
                if pending.startswith(b'\n'):
                    pending = pending[1:]
                skip_lf = False
                if not pending:
                    break
            positions = [i for i in (pending.find(b'\r'), pending.find(b'\n')) if i >= 0]
            if not positions:
                break
            end = min(positions)
            skip_lf = pending[end:end+1] == b'\r'
            line = pending[:end].decode('utf-8')
            pending = pending[end+1:]
            if not line:
                if data:
                    reply = json.loads('\n'.join(data))
                    data = []
                    if isinstance(reply, dict) and type(reply.get('id')) is int and reply['id'] == request_id:
                        return reply
            elif line.startswith('data:'):
                value = line[5:]
                data.append(value[1:] if value.startswith(' ') else value)
    raise TimeoutError('Metadata deadline exceeded')


def authorized(routine, host=None):
    auth = routine.get('maintenance_authorization', {})
    scope = auth.get('setup_health', {})
    return (auth.get('automation_id') == 'trace'
            and auth.get('host_identity') == (host or platform.node())
            and scope.get('automation_id') == 'trace'
            and scope.get('host_identity') == (host or platform.node())
            and scope.get('policy') == POLICY and bool(scope.get('approved_on')))


def fingerprint(value, key):
    return hmac.new(key, json.dumps(value, sort_keys=True, default=str).encode(),
                    hashlib.sha256).hexdigest()


def due(last, now, days):
    if not last:
        return True
    return now - datetime.fromisoformat(last) >= timedelta(days=days)


def inspect_binding(binding):
    source, target = Path(binding['source']), Path(binding['target'])
    try:
        try:
            source_stat = source.lstat()
        except FileNotFoundError:
            return {'name': binding['name'], 'source': str(source), 'target': str(target),
                    'status': 'source_missing_archive_present' if target.is_dir() else 'source_and_target_unavailable'}
        linked = source.is_symlink() or bool(getattr(source_stat, 'st_file_attributes', 0) & 0x400)
        okay = linked and target.is_dir() and source.resolve(strict=True) == target.resolve(strict=True)
        return {'name': binding['name'], 'source': str(source), 'target': str(target),
                'status': 'ok' if okay else 'broken_or_changed'}
    except (OSError, RuntimeError):
        return {'name': binding['name'], 'source': str(source), 'target': str(target),
                'status': 'unavailable'}


def stdio_probe(server, timeout=8, allow_modern=False):
    """Discover or initialize, then list metadata; never invoke a tool."""
    command = [server['command'], *server.get('args', [])]
    if not Path(command[0]).is_file():
        return {'status': 'missing_executable'}
    lines = queue.Queue(maxsize=64)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True, encoding='utf-8',
                               env={**os.environ, **server.get('env', {})},
                               cwd=server.get('cwd') or None,
                               creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    def reader():
        total = 0
        while True:
            line = process.stdout.readline(METADATA_LIMIT + 1)
            if not line:
                return
            total += len(line.encode('utf-8'))
            try:
                lines.put(line if total <= METADATA_LIMIT else None, timeout=timeout)
            except queue.Full:
                return
            if total > METADATA_LIMIT:
                return
    threading.Thread(target=reader, daemon=True).start()
    deadline = time.monotonic() + timeout
    try:
        initialize = {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
            'protocolVersion': PROBE_PROTOCOL, 'capabilities': {},
            'clientInfo': {'name': 'TRACE-readonly-health', 'version': '1'}}}
        def send(payload):
            process.stdin.write(json.dumps(payload) + '\n'); process.stdin.flush()

        send({'jsonrpc': '2.0', 'id': 0, 'method': 'server/discover', 'params': modern_params()}
             if allow_modern else initialize)
        discovery_deadline = time.monotonic() + min(1, timeout/3)
        phase = 'discover' if allow_modern else 'initialize'
        modern = False
        initialized = False
        while time.monotonic() < deadline:
            if phase == 'discover' and time.monotonic() >= discovery_deadline:
                send(initialize)
                phase = 'initialize'
            try:
                line = lines.get(timeout=min(.25, max(.01, deadline-time.monotonic())))
                if line is None:
                    return {'status': 'metadata_limit_unverified'}
                reply = json.loads(line)
            except (queue.Empty, json.JSONDecodeError):
                if process.poll() is not None:
                    return {'status': 'server_exited'}
                continue
            if not isinstance(reply, dict):
                continue
            if type(reply.get('id')) is not int:
                continue
            if reply.get('id') == 0 and phase == 'discover':
                error = rpc_error(reply, 0)
                if error:
                    if error['code'] in (-32020, -32021, -32022):
                        return {'status': 'modern_protocol_unverified'}
                    if error['code'] not in (-32600, -32601, -32602):
                        return {'status': 'discovery_refused'}
                    send(initialize)
                    phase = 'initialize'
                    continue
                result = discover_result(reply)
                if result is None:
                    return {'status': 'discovery_refused'}
                if MODERN_PROTOCOL not in result['supportedVersions']:
                    return {'status': 'unsupported_protocol_unverified'}
                modern = True
                if not isinstance(result['capabilities'].get('tools'), dict):
                    return {'status': 'tools_capability_unavailable'}
                send({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': modern_params()})
                phase = 'tools'
            elif reply.get('id') == 1 and phase == 'initialize':
                result = initialize_result(reply)
                if result is None:
                    return {'status': 'initialize_refused'}
                initialized = True
                process.stdin.write(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'})+'\n')
                if not isinstance(result['capabilities'].get('tools'), dict):
                    process.stdin.flush()
                    return {'status': 'tools_capability_unavailable', 'initialized': True}
                process.stdin.write(json.dumps({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}})+'\n')
                process.stdin.flush()
                phase = 'tools'
            elif reply.get('id') == 2 and phase == 'tools':
                result = tools_result(reply, modern)
                if result is None:
                    return {'status': 'tools_list_refused', 'initialized': initialized}
                return {'status': 'connected_metadata_only',
                        'tool_count': len(result['tools']),
                        'tool_count_scope': 'first_page' if 'nextCursor' in result else 'complete',
                        'protocol_era': 'modern' if modern else 'legacy'}
        return {'status': 'timeout_unverified', 'initialized': initialized}
    finally:
        try:
            process.stdin.close()
            process.wait(timeout=1)
        except (OSError, subprocess.TimeoutExpired):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=2)
        process.stdout.close()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def http_probe(server, timeout=8, allow_modern=False):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
    headers.update(server.get('http_headers', {}))
    for name, variable in server.get('env_http_headers', {}).items():
        if os.environ.get(variable):
            headers[name] = os.environ[variable]
    token = os.environ.get(server.get('bearer_token_env_var', ''))
    if token:
        headers['Authorization'] = 'Bearer ' + token
    try:
        deadline = time.monotonic() + timeout
        opener = urllib.request.build_opener(NoRedirect)

        def request(payload, modern):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Metadata deadline exceeded')
            wire_headers = {name: value for name, value in headers.items()
                            if name.lower() not in ('mcp-protocol-version', 'mcp-method')}
            if modern:
                wire_headers.update({'MCP-Protocol-Version': MODERN_PROTOCOL, 'Mcp-Method': payload['method']})
            req = urllib.request.Request(server['url'], data=json.dumps(payload).encode(), headers=wire_headers)
            with opener.open(req, timeout=remaining) as response:
                return http_initialize_reply(response, deadline, payload['id'])

        def legacy_request():
            body = request({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
                'protocolVersion': PROBE_PROTOCOL, 'capabilities': {},
                'clientInfo': {'name': 'TRACE-readonly-health', 'version': '1'}}}, False)
            return {'status': 'connected_metadata_only' if initialize_result(body) is not None else 'initialize_refused',
                    'protocol_era': 'legacy'}

        if not allow_modern:
            return legacy_request()

        try:
            body = request({'jsonrpc': '2.0', 'id': 0, 'method': 'server/discover', 'params': modern_params()}, True)
        except urllib.error.HTTPError as exc:
            if exc.code != 400:
                raise
            with exc:
                raw = bounded_http_body(exc, deadline)
            try:
                error = rpc_error(json.loads(raw), 0)
            except ValueError:
                error = None
            if error and error['code'] in (-32020, -32021, -32022):
                return {'status': 'modern_protocol_unverified'}
            if error and error['code'] not in (-32600, -32601, -32602):
                return {'status': 'discovery_refused'}
            return legacy_request()
        result = discover_result(body)
        if result is None:
            return {'status': 'discovery_refused'}
        if MODERN_PROTOCOL not in result['supportedVersions']:
            return {'status': 'unsupported_protocol_unverified'}
        return {'status': 'connected_metadata_only', 'protocol_era': 'modern'}
    except OverflowError:
        return {'status': 'metadata_limit_unverified'}
    except urllib.error.HTTPError as exc:
        exc.close()
        return {'status': 'client_auth_unavailable' if exc.code in (401, 403) else 'http_unverified',
                'http_status': exc.code}
    except (OSError, ValueError):
        return {'status': 'transport_unavailable'}


def recovery_drill(deployment, root, now, saved=None):
    """Copy exact receipt-owned text only; restore into a disposable directory."""
    if not root.is_absolute() or any(root.resolve().is_relative_to(p.resolve())
                                     for p in (deployment.home, deployment.state, deployment.source, deployment.personal_skills)):
        raise ValueError('Backup root must be separate from live homes/source/state')
    safe(root, 'probe')
    root.mkdir(parents=True, exist_ok=True)
    folder = safe(root, 'snapshot-' + now.strftime('%Y%m%dT%H%M%S%fZ'))
    folder.mkdir()
    manifest = []
    for name, receipt in deployment.record.get('files', {}).items():
        # A receipt alone cannot authorize reading arbitrary user data.
        allowed = (name == 'AGENTS.md' or name.startswith(('guides/', '@personal/'))
                   or name in ('astra.config.toml', 'astra-deep.config.toml', 'sol.config.toml',
                               'agents/explorer.toml', 'bin/trace_rtk.py'))
        if not allowed or any(part.lower() in ('sessions', 'auth.json', 'history.jsonl', 'db')
                              for part in Path(name).parts):
            continue
        source = deployment.path(name)
        if source.suffix not in ('.md', '.toml', '.yaml', '.yml', '.py', '.json'):
            continue
        data = source.read_bytes()
        if len(data) > 1048576 or digest(data) != receipt['sha256']:
            raise ValueError('Owned recovery input changed; no live repair attempted')
        relative = ('personal/' + name[len('@personal/'):] if name.startswith('@personal/') else 'codex/' + name)
        destination = safe(folder, relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        manifest.append({'path': relative, 'sha256': digest(data)})
    if not manifest:
        raise ValueError('No receipt-owned text available for recovery drill')
    settings = {name: (saved or {}).get(name) for name in SETTING_KEYS}
    save_json(folder/'settings-summary.json', settings)
    manifest.append({'path': 'settings-summary.json', 'sha256': digest((folder/'settings-summary.json').read_bytes())})
    save_json(folder/'manifest.json', {'owner': 'TRACE-setup-health-v1', 'files': manifest,
                                     'excludes': ['raw config', 'auth', 'sessions', 'DB', 'work files']})
    with tempfile.TemporaryDirectory(prefix='trace-restore-', dir=root) as temporary:
        for row in manifest:
            data = safe(folder, row['path']).read_bytes()
            target = safe(Path(temporary), row['path'])
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
            if digest(target.read_bytes()) != row['sha256']:
                raise ValueError('Disposable restoration hash mismatch')
    return {'status': 'verified', 'files': len(manifest), 'snapshot': str(folder),
            'scope': 'receipt-owned text; never restores into live home; raw config/auth/DB excluded'}


def collect(deployment, now=None, effective=None, host=None, probe=True):
    now = now or datetime.now(timezone.utc)
    path = deployment.state/'routine-review.json'
    routine = read_json(path, {})
    if not authorized(routine, host):
        raise ValueError('Exact host/trace setup-health authorization required')
    scope = routine['maintenance_authorization']['setup_health']
    old = routine.get('setup_health', {})
    key_path = safe(deployment.state, 'health-fingerprint.key')
    if not key_path.exists():
        key_path.write_bytes(secrets.token_bytes(32))
    key = key_path.read_bytes()
    approved_protocols = scope.get('metadata_protocols', [])
    allow_modern = isinstance(approved_protocols, list) and MODERN_PROTOCOL in approved_protocols
    probe_identity = fingerprint({'validator': PROBE_VALIDATOR,
                                  'modern_protocol': MODERN_PROTOCOL if allow_modern else None,
                                  'legacy_protocols': LEGACY_PROTOCOLS}, key)
    config_path = safe(deployment.home, 'config.toml')
    raw_before = config_path.read_bytes()
    config = tomllib.loads(raw_before.decode('utf-8-sig'))
    saved = {name: config.get(name) for name in SETTING_KEYS}
    servers = config.get('mcp_servers', {})
    signatures = {name: fingerprint(server, key) for name, server in servers.items()}
    executable_state = {}
    for name, server in servers.items():
        if 'command' not in server:
            continue
        executable = Path(server['command'])
        try:
            stat = executable.stat()
            executable_state[name] = {'status': 'available' if executable.is_file() else 'not_regular',
                                      'identity': fingerprint([str(executable.resolve()), stat.st_size, stat.st_mtime_ns], key)}
        except OSError:
            executable_state[name] = {'status': 'unavailable'}
    changed_settings = [name for name in SETTING_KEYS if old.get('saved', {}).get(name) != saved[name]] if old else []
    changed_servers = sorted(name for name in set(signatures) | set(old.get('mcp_fingerprints', {}))
                             if signatures.get(name) != old.get('mcp_fingerprints', {}).get(name)
                             or executable_state.get(name) != old.get('executables', {}).get(name))
    effective = {name: (effective or {}).get(name) for name in SETTING_KEYS}
    comparison = {name: ('unknown' if effective[name] is None else
                         'matches' if saved[name] == effective[name] else 'different_origin_unresolved')
                  for name in SETTING_KEYS}
    weekly_due = due(old.get('last_mcp_attempt'), now, 7)
    probe_due = weekly_due or old.get('probe_identity') != probe_identity
    observations = {}
    for name, server in servers.items():
        if not server.get('enabled', True):
            observations[name] = {'status': 'disabled'}; continue
        if name not in changed_servers and not probe_due:
            observations[name] = {**old.get('mcp', {}).get(name, {'status': 'unverified'}), 'reused': True}; continue
        allow = scope.get('mcp_allowlist', {}).get(name)
        if allow != signatures[name]:
            observations[name] = {'status': 'changed_launch_needs_review'}; continue
        if name in scope.get('application_bound', []):
            observations[name] = {'status': 'waiting_for_application_or_manual_session',
                                  'live_connection': 'not asserted; no GUI launch or paused UI test'}; continue
        if not probe:
            observations[name] = {'status': 'probe_not_performed'}; continue
        try:
            observations[name] = (http_probe(server, allow_modern=allow_modern) if 'url' in server
                                  else stdio_probe(server, allow_modern=allow_modern))
        except (OSError, ValueError):
            observations[name] = {'status': 'startup_unverified'}
        observations[name]['checked_at'] = now.isoformat()
    attempted = probe and (probe_due or bool(changed_servers))
    active = [row for row in observations.values() if row['status'] != 'disabled']
    connected = (bool(active) and all(row['status'] == 'connected_metadata_only' for row in active)
                 and any(not row.get('reused') for row in active))
    result = {'checked_at': now.isoformat(), 'saved': saved, 'effective_observed': effective,
              'effective_scope': 'only fields explicitly supplied from this invocation; unknown is not inferred',
              'comparison': comparison, 'changed_settings': changed_settings,
              'mcp_fingerprints': signatures, 'executables': executable_state,
              'probe_identity': probe_identity,
              'changed_mcp': changed_servers, 'mcp': observations,
              'paths': [inspect_binding(binding) for binding in scope.get('path_bindings', [])],
              'last_mcp_attempt': now.isoformat() if attempted else old.get('last_mcp_attempt'),
              'last_mcp_success': now.isoformat() if attempted and connected else old.get('last_mcp_success'),
              'last_recovery_success': old.get('last_recovery_success'),
              'recovery': old.get('recovery', {'status': 'not_yet_checked'})}
    if due(old.get('last_recovery_success'), now, 30):
        try:
            result['recovery'] = recovery_drill(deployment, Path(scope['backup_root']), now, saved)
            result['last_recovery_success'] = now.isoformat()
        except (OSError, ValueError):
            result['recovery'] = {'status': 'failed_preserved', 'reason': 'recovery inputs/root unavailable or changed; retry remains due'}
    result['action_fingerprint'] = fingerprint({
        'saved': saved, 'paths': result['paths'],
        'mcp': {name: {k: row[k] for k in ('status', 'http_status') if k in row}
                for name, row in observations.items()},
        'recovery_status': result['recovery']['status']}, key)
    result['last_notified_fingerprint'] = old.get('last_notified_fingerprint')
    result['last_notified_at'] = old.get('last_notified_at')
    if config_path.read_bytes() != raw_before:
        raise ValueError('Config changed concurrently; collection not committed')
    current = read_json(path, {})
    if current.get('setup_health', {}) != old or current.get('maintenance_authorization') != routine.get('maintenance_authorization'):
        raise ValueError('Concurrent health collection; preserve other result')
    # Redacted result contains no raw MCP args, env values, endpoint URLs or auth content.
    log_root = safe(deployment.state, 'health-logs/snapshot.json').parent
    log_root.mkdir(exist_ok=True)
    save_json(safe(log_root, now.strftime('%Y-%m-%d')+'.json'), result)
    if (not old or changed_settings or changed_servers or result['recovery'] != old.get('recovery')
            or result['paths'] != old.get('paths')):
        # Separate immutable observations retain multiple same-day changes.
        save_json(safe(log_root, 'event-'+now.strftime('%Y%m%dT%H%M%S%fZ')+'.json'), result)
    current['setup_health'] = result
    save_json(path, current)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['collect'])
    for name in ('home', 'state', 'personal-skills'):
        parser.add_argument('--'+name, type=Path)
    parser.add_argument('--session-model')
    parser.add_argument('--session-effort')
    parser.add_argument('--session-approval', choices=['never', 'on-request'])
    parser.add_argument('--session-sandbox', choices=['read-only', 'workspace-write', 'danger-full-access'])
    args = parser.parse_args()
    deployment = Deployment(home=args.home, state=args.state, personal_skills=args.personal_skills)
    effective = dict(zip(SETTING_KEYS, (args.session_model, args.session_effort, args.session_approval, args.session_sandbox)))
    result = collect(deployment, effective=effective)
    print(json.dumps({'checked_at': result['checked_at'], 'changed_settings': result['changed_settings'],
                      'comparison': result['comparison'], 'paths': len(result['paths']),
                      'mcp': result['mcp'], 'recovery': result['recovery']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
