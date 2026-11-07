import os
import tempfile
import unittest
import unittest.mock
from match_paths import matches, scan


class MatchPaths(unittest.TestCase):
    def test_file_and_parent_match(self):
        self.assertTrue(matches("src/payments/charge.ts", "src/payments/charge.ts"))
        self.assertTrue(matches("src/payments/", "src/payments/charge.ts"))
        self.assertTrue(matches("src/payments", "src/payments/charge.ts"))

    def test_neighbor_and_prefix_lookalike_do_not_match(self):
        self.assertFalse(matches("src/payments/charge.ts", "src/payments/refund.ts"))
        self.assertFalse(matches("src/pay", "src/payments/charge.ts"))
        self.assertFalse(matches("", "src/payments/charge.ts"))

    def test_tilde_and_absolute_paths_match(self):
        home = os.path.expanduser("~")
        real = home + "/.agents/instructions/shared.md"
        self.assertTrue(matches("~/.agents/instructions/shared.md", real))
        self.assertTrue(matches("~/.agents/docs/lore", home + "/.agents/docs/lore/harness/pitfalls.md"))
        self.assertTrue(matches(home + "/.agents/docs/lore", "~/.agents/docs/lore/x.md"))
        self.assertFalse(matches("~/.agents/docs/lore", home + "/.agents/docs/lorex/x.md"))

    def test_tilde_matches_when_expanduser_uses_backslashes(self):
        def expand(path):
            if path.startswith("~"):
                return "C:\\Users\\me" + path[1:]
            return path

        with unittest.mock.patch("os.path.expanduser", expand):
            self.assertTrue(matches("~/.agents/x.md", "C:\\Users\\me\\.agents\\x.md"))
            self.assertTrue(matches("C:\\Users\\me\\.agents", "~/.agents/x.md"))
            self.assertFalse(matches("~/.agents", "C:\\Users\\me\\.agentsx\\x.md"))

    def test_scan_prints_entry_titles(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "pitfalls.md")
            open(p, "w").write("# Tilde pitfall\n\n`code:` ~/.agents/x.md `updated:` 2026-01-01 `status:` active\n\nbody\n"
                                "# Old\n\n`code:` ~/.agents/x.md `updated:` 2026-01-01 `status:` resolved\n")
            self.assertEqual(scan(d, [os.path.expanduser("~/.agents/x.md")]), ["Tilde pitfall"])

    def test_scan_reads_second_level_headings(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "pitfalls.md"), "w").write(
                "# Payments pitfalls\n\n"
                "## Charge twice\n\n"
                "`code:` src/payments/charge.ts `updated:` 2026-01-01 `status:` active\n\n"
                "## Old\n\n"
                "`code:` src/payments/charge.ts `updated:` 2026-01-01 `status:` resolved\n"
            )
            open(os.path.join(d, "business-rules.md"), "w").write(
                "## Refund window\n\n"
                "`code:` src/payments/refund.ts `updated:` 2026-01-01 `status:` active\n"
            )
            self.assertEqual(scan(d, ["src/payments/charge.ts"]), ["Charge twice"])
            self.assertEqual(scan(d, ["src/payments/refund.ts"]), ["Refund window"])


if __name__ == "__main__":
    unittest.main()
