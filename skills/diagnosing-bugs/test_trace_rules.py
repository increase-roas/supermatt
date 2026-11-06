"""The debug merge keeps the new actions and leaves the stops out."""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
BUGS = (ROOT / "skills" / "diagnosing-bugs" / "SKILL.md").read_text()
FAULTS = (ROOT / "skills" / "diagnosing-agent-runs" / "FAULT-BOUNDARIES.md").read_text()
HANDOFF = (ROOT / "skills" / "handoff" / "SKILL.md").read_text()


class TraceRules(unittest.TestCase):
    def test_boundary_probe_and_source_fix(self):
        self.assertIn("logs what enters and what leaves each boundary", BUGS)
        self.assertIn("one file at a time", BUGS)
        self.assertIn("line that created the bad value", BUGS)

    def test_stops_from_the_drop_stay_out(self):
        self.assertNotIn("human partner", BUGS)
        self.assertNotIn("defense-in-depth", BUGS)
        self.assertNotIn("validation at each layer", BUGS)

    def test_window_fault_and_unverified_handoff(self):
        self.assertIn("poisoning", FAULTS)
        self.assertIn("fresh session", FAULTS)
        self.assertIn("unverified", HANDOFF)
        self.assertIn("decision that produced it", HANDOFF)


if __name__ == "__main__":
    unittest.main()
