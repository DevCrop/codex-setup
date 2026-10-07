import os
from pathlib import Path
import tempfile
import unittest

from codex_storage import scan


class StorageTests(unittest.TestCase):
    def test_credentials_and_artifacts_are_not_deleted_or_read(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            (home / 'auth.json').write_bytes(b'not-json-private')
            (home / 'visualizations').mkdir()
            (home / 'visualizations' / 'model.ckpt').write_bytes(b'abcd')
            result = scan(home)
            self.assertEqual(result['total_logical_bytes'], 20)
            self.assertTrue((home / 'auth.json').exists())
            self.assertEqual(result['entries'][0]['classification'], 'credentials-preserve')
            self.assertNotIn('not-json-private', str(result))

    def test_links_and_missing_home_are_not_healthy_empty_scans(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / 'home'
            with self.assertRaises(ValueError):
                scan(home)
            home.mkdir()
            outside = Path(directory) / 'outside'
            outside.write_bytes(b'protected')
            try:
                os.symlink(outside, home / 'cache')
            except OSError:
                self.skipTest('Host cannot create a symlink')
            result = scan(home)
            self.assertEqual(result['total_logical_bytes'], 0)
            self.assertEqual(result['entries'][0]['excluded_entries'], 1)
            self.assertEqual(outside.read_bytes(), b'protected')


if __name__ == '__main__':
    unittest.main()
