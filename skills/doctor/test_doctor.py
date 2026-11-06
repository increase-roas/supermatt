#!/usr/bin/env python3
"""doctor moves a leftover folder and leaves a checkout where it is."""
import tempfile
import unittest
from pathlib import Path

from doctor import apply, plan


class Doctor(unittest.TestCase):
    def tree(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        dump = root / "2026-11-06"
        dump.mkdir()
        note = dump / "note.md"
        note.write_text("keep me")
        primary = root / "sdk"
        (primary / ".git").mkdir(parents=True)
        (primary / "README.md").write_text("live")
        link = root / "worktrees" / "job"
        link.mkdir(parents=True)
        (link / ".git").write_text("gitdir: /somewhere\n")
        return root, note

    def test_a_dump_moves_and_a_checkout_stays(self):
        root, note = self.tree()
        moves, keeps = plan(root)
        self.assertEqual([p.name for p in moves], ["2026-11-06"])
        apply(root)
        dest = root / "archive" / "2026-11-06" / "note.md"
        self.assertEqual(dest.read_text(), "keep me")
        self.assertFalse(note.exists())
        self.assertTrue((root / "sdk" / "README.md").exists())
        self.assertTrue((root / "worktrees" / "job" / ".git").is_file())
        manifest = (root / "archive" / "MANIFEST.tsv").read_text()
        self.assertIn("2026-11-06", manifest)
        again, _ = plan(root)
        self.assertEqual(again, [])

    def test_a_second_pass_does_not_move_the_archive(self):
        root, _ = self.tree()
        apply(root)
        apply(root)
        self.assertEqual(len(list((root / "archive").iterdir())), 2)


if __name__ == "__main__":
    unittest.main()
