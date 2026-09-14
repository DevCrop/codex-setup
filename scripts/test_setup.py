import base64
import json
import os
from pathlib import Path
import tempfile
import unittest

from setup import Deployment, digest, patch_agents, safe, save_json


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="trace-test-")
        self.root = Path(self.tmp.name)
        self.source = self.root / "source 한글"
        self.source.mkdir()
        self.home = self.root / "home with spaces"
        self.state = self.root / "state"
        (self.source / "rules.md").write_text("new rules\n", encoding="utf-8")
        self.manifest = {"version": "1", "files": [{"source": "rules.md", "target": "AGENTS.md"}],
                         "agent_settings": {"enabled": True, "max_concurrent_threads_per_session": 2}}
        self.write_manifest()

    def tearDown(self):
        self.tmp.cleanup()

    def write_manifest(self):
        save_json(self.source / "manifest.json", self.manifest)

    def dep(self):
        return Deployment(self.source, self.home, self.state)

    def test_install_idempotent_rollback(self):
        d = self.dep()
        d.apply()
        self.assertEqual(d.verify()["status"], "pass")
        previous = (self.state / "previous.json").read_bytes()
        self.assertEqual(d.apply()["status"], "unchanged")
        self.assertEqual(previous, (self.state / "previous.json").read_bytes())
        d.restore()
        self.assertFalse((self.home / "AGENTS.md").exists())

    def test_existing_files_need_adoption(self):
        self.home.mkdir()
        (self.home / "AGENTS.md").write_text("personal", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.dep().apply()
        d = self.dep()
        d.apply(True)
        d.restore()
        self.assertEqual((self.home / "AGENTS.md").read_text(), "personal")

    def test_local_edits_protected_even_with_adopt(self):
        self.dep().apply()
        (self.home / "AGENTS.md").write_text("user edits", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.dep().apply(True)
        with self.assertRaises(ValueError):
            self.dep().uninstall()

    def test_remove_obsolete_owned_file(self):
        self.dep().apply()
        self.manifest["files"] = []
        self.manifest["version"] = "2"
        self.write_manifest()
        d = self.dep()
        d.apply()
        self.assertFalse((self.home / "AGENTS.md").exists())
        d.restore()
        self.assertTrue((self.home / "AGENTS.md").exists())

    def test_config_preserves_model_and_other_values(self):
        self.home.mkdir()
        raw = b'model = "user-choice"\nmodel_reasoning_effort = "xhigh"\n[agents]\nenabled = false\n[other]\nsetting = "keep"\n'
        (self.home / "config.toml").write_bytes(raw)
        self.dep().apply()
        text = (self.home / "config.toml").read_text()
        self.assertIn('model = "user-choice"', text)
        self.assertIn('setting = "keep"', text)
        self.dep().uninstall()
        self.assertIn("enabled = false", (self.home / "config.toml").read_text())

    def test_unrelated_config_edit_survives_update(self):
        self.dep().apply()
        p = self.home / "config.toml"
        p.write_text('model = "changed"\n' + p.read_text(), encoding="utf-8")
        self.dep().apply()
        self.assertIn('model = "changed"', p.read_text())

    def test_managed_config_edit_conflicts(self):
        self.dep().apply()
        p = self.home / "config.toml"
        p.write_text(p.read_text().replace("enabled = true", "enabled = false"), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.dep().apply()

    def test_retired_fingerprint(self):
        self.home.mkdir()
        (self.home / "old.md").write_bytes(b"legacy")
        self.manifest["retired"] = [{"target": "old.md", "sha256": digest(b"legacy")}]
        self.write_manifest()
        d = self.dep()
        d.apply()
        self.assertFalse((self.home / "old.md").exists())
        d.restore()
        self.assertEqual((self.home / "old.md").read_bytes(), b"legacy")

    def test_interrupted_recovery(self):
        self.home.mkdir()
        (self.home / "AGENTS.md").write_bytes(b"after")
        save_json(self.state / "pending.json", {"home": str(self.home), "record": {"files": {}}, "files": {
            "AGENTS.md": {"before": base64.b64encode(b"before").decode(), "after": digest(b"after")}}})
        d = self.dep()
        with self.assertRaises(ValueError):
            d.apply()
        d.restore("pending.json")
        self.assertEqual((self.home / "AGENTS.md").read_bytes(), b"before")

    def test_rollback_rejects_post_install_edits(self):
        self.dep().apply()
        (self.home / "AGENTS.md").write_bytes(b"edit")
        with self.assertRaises(ValueError):
            self.dep().restore()

    def test_traversal_rejected(self):
        for rel in ["../outside", "C:/outside", "/tmp/file", "a\\b", "file.", "file "]:
            with self.subTest(rel=rel), self.assertRaises(ValueError):
                safe(self.home, rel)

    def test_symlink_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.home.mkdir()
        try:
            (self.home / "linked").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Symlink creation not available")
        with self.assertRaises(ValueError):
            safe(self.home, "linked/file")

    def test_unmanaged_files_survive(self):
        self.dep().apply()
        (self.home / "user.txt").write_bytes(b"keep")
        self.dep().uninstall()
        self.assertEqual((self.home / "user.txt").read_bytes(), b"keep")

    def test_atomic_write_failure_recovers(self):
        from unittest.mock import patch
        d = self.dep()
        original = d._write
        count = 0
        def failure(p, data):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("simulated interruption")
            original(p, data)
        with patch.object(d, "_write", failure), self.assertRaises(OSError):
            d.apply()
        self.assertFalse((self.home / "AGENTS.md").exists())
        self.assertFalse((self.state / "pending.json").exists())

    def test_existing_identical_config_restored(self):
        self.home.mkdir()
        original = patch_agents(None, self.manifest["agent_settings"])
        (self.home / "config.toml").write_bytes(original)
        self.dep().apply()
        self.dep().uninstall()
        self.assertEqual((self.home / "config.toml").read_bytes(), original)

    def test_deleted_config_key_removed(self):
        self.dep().apply()
        self.manifest["agent_settings"].pop("max_concurrent_threads_per_session")
        self.manifest["version"] = "2"
        self.write_manifest()
        self.dep().apply()
        self.assertNotIn("max_concurrent", (self.home / "config.toml").read_text())

    def test_uninstall_removes_originally_absent_config(self):
        self.dep().apply()
        self.dep().uninstall()
        self.assertFalse((self.home / "config.toml").exists())

    def test_multiline_toml_false_table_refused(self):
        raw = b'developer_instructions = """\n[agents]\nenabled = false\n"""\n[agents]\nenabled = false\n'
        with self.assertRaises(ValueError):
            patch_agents(raw, self.manifest["agent_settings"])

    def test_uninstall_removes_empty_created_table_preserving_user_model(self):
        self.dep().apply()
        path = self.home / "config.toml"
        path.write_text('model = "user"\n' + path.read_text(), encoding="utf-8")
        self.dep().uninstall()
        self.assertIn('model = "user"', path.read_text())
        self.assertNotIn('[agents]', path.read_text())

    @unittest.skipUnless(os.name == "nt", "Windows junction test")
    def test_junction_refused(self):
        import subprocess
        self.home.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        junction = self.home / "linked"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(outside)], capture_output=True)
        if result.returncode:
            self.skipTest("Junction creation unavailable")
        try:
            with self.assertRaises(ValueError):
                safe(self.home, "linked/file")
        finally:
            junction.rmdir()


if __name__ == "__main__":
    unittest.main()
