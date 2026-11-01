"""Disposable component lifecycle and isolation tests; no desktop input."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
import unittest
from unittest.mock import patch

import agent_desktop
from agent_desktop import SOURCE, deployment, install, verify_runtime
from setup import save_json

spec = importlib.util.spec_from_file_location('desktop_runner', SOURCE / 'scripts/desktop.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class DesktopComponentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='trace-desktop-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'Codex home 한글'
        self.state = self.root / 'state'
        self.source = self.root / 'source'
        self.source.mkdir()
        self.binary = self.root / 'reviewed.exe'
        self.binary.write_bytes(b'nonexecutable test fixture')
        self.pin = {'version': '1.0.2', 'binary_sha256': hashlib.sha256(self.binary.read_bytes()).hexdigest(),
                    'archive_sha256': 'a' * 64, 'url': 'https://example.invalid/reviewed'}
        (self.source / 'SKILL.md').write_text('fixture skill\n', encoding='utf-8')
        save_json(self.source / 'manifest.json', {'version': 'test', 'agent_settings': {},
                  'files': [{'source': 'SKILL.md', 'target': 'SKILL.md'}], 'upstream': self.pin})

    def dep(self):
        return deployment(self.home, self.state, self.source)

    def install(self):
        return install(self.home, self.state, self.binary, self.source)

    def test_lifecycle_preserves_global_config_and_claude(self):
        self.home.mkdir()
        config = self.home / 'config.toml'
        config.write_bytes(b'model = "user-selected"\n')
        claude = self.root / '.claude'
        claude.mkdir()
        (claude / 'settings.json').write_bytes(b'{"untouched":true}')
        self.assertEqual(self.install()['status'], 'applied')
        self.assertEqual(self.install()['status'], 'unchanged')
        self.assertEqual(self.dep().verify()['status'], 'pass')
        self.assertEqual(set(self.dep().record['files']), {'SKILL.md'})
        self.assertFalse((self.dep().home / 'config.toml').exists())
        self.dep().uninstall()
        self.assertFalse((self.dep().home / 'SKILL.md').exists())
        self.dep().restore()
        self.assertEqual(self.dep().verify()['status'], 'pass')
        self.assertEqual(config.read_bytes(), b'model = "user-selected"\n')
        self.assertEqual((claude / 'settings.json').read_bytes(), b'{"untouched":true}')

    def test_user_edit_blocks_replacement_and_uninstall(self):
        self.install()
        (self.dep().home / 'SKILL.md').write_text('user edit', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'conflict'):
            self.install()
        with self.assertRaisesRegex(ValueError, 'Modified'):
            self.dep().uninstall()

    def test_runtime_tampering_blocks_install_and_verify(self):
        self.install()
        (self.state / 'runtime/agent-desktop.exe').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            verify_runtime(self.home, self.state, self.pin)
        with self.assertRaises(ValueError):
            self.install()

    def test_interrupted_runtime_receipt_is_recoverable(self):
        original = agent_desktop.save_json
        def interrupt(path, value):
            if Path(path).name == 'runtime.json':
                raise OSError('simulated interrupted receipt write')
            return original(path, value)
        with patch.object(agent_desktop, 'save_json', side_effect=interrupt):
            with self.assertRaisesRegex(OSError, 'simulated'):
                self.install()
        self.assertTrue((self.state / 'runtime-pending.json').exists())
        self.assertTrue((self.state / 'runtime/agent-desktop.exe').exists())
        self.assertEqual(self.install()['status'], 'applied')
        self.assertFalse((self.state / 'runtime-pending.json').exists())
        self.assertEqual(self.dep().verify()['status'], 'pass')

    def test_unowned_binary_is_not_adopted_without_journal(self):
        binary = self.state / 'runtime/agent-desktop.exe'
        binary.parent.mkdir(parents=True)
        binary.write_bytes(self.binary.read_bytes())
        with self.assertRaisesRegex(ValueError, 'Unowned'):
            self.install()
        self.assertFalse((self.state / 'runtime.json').exists())

    def test_noop_preserves_restore_point(self):
        self.install()
        before = (self.state / 'previous.json').read_bytes()
        self.install()
        self.assertEqual((self.state / 'previous.json').read_bytes(), before)
        self.dep().restore()
        self.assertFalse((self.dep().home / 'SKILL.md').exists())

    def test_out_of_scope_target_refused(self):
        manifest = json.loads((self.source / 'manifest.json').read_text(encoding='utf-8'))
        manifest['files'][0]['target'] = '../../config.toml'
        save_json(self.source / 'manifest.json', manifest)
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            self.install()
        self.assertFalse((self.state / 'runtime/agent-desktop.exe').exists())

    def test_linked_skill_root_refused(self):
        outside = self.root / 'outside'
        outside.mkdir()
        skill = self.home / 'skills/codex-agent-desktop'
        skill.parent.mkdir(parents=True)
        try:
            skill.symlink_to(outside, target_is_directory=True)
        except OSError:
            if os.name != 'nt':
                raise
            # Windows junctions need no symlink privilege; no shell-built paths.
            result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
                'New-Item -ItemType Junction -Path $env:TRACE_TEST_LINK -Target $env:TRACE_TEST_TARGET -ErrorAction Stop | Out-Null'],
                env={**os.environ, 'TRACE_TEST_LINK': str(skill), 'TRACE_TEST_TARGET': str(outside)},
                capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, 'Disposable junction creation failed')
        with self.assertRaisesRegex(ValueError, '(?i)link|reparse'):
            self.install()
        self.assertEqual(list(outside.iterdir()), [])

    def test_production_pin_matches_runner(self):
        pin = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))['upstream']
        self.assertEqual(pin['binary_sha256'], runner.PINNED_SHA256)

    def test_real_package_upgrade_rollback_and_removal(self):
        new_source = self.root / 'new package'
        shutil.copytree(SOURCE, new_source)
        manifest = json.loads((new_source / 'manifest.json').read_text(encoding='utf-8'))
        manifest['upstream'] = self.pin
        save_json(new_source / 'manifest.json', manifest)
        old_source = self.root / 'old package'
        shutil.copytree(new_source, old_source)
        old_manifest = dict(manifest, version='1.0.0', files=manifest['files'][:2])
        (old_source / 'SKILL.md').write_text('previous skill', encoding='utf-8')
        save_json(old_source / 'manifest.json', old_manifest)
        install(self.home, self.state, self.binary, old_source)
        self.assertEqual(install(self.home, self.state, self.binary, new_source)['status'], 'applied')
        upgraded = deployment(self.home, self.state, new_source)
        self.assertEqual(upgraded.verify()['status'], 'pass')
        self.assertEqual(len(upgraded.record['files']), 4)
        self.assertEqual(install(self.home, self.state, self.binary, new_source)['status'], 'unchanged')
        upgraded.restore()
        self.assertEqual(deployment(self.home, self.state, old_source).verify()['status'], 'pass')
        self.assertFalse((upgraded.home / 'scripts/fallback.py').exists())
        install(self.home, self.state, self.binary, new_source)
        upgraded = deployment(self.home, self.state, new_source)
        upgraded.uninstall()
        self.assertEqual(list(upgraded.home.iterdir()), [])
        upgraded.restore()
        self.assertEqual(upgraded.verify()['status'], 'pass')

    def test_runner_clears_foreign_session_and_checks_pinned_hash(self):
        self.install()
        with patch.object(runner, 'PINNED_SHA256', self.pin['binary_sha256']):
            # Use the production directory layout rather than changing the runner's contract.
            base = self.root / 'runner-base'
            runtime_state = base / 'components/agent-desktop'
            runtime_state.mkdir(parents=True)
            (runtime_state / 'runtime').mkdir()
            binary = runtime_state / 'runtime/agent-desktop.exe'
            binary.write_bytes(self.binary.read_bytes())
            save_json(runtime_state / 'runtime.json', {'owner': 'TRACE Codex agent-desktop',
                      'home': str(self.home), 'path': str(binary), 'sha256': self.pin['binary_sha256']})
            with patch.object(runner, 'state_location', return_value=base), \
                    patch.dict(os.environ, {'AGENT_DESKTOP_HOME': 'Claude', 'AGENT_DESKTOP_SESSION': 'foreign',
                                            'AGENT_DESKTOP_AGENT_ID': 'foreign-agent'}):
                found, env = runner.runtime(self.home)
                self.assertEqual(found, binary)
                self.assertEqual(env['AGENT_DESKTOP_HOME'], str(runtime_state / 'sessions'))
                self.assertNotIn('AGENT_DESKTOP_SESSION', env)
                self.assertNotIn('AGENT_DESKTOP_AGENT_ID', env)
                binary.write_bytes(b'tampered')
                with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                    runner.runtime(self.home)


if __name__ == '__main__':
    unittest.main()
