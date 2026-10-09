import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from rtk_status import publish_reports, overview, template_render, model, render, current_flow
from rtk_dashboard import Collector, probe_fingerprint
from setup import ROOT


class IntegratedReportTests(unittest.TestCase):
    def test_report_control_ids_are_real_and_unique(self):
        import re
        for name in ('adaptive-routine.template.html', 'rtk-efficiency.template.html'):
            source = (ROOT / 'templates/reports' / name).read_text(encoding='utf-8')
            ids = re.findall(r'\bid="([^"]+)"', source)
            self.assertEqual(len(ids), len(set(ids)))
            refs = set(re.findall(r"el\('([^']+)'\)", source))
            optional = {'flow-state', 'flow-findings', 'flow-reviewed-at'}
            self.assertFalse(refs - set(ids) - optional)
            for target in refs - set(ids):
                self.assertIn("if(el('" + target + "'))", source)

    def test_conflict_in_later_target_preserves_every_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            dep = SimpleNamespace(state=Path(tmp))
            folder = dep.state / 'reports'; folder.mkdir()
            (folder / 'rtk-status.html').write_bytes(b'owned')
            (folder / 'rtk-status.evidence.json').write_text(json.dumps({
                'artifact_sha256': hashlib.sha256(b'owned').hexdigest()}))
            (folder / 'overview.html').write_bytes(b'user edit')
            with self.assertRaisesRegex(ValueError, 'ownership conflict'):
                publish_reports(dep, {'rtk-status.html': b'new', 'overview.html': b'new'})
            self.assertEqual((folder / 'rtk-status.html').read_bytes(), b'owned')
            self.assertEqual((folder / 'overview.html').read_bytes(), b'user edit')

    def test_report_repeat_and_failed_write_restore_previous_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            dep = SimpleNamespace(state=Path(tmp))
            initial = {'rtk-status.html': b'one', 'overview.html': b'two'}
            publish_reports(dep, initial); publish_reports(dep, initial)
            from rtk_status import atomic
            calls = []
            def interrupted(path, data):
                calls.append(path.name)
                if len(calls) == 2:
                    raise OSError('controlled fixture failure')
                return atomic(path, data)
            with patch('rtk_status.atomic', interrupted), self.assertRaises(OSError):
                publish_reports(dep, {k: b'new' for k in initial})
            for name, data in initial.items():
                self.assertEqual((dep.state / 'reports' / name).read_bytes(), data)

    def test_current_schedule_unknowns_and_data_injection(self):
        data = overview({'automation': {'schedule': 'daily 08:00 Asia/Seoul'}}, 'fail', 'commit', 'now')
        self.assertFalse(data['publication']['applied'])
        self.assertEqual(data['host_schedule']['label'], 'daily 08:00 Asia/Seoul')
        empty = overview({}, 'pass', 'commit', 'now')
        self.assertEqual(empty['host_schedule']['label'], '미등록')
        self.assertFalse(empty['publication']['published'])
        output = template_render('adaptive-routine.template.html', '__ROUTINE_REPORT_DATA__', data).decode()
        self.assertNotIn('__ROUTINE_REPORT_DATA__', output)
        self.assertIn('canonical-flow', output)
        self.assertNotIn('매일 08:00 · Asia/Seoul', output)
        report = model({'feedback_loop': {'rtk_aggregate': {'collected_at': '</script><script>alert(1)</script>'}}}, {}, {})
        output = render(report, 'now').decode()
        self.assertNotIn('</script><script>alert(1)</script>', output)

    def test_live_refresh_invalidates_a_stale_probe_without_changing_its_time(self):
        from test_rtk_dashboard import aggregate
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); reports = root / 'reports'; reports.mkdir()
            baseline = {'probe': {'checked_at': '2026-10-08T00:00:00Z',
                                 'required_evidence_preserved': True, 'raw_exit': 0, 'filtered_exit': 0}}
            (reports / 'rtk-efficiency.json').write_text(json.dumps(baseline))
            collector = Collector(root, reports, run=lambda *a, **kw:
                subprocess.CompletedProcess(a, 0, json.dumps(aggregate()), ''))
            with patch('rtk_dashboard.probe_matches', return_value=False):
                result = collector.snapshot()
            self.assertFalse(result['probe']['required_evidence_preserved'])
            self.assertEqual(result['probe']['checked_at'], baseline['probe']['checked_at'])
            self.assertEqual(json.loads((reports / 'rtk-efficiency.json').read_text()), baseline)

    def test_publication_is_bound_to_exact_clean_source_and_remote(self):
        record = {'current_checks': {'git_publication': {'head': 'new', 'remote_head': 'new',
                   'checked_at': 'now', 'release_commit': 'old', 'release_asset_install': 'pass'}}}
        data = overview(record, 'pass', 'new', 'now', source_clean=True)
        self.assertTrue(data['publication']['committed'])
        self.assertTrue(data['publication']['branch_published'])
        self.assertFalse(data['publication']['published'])
        for commit, clean in [('old', True), ('new', False), ('new', None)]:
            data = overview(record, 'pass', commit, 'now', source_clean=clean)
            self.assertFalse(data['publication']['branch_published'])
            self.assertFalse(data['publication']['published'])

    def test_recorded_cli_failure_stays_separate_from_installation_and_redacts_details(self):
        record = {'feedback_loop': {'current_cli_doctor': {
            'version': '0.161.0', 'checked_at': '2026-10-08T14:34:48Z',
            'overall_status': 'fail', 'raw_report': 'private-secret',
            'checks': [{'check': 'checks.sandbox.helpers', 'status': 'fail',
                        'details': 'private-secret'}]}}}
        data = overview(record, 'pass', 'commit', 'later')
        self.assertEqual(data['checks'][0]['status'], 'pass')
        diagnoses = [row for row in data['checks'] if row['label'].startswith('기록된')]
        self.assertEqual([row['status'] for row in diagnoses], ['fail', 'fail'])
        self.assertTrue(all('2026-10-08T14:34:48+00:00' in row['evidence'] for row in diagnoses))
        self.assertTrue(all('현재 실행 재검증과 별도' in row['evidence'] for row in diagnoses))
        self.assertNotIn('private-secret', json.dumps(data))
        record['feedback_loop']['current_cli_doctor']['checked_at'] = 'private-secret'
        data = overview(record, 'pass', 'commit', 'later')
        self.assertEqual(data['checks'][-1]['status'], 'unknown')
        self.assertNotIn('private-secret', json.dumps(data))

    def test_flow_success_requires_current_exact_artifact_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); folder = root / 'diagrams/global'; folder.mkdir(parents=True)
            receipt = {'gates': {k: 'pass' for k in ('validate', 'deliver', 'check')}}
            for key, name in [('specification_sha256', 'codex-flow.json'), ('artifact_sha256', 'codex-flow.html')]:
                data = name.encode(); (folder / name).write_bytes(data)
                receipt[key] = hashlib.sha256(data).hexdigest()
            (folder / 'codex-flow.receipt.json').write_text(json.dumps(receipt))
            with patch('rtk_status.ROOT', root):
                self.assertEqual(current_flow()['status'], 'pass')
                (folder / 'codex-flow.html').write_bytes(b'changed')
                self.assertEqual(current_flow()['status'], 'unknown')

    def test_live_validation_reuses_exact_bytes_and_reopens_on_drift_or_unknown(self):
        collector = Collector(Path('fixture-home'), Path('fixture-reports'))
        with patch('rtk_dashboard.probe_fingerprint', side_effect=[('one',), ('one',), ('two',), None]), \
                patch('rtk_dashboard.probe_matches', side_effect=[True, False, False]) as validate:
            self.assertTrue(collector.retained_probe_matches({}))
            self.assertTrue(collector.retained_probe_matches({}))
            self.assertFalse(collector.retained_probe_matches({}))
            self.assertFalse(collector.retained_probe_matches({}))
            self.assertEqual(validate.call_count, 3)

    def test_probe_cache_identity_uses_bytes_not_unchanged_size_or_mtime(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); state = root / 'state'; home = root / 'home'
            paths = [state / 'tools-installed.json', state / 'tools/rtk' / ('rtk.exe' if os.name == 'nt' else 'rtk'),
                     home / 'bin/trace_rtk.py', root / 'scripts/verify_rtk.py']
            for p in paths:
                p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b'original')
            with patch('setup.Deployment', return_value=SimpleNamespace(state=state)), patch('setup.ROOT', root):
                before = probe_fingerprint(home, {})
                info = paths[1].stat(); paths[1].write_bytes(b'modified')
                os.utime(paths[1], ns=(info.st_atime_ns, info.st_mtime_ns))
                self.assertNotEqual(before, probe_fingerprint(home, {}))
                paths[1].unlink()
                self.assertIsNone(probe_fingerprint(home, {}))


if __name__ == '__main__':
    unittest.main()
