from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from maintenance_health import (POLICY, authorized, collect, fingerprint, http_probe,
                                http_initialize_reply, inspect_binding, stdio_probe)
from setup import Deployment, digest, read_json, save_json


INITIALIZED = {'jsonrpc': '2.0', 'id': 1, 'result': {
    'protocolVersion': '2025-03-26', 'capabilities': {'tools': {}},
    'serverInfo': {'name': 'disposable-test', 'version': '1'}}}
DISCOVERED = {'jsonrpc': '2.0', 'id': 0, 'result': {
    'resultType': 'complete', 'supportedVersions': ['2026-07-28'], 'capabilities': {'tools': {}},
    'ttlMs': 0, 'cacheScope': 'private'}}


class ProbeResponse(io.BytesIO):
    def __init__(self, raw, content_type='application/json'):
        super().__init__(raw)
        self.headers = {'Content-Type': content_type}


class HealthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='trace-health-test-')
        self.root = Path(self.tmp.name)
        self.home = self.root/'home'; self.home.mkdir()
        self.state = self.root/'state'; self.state.mkdir()
        self.source = self.root/'source'; self.source.mkdir()
        save_json(self.source/'manifest.json', {'version': 'test', 'files': []})
        (self.home/'AGENTS.md').write_text('owned instructions\n', encoding='utf-8')
        (self.home/'config.toml').write_text('model="selected-model"\nmodel_reasoning_effort="high"\napproval_policy="on-request"\nsandbox_mode="workspace-write"\n[mcp_servers.sample]\nurl="https://example.invalid/private-secret"\n', encoding='utf-8')
        # Forbidden data must remain untouched, even if accidentally listed in a receipt.
        (self.home/'auth.json').write_text('credential-secret', encoding='utf-8')
        (self.home/'work.db').write_bytes(b'protected-db')
        save_json(self.state/'installed.json', {'files': {
            name: {'sha256': digest((self.home/name).read_bytes())}
            for name in ('AGENTS.md', 'auth.json', 'work.db')}})
        self.dep = Deployment(self.source, self.home, self.state, self.root/'personal')
        self.key = b'k'*32; (self.state/'health-fingerprint.key').write_bytes(self.key)
        self.scope = {'automation_id': 'trace', 'host_identity': 'host', 'approved_on': '2026-10-25',
                      'policy': POLICY, 'backup_root': str(self.root/'backups'), 'path_bindings': [],
                      'mcp_allowlist': {'sample': fingerprint({'url': 'https://example.invalid/private-secret'}, self.key)}}
        self.routine = {'unrelated': {'preserve': True}, 'maintenance_authorization': {
            'automation_id': 'trace', 'host_identity': 'host', 'setup_health': self.scope}}
        save_json(self.state/'routine-review.json', self.routine)
        self.now = datetime(2026, 10, 25, tzinfo=timezone.utc)

    def tearDown(self):
        self.tmp.cleanup()

    def run_collect(self, now=None, **kwargs):
        return collect(self.dep, now=now or self.now, host='host', **kwargs)

    def test_exact_authority_and_host_required(self):
        self.assertTrue(authorized(self.routine, 'host'))
        self.assertFalse(authorized(self.routine, 'other'))
        self.routine['maintenance_authorization']['host_identity'] = 'other'
        self.assertFalse(authorized(self.routine, 'host'))
        save_json(self.state/'routine-review.json', self.routine)
        with self.assertRaises(ValueError):
            self.run_collect()

    @patch('maintenance_health.http_probe', return_value={'status': 'connected_metadata_only'})
    def test_snapshot_restore_privacy_and_daily_weekly_monthly_cadence(self, probe):
        protected = {p.name: p.read_bytes() for p in self.home.iterdir()}
        first = self.run_collect()
        self.assertEqual(first['recovery']['status'], 'verified')
        self.assertEqual(first['comparison']['model'], 'unknown')
        manifest = read_json(Path(first['recovery']['snapshot'])/'manifest.json')
        self.assertEqual({r['path'] for r in manifest['files']}, {'codex/AGENTS.md', 'settings-summary.json'})
        self.assertEqual(probe.call_count, 1)
        self.run_collect(self.now + timedelta(days=1))
        self.assertEqual(probe.call_count, 1)
        week = self.run_collect(self.now + timedelta(days=7))
        self.assertEqual(probe.call_count, 2)
        self.assertEqual(week['last_recovery_success'], first['last_recovery_success'])
        month = self.run_collect(self.now + timedelta(days=30))
        self.assertNotEqual(month['recovery']['snapshot'], first['recovery']['snapshot'])
        self.assertEqual(protected, {p.name: p.read_bytes() for p in self.home.iterdir()})
        self.assertTrue(read_json(self.state/'routine-review.json')['unrelated']['preserve'])
        for p in list((self.state/'health-logs').glob('*.json')) + list((self.root/'backups').rglob('*.json')):
            self.assertNotIn('private-secret', p.read_text(encoding='utf-8'))
            self.assertNotIn('credential-secret', p.read_text(encoding='utf-8'))
        self.assertFalse(list((self.root/'backups').glob('trace-restore-*')))

    @patch('maintenance_health.http_probe', return_value={'status': 'client_auth_unavailable', 'http_status': 401})
    def test_failed_mcp_attempt_is_not_success_and_not_retried_daily(self, probe):
        first = self.run_collect()
        self.assertIsNone(first['last_mcp_success'])
        routine = read_json(self.state/'routine-review.json')
        routine['setup_health']['last_notified_fingerprint'] = first['action_fingerprint']
        routine['setup_health']['last_notified_at'] = self.now.isoformat()
        save_json(self.state/'routine-review.json', routine)
        second = self.run_collect(self.now + timedelta(days=1))
        self.assertEqual(second['action_fingerprint'], second['last_notified_fingerprint'])
        self.assertEqual(second['last_notified_at'], self.now.isoformat())
        self.assertEqual(probe.call_count, 1)
        self.run_collect(self.now + timedelta(days=7))
        self.assertEqual(probe.call_count, 2)

    @patch('maintenance_health.http_probe', return_value={'status': 'connected_metadata_only'})
    def test_drift_never_changes_settings_and_changed_launch_needs_review(self, probe):
        self.run_collect()
        config = self.home/'config.toml'
        config.write_text(config.read_text().replace('"high"', '"low"').replace('private-secret', 'changed-secret'))
        expected = config.read_bytes()
        second = self.run_collect(self.now + timedelta(seconds=1), effective={'approval_policy': 'never'})
        self.assertEqual(second['changed_settings'], ['model_reasoning_effort'])
        self.assertEqual(second['comparison']['approval_policy'], 'different_origin_unresolved')
        self.assertEqual(second['mcp']['sample']['status'], 'changed_launch_needs_review')
        self.assertEqual(probe.call_count, 1)
        self.assertEqual(config.read_bytes(), expected)
        self.assertEqual(len(list((self.state/'health-logs').glob('event-*'))), 2)

    @patch('maintenance_health.http_probe')
    def test_application_bound_skips_launch_and_failed_recovery_remains_due(self, probe):
        self.scope['application_bound'] = ['sample']
        save_json(self.state/'routine-review.json', self.routine)
        (self.home/'AGENTS.md').write_text('user edit', encoding='utf-8')
        first = self.run_collect()
        self.assertEqual(first['mcp']['sample']['status'], 'waiting_for_application_or_manual_session')
        probe.assert_not_called()
        self.assertEqual(first['recovery']['status'], 'failed_preserved')
        self.assertIsNone(first['last_recovery_success'])
        (self.home/'AGENTS.md').write_text('owned instructions\n', encoding='utf-8')
        self.assertEqual(self.run_collect(self.now + timedelta(days=1))['recovery']['status'], 'verified')

    def test_link_metadata_only_and_missing_executable(self):
        source = self.root/'ordinary'; source.mkdir()
        row = inspect_binding({'name': 'ordinary', 'source': str(source), 'target': str(self.home)})
        self.assertEqual(row['status'], 'broken_or_changed')
        self.assertTrue(source.is_dir())
        missing = self.root/'missing-source'
        row = inspect_binding({'name': 'archived', 'source': str(missing), 'target': str(self.home)})
        self.assertEqual(row['status'], 'source_missing_archive_present')
        self.assertFalse(missing.exists())
        self.assertEqual(stdio_probe({'command': str(self.root/'missing.exe')})['status'], 'missing_executable')

    def test_stdio_uses_only_initialize_and_list_then_stops_owned_child(self):
        log = self.root/'methods.jsonl'
        fake = self.root/'fake_mcp.py'
        fake.write_text('import sys,json\nfrom pathlib import Path\n'
                        'for line in sys.stdin:\n'
                        ' q=json.loads(line)\n'
                        ' with Path(sys.argv[1]).open("a") as f: f.write(q["method"]+"\\n")\n'
                        ' if "id" in q:\n'
                        f'  reply={INITIALIZED!r} if q["id"] == 1 else {{"jsonrpc":"2.0","id":2,"result":{{"tools":[]}}}}\n'
                        '  print(json.dumps(reply),flush=True)\n', encoding='utf-8')
        result = stdio_probe({'command': sys.executable, 'args': [str(fake), str(log)]})
        self.assertEqual(result['status'], 'connected_metadata_only')
        self.assertEqual(log.read_text().splitlines(), ['initialize', 'notifications/initialized', 'tools/list'])

    def test_stdio_rejects_malformed_and_out_of_order_responses(self):
        fake = self.root/'invalid_mcp.py'
        bad_init = [None, [], {}, {'jsonrpc': '2.0', 'id': 1, 'result': []},
                    {**INITIALIZED, 'id': True}, {**INITIALIZED, 'id': 99},
                    {**INITIALIZED, 'jsonrpc': '1.0'},
                    {**INITIALIZED, 'error': {'code': -1, 'message': 'denied'}},
                    {**INITIALIZED, 'result': {**INITIALIZED['result'], 'serverInfo': {}}},
                    {**INITIALIZED, 'result': {**INITIALIZED['result'], 'protocolVersion': '2099-01-01'}},
                    {'jsonrpc': '2.0', 'id': 2, 'result': {'tools': []}}]
        for reply in bad_init:
            with self.subTest(initialize=reply):
                fake.write_text('import sys,json\nsys.stdin.readline()\n'
                                f'print(json.dumps({reply!r}), flush=True)\n', encoding='utf-8')
                result = stdio_probe({'command': sys.executable, 'args': [str(fake)]}, timeout=1)
                self.assertNotEqual(result['status'], 'connected_metadata_only')
        bad_tools = [None, [], {}, {'tools': None}, {'tools': {}}, {'tools': [None]},
                     {'tools': [{'name': 'x'}]}, {'tools': [{'name': 1, 'inputSchema': {'type': 'object'}}]},
                     {'tools': [{'name': 'x', 'inputSchema': {'type': 'array'}}]},
                     {'tools': [], 'nextCursor': 3}]
        for result in bad_tools:
            with self.subTest(tools=result):
                fake.write_text('import sys,json\n'
                                'for line in sys.stdin:\n'
                                ' q=json.loads(line)\n'
                                f' if q.get("id") == 1: print(json.dumps({INITIALIZED!r}),flush=True)\n'
                                f' if q.get("id") == 2: print(json.dumps({{"jsonrpc":"2.0","id":2,"result":{result!r}}}),flush=True)\n', encoding='utf-8')
                self.assertEqual(stdio_probe({'command': sys.executable, 'args': [str(fake)]})['status'],
                                 'tools_list_refused')

    def test_http_json_rejects_wrong_id_error_and_malformed_initialize(self):
        replies = [None, [], {}, {**INITIALIZED, 'id': 2}, {**INITIALIZED, 'id': True},
                   {**INITIALIZED, 'jsonrpc': '1.0'}, {**INITIALIZED, 'result': []},
                   {**INITIALIZED, 'result': {'tools': []}},
                   {**INITIALIZED, 'error': {'code': -1, 'message': 'private-secret'}}]
        for reply in replies:
            with self.subTest(reply=reply), patch('maintenance_health.urllib.request.build_opener') as opener:
                opener.return_value.open.return_value = ProbeResponse(json.dumps(reply).encode())
                self.assertEqual(http_probe({'url': 'http://example.invalid'})['status'], 'initialize_refused')
        with patch('maintenance_health.urllib.request.build_opener') as opener:
            opener.return_value.open.return_value = ProbeResponse(json.dumps(INITIALIZED).encode())
            self.assertEqual(http_probe({'url': 'http://example.invalid'})['status'], 'connected_metadata_only')

    def test_http_sse_reads_matching_multiline_event_before_keepalive_eof(self):
        finished = threading.Event()
        methods = []
        payload = json.dumps(INITIALIZED).replace(', ', ',\ndata: ')
        raw = (': keepalive\r\n\r\n'
               'data: {"jsonrpc":"2.0","method":"notifications/message"}\r\n\r\n'
               'data: {"jsonrpc":"2.0","id":99,"result":{}}\r\n\r\n'
               f'event: message\ndata: {payload}\n\n').encode()

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'

            def do_POST(self):
                methods.append(json.loads(self.rfile.read(int(self.headers['Content-Length'])))['method'])
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
                self.end_headers()
                self.wfile.write(raw); self.wfile.flush()
                finished.wait(3)  # Deliberately do not send EOF until the probe has returned.
                self.close_connection = True

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True); worker.start()
        try:
            result = http_probe({'url': f'http://127.0.0.1:{server.server_port}/mcp'}, timeout=.7)
            self.assertEqual(result['status'], 'connected_metadata_only')
            self.assertEqual(methods, ['initialize'])
        finally:
            finished.set(); server.shutdown(); server.server_close(); worker.join(timeout=2)

    def test_http_sse_limits_and_incomplete_or_invalid_events(self):
        for ending in (b'\n', b'\r\n', b'\r'):
            with self.subTest(ending=ending):
                raw = b'data: ' + json.dumps(INITIALIZED).encode() + ending*2
                self.assertEqual(http_initialize_reply(ProbeResponse(raw, 'text/event-stream'),
                                                      time.monotonic()+1), INITIALIZED)
        class FragmentedResponse(ProbeResponse):
            def read1(self, size):
                return super().read1(min(size, 1))
        raw = b'data: '+json.dumps(INITIALIZED).encode()+b'\r\n\r\n'
        self.assertEqual(http_initialize_reply(FragmentedResponse(raw, 'text/event-stream'),
                                              time.monotonic()+1), INITIALIZED)
        for raw in (b'data: {}\n\n', b'data: nope\n\n', b'data: {}', b'data: \xff\n\n'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                http_initialize_reply(ProbeResponse(raw, 'text/event-stream'), time.monotonic()+1)
        with self.assertRaises(OverflowError):
            http_initialize_reply(ProbeResponse(b':' + b'x'*1048576, 'text/event-stream'), time.monotonic()+1)
        with self.assertRaises(TimeoutError):
            http_initialize_reply(ProbeResponse(b': keepalive\n\n', 'text/event-stream'), time.monotonic()-1)

    @patch('maintenance_health.http_probe')
    def test_empty_or_disabled_scope_preserves_last_success(self, probe):
        for config in ('', '[mcp_servers.sample]\nenabled=false\nurl="https://example.invalid"\n'):
            with self.subTest(config=config):
                (self.home/'config.toml').write_text(config, encoding='utf-8')
                self.routine['setup_health'] = {'last_mcp_success': '2026-01-01T00:00:00+00:00'}
                save_json(self.state/'routine-review.json', self.routine)
                self.assertEqual(self.run_collect()['last_mcp_success'], '2026-01-01T00:00:00+00:00')
        probe.assert_not_called()

    @patch('maintenance_health.http_probe', return_value={'status': 'connected_metadata_only'})
    def test_disabled_scope_change_does_not_relabel_cached_success_as_live(self, probe):
        first = self.run_collect()
        config = self.home/'config.toml'
        config.write_text(config.read_text(encoding='utf-8') + '\n[mcp_servers.disabled]\nenabled=false\n', encoding='utf-8')
        second = self.run_collect(self.now+timedelta(days=1))
        self.assertEqual(second['last_mcp_success'], first['last_mcp_success'])
        self.assertTrue(second['mcp']['sample']['reused'])
        self.assertEqual(probe.call_count, 1)

    @patch('maintenance_health.http_probe', return_value={'status': 'connected_metadata_only'})
    def test_probe_identity_change_rechecks_once_and_protocols_require_host_scope(self, probe):
        first = self.run_collect()
        self.assertEqual(probe.call_args.kwargs, {'allow_modern': False})
        self.run_collect(self.now+timedelta(days=1))
        self.assertEqual(probe.call_count, 1)
        routine = read_json(self.state/'routine-review.json')
        routine['setup_health']['probe_identity'] = 'older-validator'
        save_json(self.state/'routine-review.json', routine)
        second = self.run_collect(self.now+timedelta(days=1, seconds=1))
        self.assertEqual(probe.call_count, 2)
        self.assertEqual(second['probe_identity'], first['probe_identity'])
        self.run_collect(self.now+timedelta(days=2))
        self.assertEqual(probe.call_count, 2)
        routine = read_json(self.state/'routine-review.json')
        routine['maintenance_authorization']['setup_health']['metadata_protocols'] = ['2026-07-28']
        save_json(self.state/'routine-review.json', routine)
        third = self.run_collect(self.now+timedelta(days=2, seconds=1))
        self.assertNotEqual(third['probe_identity'], first['probe_identity'])
        self.assertEqual(probe.call_args.kwargs, {'allow_modern': True})
        self.assertEqual(probe.call_count, 3)

    def test_modern_stdio_discovery_and_legacy_fallback_are_metadata_only(self):
        for modern in (True, False):
            with self.subTest(modern=modern):
                log = self.root/'negotiated-methods.jsonl'
                log.write_text('', encoding='utf-8')
                fake = self.root/'negotiated_mcp.py'
                discovered = DISCOVERED if modern else {
                    'jsonrpc': '2.0', 'id': 0, 'error': {'code': -32601, 'message': 'unknown method'}}
                listed = {'jsonrpc': '2.0', 'id': 2, 'result': {
                    'tools': [], 'resultType': 'complete', 'ttlMs': 0, 'cacheScope': 'private'}}
                fake.write_text('import sys,json\nfrom pathlib import Path\n'
                                f'replies={{0:{discovered!r},1:{INITIALIZED!r},2:{listed!r}}}\n'
                                'for line in sys.stdin:\n'
                                ' q=json.loads(line)\n'
                                ' with Path(sys.argv[1]).open("a") as f: f.write(q["method"]+"\\n")\n'
                                ' if q["method"] == "server/discover":\n'
                                '  assert q["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"] == "2026-07-28"\n'
                                f' if {modern!r} and q["method"] == "tools/list":\n'
                                '  assert q["params"]["_meta"]["io.modelcontextprotocol/clientCapabilities"] == {}\n'
                                ' if "id" in q: print(json.dumps(replies[q["id"]]),flush=True)\n', encoding='utf-8')
                result = stdio_probe({'command': sys.executable, 'args': [str(fake), str(log)]}, allow_modern=True)
                self.assertEqual(result['status'], 'connected_metadata_only')
                self.assertEqual(result['protocol_era'], 'modern' if modern else 'legacy')
                self.assertEqual(log.read_text().splitlines(), ['server/discover', 'tools/list'] if modern else
                                 ['server/discover', 'initialize', 'notifications/initialized', 'tools/list'])

    def test_modern_http_malformed_discovery_is_never_success_or_legacy_retry(self):
        bad_results = [None, [], {},
                       {**DISCOVERED['result'], 'supportedVersions': '2026-07-28'},
                       {**DISCOVERED['result'], 'capabilities': []},
                       {**DISCOVERED['result'], 'resultType': 'input_required'},
                       {**DISCOVERED['result'], 'ttlMs': -1},
                       {**DISCOVERED['result'], 'cacheScope': 'unknown'}]
        replies = [{**DISCOVERED, 'result': result} for result in bad_results]
        replies += [{**DISCOVERED, 'id': 1}, {**DISCOVERED, 'id': False},
                    {**DISCOVERED, 'error': {'code': -1, 'message': 'denied'}}]
        for reply in replies:
            with self.subTest(reply=reply), patch('maintenance_health.urllib.request.build_opener') as opener:
                opener.return_value.open.return_value = ProbeResponse(json.dumps(reply).encode())
                self.assertEqual(http_probe({'url': 'http://example.invalid'}, allow_modern=True)['status'],
                                 'discovery_refused')
                self.assertEqual(opener.return_value.open.call_count, 1)

    def test_modern_http_loopback_negotiation_and_no_auth_or_error_fallback(self):
        for mode in ('modern', 'legacy', 'auth', 'modern_error', 'malformed'):
            with self.subTest(mode=mode):
                finished = threading.Event()
                requests = []

                class Handler(BaseHTTPRequestHandler):
                    protocol_version = 'HTTP/1.1'

                    def do_POST(self):
                        q = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                        requests.append((self.path, q, dict(self.headers)))
                        if mode == 'legacy' and q['method'] == 'server/discover':
                            code, body = 400, {'jsonrpc': '2.0', 'id': 0, 'error': {'code': -32601, 'message': 'unknown method'}}
                        elif mode == 'auth':
                            code, body = 401, {}
                        elif mode == 'modern_error':
                            code, body = 400, {'jsonrpc': '2.0', 'id': 0, 'error': {
                                'code': -32022, 'message': 'unsupported', 'data': {'supported': ['2099-01-01']}}}
                        elif mode == 'malformed':
                            code, body = 200, {**DISCOVERED, 'result': {'supportedVersions': '2026-07-28'}}
                        else:
                            code, body = 200, INITIALIZED if mode == 'legacy' else DISCOVERED
                        raw = json.dumps(body).encode()
                        self.send_response(code)
                        self.send_header('Content-Type', 'text/event-stream' if mode == 'modern' else 'application/json')
                        if mode != 'modern':
                            self.send_header('Content-Length', str(len(raw)))
                        self.end_headers()
                        self.wfile.write(b'data: '+raw+b'\n\n' if mode == 'modern' else raw); self.wfile.flush()
                        if mode == 'modern':
                            finished.wait(3)
                        self.close_connection = True

                    def log_message(self, *args):
                        pass

                server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
                worker = threading.Thread(target=server.serve_forever, daemon=True); worker.start()
                try:
                    result = http_probe({'url': f'http://127.0.0.1:{server.server_port}/mcp'}, timeout=1, allow_modern=True)
                    expected = {'modern': 'connected_metadata_only', 'legacy': 'connected_metadata_only',
                                'auth': 'client_auth_unavailable', 'modern_error': 'modern_protocol_unverified',
                                'malformed': 'discovery_refused'}[mode]
                    self.assertEqual(result['status'], expected)
                    self.assertEqual([row[1]['method'] for row in requests],
                                     ['server/discover', 'initialize'] if mode == 'legacy' else ['server/discover'])
                    self.assertTrue(all(row[0] == '/mcp' for row in requests))
                    headers = {k.lower(): v for k, v in requests[0][2].items()}
                    self.assertEqual(headers['mcp-protocol-version'], '2026-07-28')
                    self.assertEqual(headers['mcp-method'], 'server/discover')
                    self.assertEqual(requests[0][1]['params']['_meta']['io.modelcontextprotocol/clientCapabilities'], {})
                finally:
                    finished.set(); server.shutdown(); server.server_close(); worker.join(timeout=2)


if __name__ == '__main__':
    unittest.main()
