import tempfile
from pathlib import Path
import unittest

from check_updates import Body, check
from setup import read_json, save_json


class MonitorTests(unittest.TestCase):
    def test_main_body_excludes_navigation(self):
        parser = Body()
        parser.feed('<header>changing navigation</header><main>real <article>body</article></main><footer>noise</footer>')
        self.assertEqual(' '.join(parser.primary), 'real  body')

    def test_failure_preserves_success_and_previous_body(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d)
            items = [{'id': 'A', 'url': 'https://example.org'}]
            def good(item):
                return {**item, 'status': 'fetched', 'sha256': 'one', 'body': 'old body'}
            check(state, items, good)
            success = (state / 'source-success.json').read_bytes()
            report = check(state, items, lambda item: {**item, 'status': 'error', 'error': 'TimeoutError'})
            self.assertEqual(report['results'][0]['status'], 'error')
            self.assertEqual((state / 'source-success.json').read_bytes(), success)
            self.assertEqual(read_json(state / 'source-status.json')['A']['body'], 'old body')

    def test_change_diff_and_retired_source_cleanup(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d)
            save_json(state / 'source-status.json', {'A': {'sha256': 'old', 'body': 'old body'}, 'removed': {'body': 'legacy'}})
            report = check(state, [{'id': 'A', 'url': 'https://example.org'}],
                           lambda item: {**item, 'status': 'fetched', 'sha256': 'new', 'body': 'new body'})
            self.assertEqual(report['results'][0]['change'], 'candidate')
            self.assertIn('-old body', report['results'][0]['diff_excerpt'])
            self.assertNotIn('removed', read_json(state / 'source-status.json'))

    def test_empty_watchlist_refused(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                check(Path(d), [])


if __name__ == '__main__':
    unittest.main()
