"""A non-gate choice prefers a method that already worked, and records a checked result."""

import pathlib
import unittest

SKILL = (pathlib.Path(__file__).resolve().parent / "SKILL.md").read_text()


class DecisionRecord(unittest.TestCase):
    def test_prefers_the_recorded_method_and_saves_a_checked_result(self):
        self.assertIn("prefer the method that worked", SKILL)
        self.assertIn("save the method and whether it worked to Hindsight", SKILL)
        self.assertIn("unchecked guess is not a record", SKILL)

    def test_a_close_call_stays_one_recommendation(self):
        self.assertIn("Otherwise the lean is the decision", SKILL)
        self.assertNotIn("jury.sh", SKILL)


if __name__ == "__main__":
    unittest.main()
