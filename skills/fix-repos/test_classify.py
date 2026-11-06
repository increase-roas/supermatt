#!/usr/bin/env python3
"""A child folder is one class. A name alone never makes it a repo."""
import tempfile
import unittest
from pathlib import Path

from classify import classify


class Classify(unittest.TestCase):
    def layout(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        return root

    def test_a_checkout_is_primary(self):
        root = self.layout()
        repo = root / "sdk"
        (repo / ".git").mkdir(parents=True)
        self.assertEqual(classify(repo), "primary")

    def test_a_linked_worktree_is_a_worktree(self):
        root = self.layout()
        repo = root / "agents-skill-quality"
        repo.mkdir()
        (repo / ".git").write_text("gitdir: /somewhere\n")
        self.assertEqual(classify(repo), "worktree")

    def test_a_checkout_inside_worktrees_is_misplaced(self):
        root = self.layout()
        repo = root / "worktrees" / "paperclip"
        (repo / ".git").mkdir(parents=True)
        self.assertEqual(classify(repo), "misplaced")

    def test_a_dated_folder_with_no_git_is_a_dump(self):
        root = self.layout()
        dump = root / "2026-11-06"
        dump.mkdir()
        (dump / "note.md").write_text("x")
        self.assertEqual(classify(dump), "dump")

    def test_a_worktree_folder_is_a_nest(self):
        root = self.layout()
        nest = root / "worktrees"
        nest.mkdir()
        self.assertEqual(classify(nest), "nest")
        other = root / "sdk-worktrees"
        other.mkdir()
        self.assertEqual(classify(other), "nest")

    def test_a_wrapper_around_a_worktree_is_a_nest(self):
        root = self.layout()
        wrapper = root / "Alex-Director"
        repo = wrapper / "gifted"
        repo.mkdir(parents=True)
        (repo / ".git").write_text("gitdir: /somewhere\n")
        self.assertEqual(classify(wrapper), "nest")
        self.assertEqual(classify(repo), "worktree")

    def test_a_file_is_skipped(self):
        root = self.layout()
        f = root / "results.csv"
        f.write_text("a")
        self.assertEqual(classify(f), "skip")


if __name__ == "__main__":
    unittest.main()
