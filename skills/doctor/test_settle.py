#!/usr/bin/env python3
"""Work sitting in a checkout is saved. An extra checkout goes away once the remote has it."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from doctor import plain_name, publish, retire, save_changes


class Names(unittest.TestCase):
    def test_a_dated_slug_uses_the_title(self):
        self.assertEqual(
            plain_name("hermes-otel-2026-10-18", "Hermes OpenTelemetry installation"),
            "Hermes OpenTelemetry Installation")

    def test_a_random_pair_is_not_a_name(self):
        self.assertEqual(plain_name("gifted-northcutt-a14988", ""), "")

    def test_repair_and_the_date_come_off(self):
        self.assertEqual(plain_name("javar-huggingface-repair", ""), "Javar Huggingface")


def git(path, *args):
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True, text=True)


class Settle(unittest.TestCase):
    def repo(self):
        root = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(subprocess.run, ["rm", "-rf", str(root)], check=False)
        remote = root / "remote.git"
        subprocess.run(["git", "init", "--bare", "-b", "main", str(remote)], check=True, capture_output=True)
        checkout = root / "checkout"
        subprocess.run(["git", "clone", str(remote), str(checkout)], check=True, capture_output=True)
        git(checkout, "commit", "--allow-empty", "-m", "start")
        git(checkout, "push", "-u", "origin", "HEAD")
        return root, checkout

    def test_a_new_file_is_committed(self):
        _, checkout = self.repo()
        (checkout / "note.md").write_text("hello")
        (checkout / "backup.age").write_text("local only")
        self.assertEqual(save_changes(checkout), "committed")
        listed = subprocess.run(
            ["git", "-C", str(checkout), "ls-files"], capture_output=True, text=True, check=True)
        self.assertIn("note.md", listed.stdout)
        self.assertNotIn("backup.age", listed.stdout)
        self.assertTrue((checkout / "backup.age").exists())

    def test_a_key_is_not_committed(self):
        _, checkout = self.repo()
        (checkout / "note.md").write_text("hello")
        (checkout / "key.txt").write_text("-----BEGIN PRIVATE KEY-----\nABC\n")
        self.assertEqual(save_changes(checkout), "secret")
        listed = subprocess.run(
            ["git", "-C", str(checkout), "ls-files"], capture_output=True, text=True, check=True)
        self.assertIn("note.md", listed.stdout)
        self.assertNotIn("key.txt", listed.stdout)
        self.assertTrue((checkout / "key.txt").exists())

    def test_a_pushed_extra_checkout_is_removed(self):
        root, checkout = self.repo()
        extra = root / "extra"
        git(checkout, "worktree", "add", "-b", "extra", str(extra))
        (extra / "more.md").write_text("more")
        self.assertEqual(save_changes(extra), "committed")
        self.assertEqual(publish(extra), "pushed")
        self.assertEqual(retire(extra), "removed")
        self.assertFalse(extra.exists())


if __name__ == "__main__":
    unittest.main()
