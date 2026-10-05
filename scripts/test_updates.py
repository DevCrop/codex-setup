import tempfile
from pathlib import Path
import unittest

from check_updates import Body, check, github_body, resolve_candidate
from setup import read_json, save_json


class MonitorTests(unittest.TestCase):
    def test_release_digest_and_notes_without_download_count_noise(self):
        release = {'tag_name':'v1', 'published_at':'date', 'body':'notes',
                   'assets':[{'name':'binary', 'digest':'sha256:a', 'browser_download_url':'url', 'download_count':1}]}
        first = github_body(release)
        release['assets'][0]['download_count'] = 99
        self.assertEqual(github_body(release), first)
        release['assets'][0]['digest'] = 'sha256:b'
        self.assertNotEqual(github_body(release), first)

    def test_candidate_survives_unchanged_and_resolution_is_hash_bound(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d)
            items = [{'id': 'A', 'url': 'https://example.org'}]
            save_json(state / 'source-status.json', {'A': {'sha256': 'old', 'body': 'old body'}})
            fetch = lambda item: {**item, 'status': 'fetched', 'sha256': 'new', 'body': 'new body'}
            check(state, items, fetch)
            again = check(state, items, fetch)
            self.assertEqual(again['results'][0]['change'], 'unchanged')
            self.assertEqual(len(again['pending']), 1)
            with self.assertRaises(ValueError):
                resolve_candidate(state, 'A', 'outdated', 'reviewed')
            resolve_candidate(state, 'A', 'new', 'example-only change, no policy adoption')
            self.assertEqual(check(state, items, fetch)['pending'], [])

    def test_punctuation_noise_and_legacy_pending_import(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d)
            save_json(state / 'source-status.json', {'A': {'sha256': 'old', 'body': "it's unchanged"}})
            save_json(state / 'source-report.json', {'results': [{'id': 'A', 'sha256': 'old', 'change': 'candidate'}]})
            report = check(state, [{'id': 'A', 'url': 'https://example.org'}],
                           lambda item: {**item, 'status': 'fetched', 'sha256': 'new', 'body': 'it’s unchanged'})
            self.assertEqual(report['results'][0]['change'], 'unchanged')
            self.assertEqual(len(report['pending']), 1)

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

    def test_retired_watch_preserves_unresolved_candidate_and_resolution_updates_report(self):
        with tempfile.TemporaryDirectory() as d:
            state = Path(d)
            save_json(state / 'source-pending.json', {'retired': {'id': 'retired', 'sha256': 'hash'}})
            report = check(state, [{'id': 'A', 'url': 'https://example.org'}],
                           lambda item: {**item, 'status': 'fetched', 'sha256': 'new', 'body': 'current'})
            self.assertEqual(report['pending'][0]['id'], 'retired')
            self.assertTrue(report['pending'][0]['monitor_retired'])
            resolve_candidate(state, 'retired', 'hash', 'exact content reviewed; no active use')
            self.assertEqual(read_json(state / 'source-report.json')['pending'], [])


if __name__ == '__main__':
    unittest.main()
