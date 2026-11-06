import unittest
from match_paths import matches


class MatchPaths(unittest.TestCase):
    def test_file_and_parent_match(self):
        self.assertTrue(matches("src/payments/charge.ts", "src/payments/charge.ts"))
        self.assertTrue(matches("src/payments/", "src/payments/charge.ts"))
        self.assertTrue(matches("src/payments", "src/payments/charge.ts"))

    def test_neighbor_and_prefix_lookalike_do_not_match(self):
        self.assertFalse(matches("src/payments/charge.ts", "src/payments/refund.ts"))
        self.assertFalse(matches("src/pay", "src/payments/charge.ts"))
        self.assertFalse(matches("", "src/payments/charge.ts"))


if __name__ == "__main__":
    unittest.main()
