import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from rtk_status import publish_reports, overview, template_render, model, render
from rtk_dashboard import Collector
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


if __name__ == '__main__':
    unittest.main()
