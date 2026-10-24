import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from codex_dashboard import Projection, local_link, make_server, schedule_label, write_ready
from setup import Deployment, ROOT, save_json


class FakeRTK:
    def __init__(self):
        self.calls = 0
        self.failed = False

    def snapshot(self):
        self.calls += 1
        if self.failed:
            raise RuntimeError('Unavailable')
        return {'collected_at': '2026-10-24T12:00:00+00:00',
                'summary': {'total_commands': 1, 'total_input': 20,
                            'total_output': 10, 'total_saved': 11},
                'daily': [{'date': '2026-10-24', 'commands': 1,
                           'input_tokens': 20, 'output_tokens': 10, 'saved_tokens': 11}],
                'probe': {'checked_at': '2026-10-01T01:00:00+00:00'},
                'arithmetic_difference': 1,
                'rtk_record_date_basis': 'unknown'}


class CodexDashboardTests(unittest.TestCase):
    def test_optional_disk_link_is_host_local_and_never_copies_credentials(self):
        self.assertEqual(local_link('http://127.0.0.1:8765/'), 'http://127.0.0.1:8765/')
        for url in [None, 'https://example.com/', 'http://127.0.0.1:8765/?token=secret',
                    'http://user:pass@127.0.0.1:8765/', 'http://127.0.0.1:99999/']:
            self.assertIsNone(local_link(url))

    def test_schedule_is_human_readable_without_guessing_unknown_rules(self):
        self.assertEqual(schedule_label('FREQ=DAILY;BYHOUR=8;BYMINUTE=0'), '매일 08:00')
        self.assertIsNone(schedule_label(None))
        for rule in ['FREQ=WEEKLY;BYDAY=MO', 'FREQ=DAILY;BYHOUR=99;BYMINUTE=0']:
            self.assertEqual(schedule_label(rule), '사용자 지정 일정 · 앱에서 확인')

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='trace-dashboard-')
        self.root = Path(self.tmp.name)
        self.home = self.root / 'home 한글'
        self.home.mkdir()
        (self.home / 'config.toml').write_text(
            'model = "user-selected-model"\nmodel_reasoning_effort = "high"\n'
            '[mcp_servers.fixture]\nsecret = "DO_NOT_EXPOSE_CONFIG_SECRET"\n', encoding='utf-8')
        (self.home / 'auth.json').write_text('DO_NOT_READ_AUTH_SECRET', encoding='utf-8')
        (self.home / 'sessions').mkdir()
        (self.home / 'sessions/history.jsonl').write_text('DO_NOT_READ_CONVERSATIONS', encoding='utf-8')
        self.dep = Deployment(ROOT, self.home, self.root / 'state', self.root / 'skills')
        self.dep.apply()
        save_json(self.dep.state / 'routine-review.json', {'unresolved_findings': {},
                                                         'last_verification': {'checked_at': '2026-10-01T00:00:00Z'}})
        save_json(self.dep.state / 'source-report.json', {'results': [], 'pending': []})
        save_json(self.dep.state / 'release-verification.json', {'status': 'pass', 'tag': 'fixture'})
        save_json(self.dep.state / 'closure-report.json', {'cli': 'fixture-cli'})
        auto = self.home / 'automations/trace/automation.toml'
        auto.parent.mkdir(parents=True)
        auto.write_text('status="ACTIVE"\nrrule="FREQ=DAILY;BYHOUR=8"\n', encoding='utf-8')
        self.rtk = FakeRTK()
        self.tick = [0]
        self.projection = Projection(self.dep, self.rtk, lambda: self.tick[0])

    def tearDown(self):
        self.tmp.cleanup()

    def test_projection_is_whitelisted_and_does_not_run_commands_or_read_history(self):
        with patch('subprocess.run', side_effect=AssertionError('No diagnostic/model execution')):
            value = self.projection.snapshot()
        payload = json.dumps(value)
        for secret in ['DO_NOT_EXPOSE_CONFIG_SECRET', 'DO_NOT_READ_AUTH_SECRET',
                       'DO_NOT_READ_CONVERSATIONS', str(self.home)]:
            self.assertNotIn(secret, payload)
        self.assertEqual(value['agents']['parent_model_default'], 'user-selected-model')
        self.assertIsNone(value['agents']['live_count'])
        self.assertIsNone(value['actual_openai_tokens'])
        self.assertIsNone(value['actual_cache_hit_rate'])
        self.assertTrue(value['ponytail']['pinned_hash_matches'])
        self.assertTrue(value['ponytail']['explicit_only'])

    def test_ten_second_cache_then_actual_changes_appear_without_full_validation(self):
        first = self.projection.snapshot()
        (self.home / 'AGENTS.md').write_text('user change', encoding='utf-8')
        self.assertIs(self.projection.snapshot(), first)
        self.assertEqual(self.rtk.calls, 1)
        self.tick[0] = 11
        with patch.object(Deployment, 'verify', side_effect=AssertionError('No full verifier per poll')):
            second = self.projection.snapshot()
        self.assertEqual(second['installation']['mismatch_count'], 1)
        self.assertNotEqual(first['revision'], second['revision'])
        self.assertEqual(self.rtk.calls, 2)
        self.assertEqual(second['installation']['last_verified_at'], '2026-10-01T00:00:00Z')

    def test_missing_state_is_unknown_and_failed_rtk_keeps_original_time(self):
        first = self.projection.snapshot()
        self.rtk.failed = True
        (self.home / 'automations/trace/automation.toml').unlink()
        self.tick[0] = 11
        second = self.projection.snapshot()
        self.assertIsNone(second['routine']['status'])
        self.assertEqual(second['rtk']['status'], 'stale')
        self.assertEqual(second['rtk']['collected_at'], first['rtk']['collected_at'])
        self.assertEqual(second['rtk']['probe'], first['rtk']['probe'])

    def test_readonly_loopback_routes_reject_origin_host_and_file_access(self):
        server = make_server(self.dep, collector=self.projection)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            def request(path, method='GET', headers=None):
                client = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
                client.request(method, path, headers=headers or {})
                result = client.getresponse()
                body = result.read()
                code, fields = result.status, dict(result.getheaders())
                client.close()
                return code, fields, body

            code, fields, body = request('/')
            self.assertEqual(code, 200)
            self.assertIn('Codex 설정 모니터'.encode(), body)
            self.assertNotIn(b'__CODEX_DASHBOARD_DATA__', body)
            self.assertIn("frame-ancestors 'none'", fields['Content-Security-Policy'])
            self.assertEqual(request('/api/dashboard')[0], 200)
            self.assertEqual(request('/assets/dashboard.css')[0], 200)
            self.assertEqual(request('/assets/PretendardVariable.woff2')[0], 200)
            self.assertEqual(request('/api/dashboard', headers={'Origin': 'https://example.com'})[0], 403)
            self.assertEqual(request('/', headers={'Host': 'example.com'})[0], 403)
            for path in ['/auth.json', '/%2e%2e/auth.json', '/api/dashboard?path=auth.json']:
                self.assertEqual(request(path)[0], 404)
            self.assertEqual(request('/api/dashboard', 'POST')[0], 405)
            self.assertNotIn(b'DO_NOT_EXPOSE', request('/api/dashboard')[2])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_ready_file_does_not_replace_user_file(self):
        path = self.root / 'ready.json'
        save_json(path, {'user': 'data'})
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            write_ready(path, {'viewer': 'TRACE Codex dashboard'})
        self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
