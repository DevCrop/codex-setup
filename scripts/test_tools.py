import hashlib
import io
import os
from pathlib import Path
import tempfile
import tarfile
import unittest
from unittest.mock import patch
import zipfile

from tools import extract, install, rollback, uninstall, runtime_env, target_name, validate_command
from setup import read_json


class ToolTests(unittest.TestCase):
    def package(self, version):
        payload = version.encode()
        buffer = io.BytesIO()
        if os.name == 'nt':
            with zipfile.ZipFile(buffer, 'w') as z:
                z.writestr('rtk.exe', payload)
        else:
            with tarfile.open(fileobj=buffer, mode='w:gz') as t:
                entry = tarfile.TarInfo('rtk')
                entry.size = len(payload)
                t.addfile(entry, io.BytesIO(payload))
        data = buffer.getvalue()
        lock = {'version': version, 'assets': {target_name():
                {'url': 'fixture', 'sha256': hashlib.sha256(data).hexdigest()}}}
        return lock, lambda url: data

    def test_upgrade_restore_uninstall_and_failed_record(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            one, fetch_one = self.package('one')
            two, fetch_two = self.package('two')
            result = install(state, one, fetch_one, verify_binary=False)
            binary = Path(result['path'])
            with patch('tools.save_json', side_effect=OSError('fixture write failure')):
                with self.assertRaises(OSError):
                    install(state, two, fetch_two, verify_binary=False)
            self.assertEqual(binary.read_bytes(), b'one')
            self.assertEqual(read_json(state/'tools-installed.json')['rtk']['version'], 'one')
            self.assertFalse((state/'tools/rtk/.previous').exists())
            self.assertFalse(list((state/'tools/rtk').glob('.staged*')))
            install(state, two, fetch_two, verify_binary=False)
            with patch('tools.verify', return_value={'status': 'pass'}):
                for action in (rollback, uninstall):
                    with patch('tools.save_json', side_effect=OSError('fixture record failure')):
                        with self.assertRaises(OSError):
                            action(state)
                    self.assertEqual(binary.read_bytes(), b'two')
                    self.assertEqual((state/'tools/rtk/.previous').read_bytes(), b'one')
                    self.assertEqual(read_json(state/'tools-installed.json')['rtk']['version'], 'two')
                self.assertEqual(rollback(state)['version'], 'one')
                self.assertEqual(binary.read_bytes(), b'one')
                self.assertEqual(uninstall(state)['status'], 'removed')
                self.assertEqual(uninstall(state)['status'], 'unchanged')
            self.assertFalse(binary.exists())

    def test_local_compiler_priority_and_missing_compiler_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project/'.git').mkdir()
            bins = project/'node_modules/.bin'
            bins.mkdir(parents=True)
            self.assertEqual(runtime_env(project)['PATH'].split(os.pathsep)[0], str(bins.resolve()))
            with self.assertRaises(ValueError):
                validate_command(['tsc'], project)
            compiler = project/'node_modules/typescript/bin/tsc'
            compiler.parent.mkdir(parents=True)
            compiler.write_text('fixture')
            validate_command(['tsc','--noEmit'], project)
            self.assertEqual(runtime_env(project)['npm_config_offline'], 'true')
    def test_platforms_and_bad_archive(self):
        self.assertIn('windows', target_name('Windows', 'AMD64'))
        self.assertIn('aarch64-apple', target_name('Darwin', 'arm64'))
        self.assertIn('linux-musl', target_name('Linux', 'x86_64'))
        with self.assertRaises(ValueError):
            target_name('Windows', 'arm64')
        with self.assertRaises(Exception):
            extract(b'not an archive', 'rtk.zip')

    def test_checksum_owned_repeat_and_modified_conflict(self):
        buffer = io.BytesIO()
        if os.name == 'nt':
            with zipfile.ZipFile(buffer, 'w') as z:
                z.writestr('rtk.exe', b'fixture binary')
                z.writestr('../../outside', b'must not extract')
        else:
            with tarfile.open(fileobj=buffer, mode='w:gz') as t:
                entry = tarfile.TarInfo('rtk')
                entry.size = len(b'fixture binary')
                t.addfile(entry, io.BytesIO(b'fixture binary'))
                link = tarfile.TarInfo('../../outside')
                link.type = tarfile.SYMTYPE
                link.linkname = '/outside'
                t.addfile(link)
        data = buffer.getvalue()
        asset = {'url': 'fixture', 'sha256': hashlib.sha256(data).hexdigest()}
        lock = {'version': 'fixture', 'assets': {target_name(): asset}}
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            result = install(state, lock, lambda u: data, verify_binary=False)
            self.assertEqual(result['status'], 'installed')
            self.assertFalse((state/'outside').exists())
            self.assertEqual(install(state, lock, lambda u: data, verify_binary=False)['status'], 'unchanged')
            Path(result['path']).write_bytes(b'user modified')
            with self.assertRaises(ValueError):
                install(state, lock, lambda u: data, verify_binary=False)
        with tempfile.TemporaryDirectory() as directory:
            asset['sha256'] = '0'*64
            with self.assertRaises(ValueError):
                install(Path(directory), lock, lambda u: data, verify_binary=False)


if __name__ == '__main__':
    unittest.main()
