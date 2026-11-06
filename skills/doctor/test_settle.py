#!/usr/bin/env python3
"""Run doctor on disposable checkouts and read back the saved Git state."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from doctor import MAX_FILE_BYTES, plain_name

DOCTOR = Path(__file__).resolve().with_name("doctor.py")


def git(path, *args):
    return subprocess.run(
        ["git", "-C", str(path), *args], check=True, capture_output=True).stdout


def doctor(path, *args, cwd=None, env=None):
    return subprocess.run(
        [sys.executable, "-B", str(DOCTOR), str(path), *args],
        cwd=cwd, env=env, text=True, capture_output=True, timeout=55)


class Names(unittest.TestCase):
    def test_a_dated_slug_uses_the_title(self):
        self.assertEqual(
            plain_name("telemetry-2026-10-18", "Hermes OpenTelemetry installation"),
            "Hermes OpenTelemetry Installation")

    def test_a_random_pair_is_not_a_name(self):
        self.assertEqual(plain_name("gifted-northcutt-a14988"), "")


class Settle(unittest.TestCase):
    def repo(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        remote = root / "remote.git"
        checkout = root / "checkout"
        git(root, "init", "--bare", "-b", "main", str(remote))
        git(root, "clone", str(remote), str(checkout))
        git(checkout, "config", "user.name", "Doctor Test")
        git(checkout, "config", "user.email", "doctor@example.test")
        git(checkout, "config", "commit.gpgsign", "false")
        git(checkout, "config", "core.hooksPath", str(root / "fixture-hooks"))
        (checkout / ".gitignore").write_text("ignored.txt\n")
        (checkout / "tracked.md").write_text("starting text")
        git(checkout, "add", "--", ".gitignore", "tracked.md")
        git(checkout, "commit", "-m", "start")
        git(checkout, "push", "-u", "origin", "HEAD")
        return root, remote, checkout

    def run_doctor(self, path, *args, env=None):
        result = doctor(path, *args, env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def snapshots(self, path):
        return git(path, "for-each-ref", "--format=%(refname)", "refs/heads/doctor/").splitlines()

    def test_snapshot_saves_only_eligible_files_and_preserves_original_index(self):
        _, remote, checkout = self.repo()
        (checkout / ".env").write_text("FAKE_TOKEN=fixture")
        git(checkout, "add", "--", ".env")
        (checkout / "tracked.md").write_text("staged work")
        git(checkout, "add", "--", "tracked.md")
        (checkout / "tracked.md").write_text("unsaved work over staged work")
        (checkout / "ignored.txt").write_text("ignored")
        (checkout / "staged-backup.txt").write_bytes(b"x" * (MAX_FILE_BYTES + 1))
        git(checkout, "add", "--", "staged-backup.txt")
        (checkout / "large.txt").write_bytes(b"y" * (MAX_FILE_BYTES + 1))
        (checkout / "key.txt").write_text("-----BEGIN PRIVATE KEY-----\nABC\n")
        (checkout / "settings.json").write_text('{"access_token": "fixture"}')
        (checkout / "note with -> punctuation\nand newline.md").write_text("save this")
        (checkout / "other.md").symlink_to("tracked.md")
        head = git(checkout, "rev-parse", "HEAD")
        index = (checkout / ".git" / "index").read_bytes()
        status = git(checkout, "status", "--porcelain=v1", "-z", "--ignored")

        report = self.run_doctor(checkout)

        self.assertIn("verified remote commit", report)
        self.assertEqual(git(checkout, "rev-parse", "HEAD"), head)
        self.assertEqual(git(remote, "rev-parse", "refs/heads/main"), head)
        self.assertEqual((checkout / ".git" / "index").read_bytes(), index)
        self.assertEqual(git(checkout, "status", "--porcelain=v1", "-z", "--ignored"), status)
        snapshot, = self.snapshots(remote)
        self.assertEqual(self.snapshots(checkout), [snapshot])
        self.assertEqual(git(remote, "rev-parse", snapshot), git(checkout, "rev-parse", snapshot))
        self.assertEqual(
            git(remote, "ls-tree", "-z", "--name-only", snapshot).split(b"\0"),
            [b".gitignore", b"note with -> punctuation\nand newline.md", b"tracked.md", b""])
        self.assertEqual(git(remote, "show", snapshot + b":tracked.md"), b"starting text")
        self.assertEqual(git(remote, "show", snapshot + b":note with -> punctuation\nand newline.md"),
                         b"save this")
        self.assertNotIn("FAKE_TOKEN", report)
        self.assertIn("'key.txt' on disk (possible credential", report)
        self.assertNotIn("BEGIN PRIVATE KEY", report)
        self.assertIn("verified remote commit", self.run_doctor(checkout))
        self.assertEqual(self.snapshots(remote), [snapshot])

    def test_linked_worktree_and_its_ignored_content_stay_where_they_are(self):
        root, remote, checkout = self.repo()
        extra = root / "extra"
        git(checkout, "worktree", "add", "-b", "extra", str(extra))
        git(extra, "push", "-u", "origin", "HEAD")
        git(extra, "worktree", "lock", "--reason", "another session", str(extra))
        (extra / "ignored.txt").write_text("local work")
        (extra / "new.txt").write_text("save this")

        report = self.run_doctor(extra)

        self.assertIn("verified remote commit", report)
        self.assertEqual((extra / "ignored.txt").read_text(), "local work")
        self.assertEqual((extra / "new.txt").read_text(), "save this")
        self.assertIn(os.fsencode(extra), git(checkout, "worktree", "list", "--porcelain"))
        self.assertEqual(len(self.snapshots(remote)), 1)

    def test_divergent_histories_save_locally_without_rebasing_or_pushing(self):
        root, remote, checkout = self.repo()
        other = root / "other"
        git(root, "clone", str(remote), str(other))
        git(other, "-c", "user.name=Doctor Test", "-c", "user.email=doctor@example.test",
            "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", "the remote changed")
        git(other, "push", "origin", "HEAD")
        remote_head = git(remote, "rev-parse", "main")
        git(checkout, "commit", "--allow-empty", "-m", "local commit")
        local_head = git(checkout, "rev-parse", "HEAD")
        (checkout / "pending.txt").write_text("keep")

        self.assertIn("Kept local", self.run_doctor(checkout))
        self.assertEqual(git(checkout, "rev-parse", "HEAD"), local_head)
        self.assertEqual(git(remote, "rev-parse", "main"), remote_head)
        self.assertEqual(self.snapshots(remote), [])
        snapshot, = self.snapshots(checkout)
        self.assertEqual(git(checkout, "show", snapshot + b":pending.txt"), b"keep")

    def test_dry_run_and_exclude_leave_checkouts_and_remotes_untouched(self):
        _, remote, checkout = self.repo()
        (checkout / "note.md").write_text("keep")
        self.assertIn("Preview. 1 file(s)", self.run_doctor(checkout, "--dry-run"))
        self.assertIn("No eligible", self.run_doctor(checkout, "--exclude", "note.md"))
        self.assertEqual(self.snapshots(checkout), [])
        self.assertEqual(self.snapshots(remote), [])

    def test_a_remote_rejection_keeps_a_local_copy_without_claiming_remote_backup(self):
        _, remote, checkout = self.repo()
        reject = remote / "hooks" / "pre-receive"
        reject.write_text("#!/bin/sh\nexit 1\n")
        reject.chmod(0o700)
        (checkout / "pending.txt").write_text("keep")

        report = self.run_doctor(checkout)

        self.assertIn("the remote did not confirm", report)
        self.assertNotIn("verified remote commit", report)
        self.assertEqual(self.snapshots(remote), [])
        snapshot, = self.snapshots(checkout)
        self.assertEqual(git(checkout, "show", snapshot + b":pending.txt"), b"keep")

    def test_a_linked_checkout_cannot_write_into_an_excluded_primary_checkout(self):
        root, remote, checkout = self.repo()
        extra = root / "active-copy"
        git(checkout, "worktree", "add", "-b", "extra", str(extra))
        (extra / "pending.txt").write_text("keep")

        result = doctor(extra, "--exclude", str(checkout))

        self.assertIn("Git data is excluded", result.stdout)
        self.assertEqual((extra / "pending.txt").read_text(), "keep")
        self.assertEqual(self.snapshots(checkout), [])
        self.assertEqual(self.snapshots(remote), [])

    def test_checkout_commit_hooks_are_respected(self):
        root, remote, checkout = self.repo()
        hooks = root / "fixture-hooks"
        hooks.mkdir()
        hook = hooks / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o700)
        (checkout / "pending.txt").write_text("keep")

        report = self.run_doctor(checkout)

        self.assertIn("needs its normal commit workflow", report)
        self.assertEqual((checkout / "pending.txt").read_text(), "keep")
        self.assertEqual(self.snapshots(checkout), [])
        self.assertEqual(self.snapshots(remote), [])

    def test_common_credentials_in_ordinary_text_are_held(self):
        _, remote, checkout = self.repo()
        fixtures = {
            "oauth.json": '{"client_secret": "fixture"}',
            "app.json": '{"clientSecret": "fixture"}',
            "provider.json": '{"AWS_SECRET_ACCESS_KEY": "fixture"}',
            "google.txt": "AIza" + "X" * 35,
            "stripe.txt": "sk_live_" + "X" * 24,
            "registry.txt": "npm_" + "X" * 36,
            "gitlab.txt": "glpat-" + "X" * 20,
            "header.txt": "eyJ0eXAiOiJKV1Q.eyJzdWIiOiJmaXh0dXJl.fakefixtureSignature",
        }
        for name, content in fixtures.items():
            (checkout / name).write_text(content)
        (checkout / "note.md").write_text("save me")

        report = self.run_doctor(checkout)

        snapshot, = self.snapshots(remote)
        names = git(remote, "ls-tree", "--name-only", snapshot).splitlines()
        self.assertEqual(names, [b".gitignore", b"note.md", b"tracked.md"])
        for name, content in fixtures.items():
            self.assertIn(name, report)
            self.assertNotIn(content, report)
            self.assertEqual((checkout / name).read_text(), content)

    def test_excluded_local_and_file_url_remotes_receive_no_snapshot(self):
        for mode in ("path", "file", "named", "symlink"):
            with self.subTest(mode=mode):
                root, remote, checkout = self.repo()
                restricted = root / ("Javar Testing" if mode == "named" else "outside")
                restricted.mkdir()
                destination = restricted / "destination.git"
                remote.rename(destination)
                url = destination.as_uri() if mode == "file" else str(destination)
                if mode == "symlink":
                    alias = root / "alias.git"
                    alias.symlink_to(destination, target_is_directory=True)
                    url = str(alias)
                git(checkout, "remote", "set-url", "origin", url)
                (checkout / "pending.txt").write_text("keep")
                exclusions = [] if mode == "named" else ["--exclude", str(restricted)]
                report = self.run_doctor(checkout, *exclusions)
                self.assertIn("remote destination is excluded", report)
                self.assertEqual(self.snapshots(destination), [])
                self.assertEqual(len(self.snapshots(checkout)), 1)

    def test_clean_ahead_checkout_reports_local_commit(self):
        _, remote, checkout = self.repo()
        git(checkout, "commit", "--allow-empty", "-m", "work saved locally")
        local = git(checkout, "rev-parse", "HEAD")

        report = self.run_doctor(checkout)

        self.assertIn("ahead of its remote branch", report)
        self.assertNotEqual(git(remote, "rev-parse", "main"), local)
        self.assertEqual(self.snapshots(remote), [])

    def test_unborn_checkout_preview_explains_missing_starting_commit(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        git(root, "init", "-b", "main")
        (root / "pending.txt").write_text("keep")

        report = self.run_doctor(root, "--dry-run")

        self.assertIn("no starting commit yet", report)
        self.assertNotIn("qualify", report)
        self.assertEqual(self.snapshots(root), [])


if __name__ == "__main__":
    unittest.main()
