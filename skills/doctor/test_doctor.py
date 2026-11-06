#!/usr/bin/env python3
"""Run the doctor command on disposable folders and a Codex diagnostic fixture."""
import json
import os
import tempfile
import unittest
from pathlib import Path

from test_settle import doctor, git


class Doctor(unittest.TestCase):
    def tree(self):
        return Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()

    def closed_folder(self, root, name="2026-11-06"):
        folder = root / name
        folder.mkdir()
        (folder / "README.md").write_text("# Draft Inbox Review\n")
        (folder / ".hidden").write_bytes(b"\0keep me\xff")
        return folder

    def test_preview_and_archive_keep_the_original_contents_under_a_plain_name(self):
        root = self.tree()
        folder = self.closed_folder(root)
        dest = root / "archive" / "Draft Inbox Review" / "Files"
        inode = folder.stat().st_ino

        preview = doctor(folder, "--archive", "--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stdout)
        self.assertIn(str(dest), preview.stdout)
        self.assertFalse(dest.parent.parent.exists())
        self.assertTrue(folder.exists())

        moved = doctor(folder, "--archive")
        self.assertEqual(moved.returncode, 0, moved.stdout)
        self.assertEqual(dest.stat().st_ino, inode)
        self.assertEqual((dest / ".hidden").read_bytes(), b"\0keep me\xff")
        self.assertFalse(folder.exists())
        manifest = root / "archive" / "MANIFEST.tsv"
        rows = manifest.read_text().splitlines()
        self.assertEqual([row.split("\t")[0] for row in rows], ["planned", "moved"])
        self.assertEqual([json.loads(part) for part in rows[-1].split("\t")[1:]], [str(folder), str(dest)])

        rerun = doctor(root)
        self.assertEqual(rerun.returncode, 0, rerun.stdout)
        self.assertEqual(manifest.read_text().splitlines(), rows)
        self.assertTrue(dest.exists())

    def test_same_archive_name_keeps_second_folder_and_first_archive(self):
        root = self.tree()
        first = self.closed_folder(root, "first")
        second = self.closed_folder(root, "second")
        (second / ".hidden").write_text("second copy")

        self.assertEqual(doctor(first, "--archive").returncode, 0)
        result = doctor(second, "--archive")

        self.assertIn("already in use", result.stdout)
        self.assertEqual((second / ".hidden").read_text(), "second copy")
        dest = root / "archive" / "Draft Inbox Review" / "Files"
        self.assertEqual((dest / ".hidden").read_bytes(), b"\0keep me\xff")

    def test_keeps_the_active_folder(self):
        root = self.tree()
        folder = self.closed_folder(root)
        result = doctor(folder, "--archive", cwd=folder)
        self.assertIn("active", result.stdout)
        self.assertTrue(folder.is_dir())
        self.assertFalse((root / "archive").exists())

    def test_keeps_excluded_paths_and_parents_containing_them(self):
        root = self.tree()
        folder = self.closed_folder(root)
        excluded = folder / "Javar Testing"
        excluded.mkdir()
        (excluded / "fixture").write_text("keep")
        sibling = root / "Javar"
        sibling.mkdir()
        other = root / "private work"
        other.mkdir()
        report = doctor(root, "--exclude", "private work").stdout
        self.assertIn("Skipped excluded path 'Javar'", report)
        self.assertIn("Skipped excluded path 'private work'", report)
        self.assertIn("Skipped the excluded folder", doctor(sibling, "--archive").stdout)
        self.assertIn("excluded path", doctor(folder, "--archive").stdout)
        self.assertEqual((excluded / "fixture").read_text(), "keep")
        self.assertFalse((root / "archive").exists())

    def test_collection_checks_without_moving_or_renaming_children(self):
        root = self.tree()
        folder = self.closed_folder(root)
        checkout = root / "old-machine-checkout"
        (checkout / ".git").mkdir(parents=True)
        result = doctor(root)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Collection check complete", result.stdout)
        self.assertTrue(folder.exists())
        self.assertTrue(checkout.exists())
        self.assertFalse((root / "archive").exists())

    def test_keeps_a_folder_with_a_deep_checkout_or_relative_link(self):
        root = self.tree()
        folder = self.closed_folder(root)
        nested = folder / "nested" / "checkout" / ".git"
        nested.mkdir(parents=True)
        linked = self.closed_folder(root, "another")
        (linked / "pointer").symlink_to("../2026-11-06")

        self.assertIn("contains a checkout", doctor(folder, "--archive").stdout)
        self.assertIn("contains a checkout, link", doctor(linked, "--archive").stdout)
        self.assertTrue(nested.is_dir())
        self.assertEqual(os.readlink(linked / "pointer"), "../2026-11-06")
        self.assertFalse((root / "archive").exists())

    def test_keeps_bare_git_repositories_and_their_parent_folders(self):
        root = self.tree()
        folder = self.closed_folder(root)
        bare = folder / "nested" / "a-remote"
        bare.parent.mkdir()
        git(root, "init", "--bare", str(bare))

        self.assertIn("bare Git repository", doctor(bare, "--archive").stdout)
        self.assertIn("bare Git repository", doctor(folder, "--archive").stdout)
        self.assertTrue((bare / "HEAD").is_file())
        self.assertFalse((root / "archive").exists())

    def test_keeps_a_folder_that_contains_the_configured_codex_home(self):
        root = self.tree()
        folder = self.closed_folder(root)
        home = folder / "tools"
        home.mkdir()
        (home / "config.toml").write_text("# live config fixture")

        result = doctor(folder, "--archive", env=dict(os.environ, CODEX_HOME=str(home)))

        self.assertIn("contains the Codex configuration folder", result.stdout)
        self.assertEqual((home / "config.toml").read_text(), "# live config fixture")
        self.assertFalse((root / "archive").exists())

    def test_keeps_an_excluded_or_hardlinked_manifest_untouched(self):
        for mode in ("excluded", "hardlinked"):
            with self.subTest(mode=mode):
                root = self.tree()
                folder = self.closed_folder(root)
                archive = root / "archive"
                archive.mkdir()
                manifest = archive / "MANIFEST.tsv"
                external = root / "other"
                external.write_text("keep")
                if mode == "hardlinked":
                    os.link(external, manifest)
                    result = doctor(folder, "--archive")
                else:
                    result = doctor(folder, "--archive", "--exclude", str(manifest))

                self.assertIn("archive record", result.stdout)
                self.assertTrue(folder.exists())
                self.assertEqual(external.read_text(), "keep")
                self.assertEqual(list(archive.iterdir()), [manifest] if mode == "hardlinked" else [])

    def test_resumes_its_own_pending_archive_with_an_empty_destination(self):
        root = self.tree()
        folder = self.closed_folder(root)
        container = root / "archive" / "Draft Inbox Review"
        dest = container / "Files"
        container.mkdir(parents=True)
        manifest = container.parent / "MANIFEST.tsv"
        paths = "\t".join(json.dumps(str(item)) for item in (folder, dest))
        manifest.write_text(f"planned\t{paths}\n")

        result = doctor(folder, "--archive")

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual((dest / ".hidden").read_bytes(), b"\0keep me\xff")
        self.assertEqual(manifest.read_text(), f"planned\t{paths}\nmoved\t{paths}\n")

    def test_codex_diagnostic_without_configuration_status_reports_incomplete(self):
        root = self.tree()
        home = root / "codex-fixture"
        home.mkdir()
        native = root / "codex"
        native.write_text("""#!/bin/sh
printf '%s\n' '{"overallStatus":"ok","checks":{}}'
""")
        native.chmod(0o700)
        env = dict(os.environ, CODEX_HOME=str(home), PATH=f"{root}:{os.environ['PATH']}")

        result = doctor(home, env=env)

        self.assertEqual(result.returncode, 1)
        self.assertIn("diagnostic was unavailable or incomplete", result.stdout)
        self.assertNotIn("Overall Codex health: passed", result.stdout)

    def test_codex_home_uses_native_diagnostic_and_prints_only_health(self):
        root = self.tree()
        home = root / ".codex"
        home.mkdir()
        marker = home / "config.toml"
        marker.write_text("# configuration bytes")
        bin_path = root / "bin"
        bin_path.mkdir()
        native = bin_path / "codex"
        native.write_text(
            "#!/bin/sh\n"
            'test "$*" = "doctor --json" || exit 7\n'
            'test "$CODEX_HOME" = "$PWD" || exit 8\n'
            "cat <<'EOF'\n"
            '{"overallStatus":"fail","checks":{"config.load":{"status":"ok"},'
            '"auth.credentials":{"status":"fail","detail":"Fixture secret marker"},'
            '"desktop.security.enforcement":{"status":"warning"}}}\n'
            "EOF\n"
            "exit 1\n")
        native.chmod(0o700)
        env = dict(os.environ, CODEX_HOME=str(home), PATH=f"{bin_path}:{os.environ['PATH']}")

        result = doctor(home, "--dry-run", env=env)

        self.assertEqual(result.returncode, 1)
        self.assertIn("Codex configuration: passed", result.stdout)
        self.assertIn("Codex sign-in: failed", result.stdout)
        self.assertIn("Desktop security checks: warning", result.stdout)
        self.assertNotIn("Fixture secret marker", result.stdout + result.stderr)
        self.assertEqual(marker.read_text(), "# configuration bytes")


if __name__ == "__main__":
    unittest.main()
