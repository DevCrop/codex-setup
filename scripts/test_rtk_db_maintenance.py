"""Recovery-point acceptance on disposable DBs; never touch the host's history."""
import hashlib
from contextlib import closing
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import rtk_db_maintenance as maintenance


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / 'history.db'
        self.tool = self.root / 'reviewed-tool'
        self.tool.write_bytes(b'reviewed fixture')
        self.sha = hashlib.sha256(self.tool.read_bytes()).hexdigest()
        self.state = self.root / 'private'
        with closing(sqlite3.connect(self.db)) as c, c:
            c.execute('CREATE TABLE commands(id INTEGER)')
            c.execute('INSERT INTO commands VALUES (1)')
        self.addCleanup(patch.stopall)
        patch.object(maintenance.subprocess, 'run', return_value=
                     subprocess.CompletedProcess([], 0, '3.54.0 fixture', '')).start()
        patch.object(maintenance, 'sqlite', side_effect=self.sqlite).start()

    def sqlite(self, tool, database, sql):
        with closing(sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)) as c:
            if sql.startswith('.backup '):
                import json
                with closing(sqlite3.connect(json.loads(sql.removeprefix('.backup ')))) as dest:
                    c.backup(dest)
                return []
            result = []
            for statement in sql.split(';'):
                if statement.strip():
                    result.extend(str(r[0]) for r in c.execute(statement))
            return result

    def backup(self):
        return maintenance.backup(self.db, self.tool, self.sha, self.state)

    def test_online_backup_includes_committed_wal_and_keeps_prior(self):
        c = sqlite3.connect(self.db)
        self.addCleanup(c.close)
        c.execute('PRAGMA journal_mode=WAL')
        c.execute('INSERT INTO commands VALUES (2)')
        c.commit()
        before = self.db.read_bytes()
        first = self.backup()
        self.assertEqual(first['commands'], 2)
        self.assertEqual(first['source_journal_mode'], 'wal')
        self.assertEqual(self.db.read_bytes(), before)
        c.execute('INSERT INTO commands VALUES (3)')
        c.commit()
        second = self.backup()
        self.assertEqual(second['commands'], 3)
        self.assertTrue(second['previous_retained'])
        with closing(sqlite3.connect(self.state / 'rtk-db-backup/previous.db')) as previous:
            self.assertEqual(previous.execute('SELECT COUNT(*) FROM commands').fetchone()[0], 2)
        receipt = (self.state / 'rtk-db-backup/receipt.json').read_bytes()
        self.assertEqual(self.backup()['status'], 'unchanged')
        self.assertEqual((self.state / 'rtk-db-backup/receipt.json').read_bytes(), receipt)

    def test_corruption_preserves_good_backup_and_receipt(self):
        self.backup()
        folder = self.state / 'rtk-db-backup'
        before = {p.name: p.read_bytes() for p in folder.iterdir() if p.suffix in ('.db', '.json')}
        self.db.write_bytes(b'not a database')
        with self.assertRaises(sqlite3.DatabaseError):
            self.backup()
        self.assertEqual(before, {p.name: p.read_bytes() for p in folder.iterdir() if p.suffix in ('.db', '.json')})

    def test_unowned_and_modified_backup_refused(self):
        folder = self.state / 'rtk-db-backup'
        folder.mkdir(parents=True)
        (folder / 'current.db').write_bytes(b'user file')
        with self.assertRaisesRegex(ValueError, 'Unowned'):
            self.backup()
        self.assertEqual((folder / 'current.db').read_bytes(), b'user file')

    def test_missing_source_never_created_and_tool_hash_checked(self):
        self.db.unlink()
        with self.assertRaises(ValueError):
            self.backup()
        self.assertFalse(self.db.exists())
        with self.assertRaises(ValueError):
            maintenance.backup(self.db, self.tool, '0' * 64, self.state)

    def test_old_sqlite_refused(self):
        maintenance.subprocess.run.return_value.stdout = '3.50.4 old'
        with self.assertRaisesRegex(ValueError, '3.51.3'):
            self.backup()

    def test_invalid_receipt_is_rejected_without_overwrite(self):
        self.backup()
        folder = self.state / 'rtk-db-backup'
        before = (folder / 'current.db').read_bytes()
        receipt = b'{"current":{"sha256":42}}'
        (folder / 'receipt.json').write_bytes(receipt)
        with self.assertRaisesRegex(ValueError, 'Unowned backup receipt'):
            self.backup()
        self.assertEqual((folder / 'current.db').read_bytes(), before)
        self.assertEqual((folder / 'receipt.json').read_bytes(), receipt)


if __name__ == '__main__':
    unittest.main()
