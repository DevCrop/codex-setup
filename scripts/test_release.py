"""Exercise the actual release payload in disposable, explicitly isolated roots."""
from pathlib import Path
import tempfile
import unittest

from setup import Deployment, ROOT, read_json, digest


class ReleaseTests(unittest.TestCase):
    def test_payload_install_remove_restore(self):
        with tempfile.TemporaryDirectory(prefix='trace-release-') as directory:
            root = Path(directory)
            dep = Deployment(ROOT, root / 'home 한글', root / 'state', root / 'personal skills')
            dep.apply()
            self.assertEqual(dep.verify()['status'], 'pass')
            self.assertEqual(dep.apply()['status'], 'unchanged')
            for skill in read_json(ROOT / 'versions.lock.json')['skills']:
                for relative, expected in skill['files'].items():
                    self.assertEqual(digest((dep.home / 'skills' / skill['name'] / relative).read_bytes()), expected)
                self.assertEqual((dep.home / 'skills' / skill['name'] / 'agents/openai.yaml').read_text(encoding='utf-8').strip(),
                                 'policy:\n  allow_implicit_invocation: false')
            (dep.personal_skills / 'user').mkdir(parents=True)
            user = dep.personal_skills / 'user/SKILL.md'
            user.write_text('user-owned', encoding='utf-8')
            self.assertIn('@personal/user/SKILL.md', dep.inventory())
            dep.uninstall()
            self.assertFalse(any(p.is_file() for p in dep.home.rglob('*')))
            self.assertEqual(user.read_text(encoding='utf-8'), 'user-owned')
            dep.restore()
            self.assertEqual(dep.verify()['status'], 'pass')


if __name__ == '__main__':
    unittest.main()
