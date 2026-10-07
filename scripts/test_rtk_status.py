from pathlib import Path
import unittest

from rtk_status import model, render


class ReportTests(unittest.TestCase):
    def test_missing_evidence_is_unknown_not_zero_or_pass(self):
        data = model({}, {}, {})
        self.assertIsNone(data['difference'])
        self.assertIsNone(data['runtime_checks'])
        output = render(data, 'checked').decode()
        self.assertIn('미확인', output)
        self.assertIn('data:font/woff2;base64,', output)
        self.assertNotIn('{{', output)

    def test_discrepancy_is_visible_and_raw_history_is_not_rendered(self):
        routine = {'feedback_loop': {'rtk_aggregate': {'summary': {
            'total_input': 5344, 'total_output': 3176, 'total_saved': 2272, 'total_commands': 89},
            'daily_by_date': {'2026-10-07': {'commands': 8, 'input_tokens': 208, 'output_tokens': 113,
                                           'command': 'private-secret'}},
            'collected_at': '<script>alert(1)</script>'}}}
        data = model(routine, {}, {'status': 'unknown'})
        self.assertEqual(data['discrepancy'], 104)
        self.assertIsNone(data['runtime_checks'])
        output = render(data, 'checked').decode()
        self.assertIn('104', output)
        self.assertNotIn('private-secret', output)
        self.assertNotIn('<script>alert(1)</script>', output)
        self.assertIn('&lt;script&gt;', output)


if __name__ == '__main__':
    unittest.main()
