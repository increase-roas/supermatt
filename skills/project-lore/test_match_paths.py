import os
import tempfile
import unittest
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

    def test_scan_prints_entry_titles(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "pitfalls.md")
            open(p, "w").write("# Tilde pitfall\n\n`code:` ~/.agents/x.md `updated:` 2026-01-01 `status:` active\n\nbody\n"
                                "# Old\n\n`code:` ~/.agents/x.md `updated:` 2026-01-01 `status:` resolved\n")
            self.assertEqual(scan(d, [os.path.expanduser("~/.agents/x.md")]), ["Tilde pitfall"])


if __name__ == "__main__":
    unittest.main()
