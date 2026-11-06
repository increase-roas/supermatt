import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

const habits = [
  ["../skills/verifying-completion/SKILL.md", "Skip tests for now"],
  ["../skills/verifying-completion/SKILL.md", "deployed, live, or production"],
  ["../skills/implement/SKILL.md", "Before the first edit of a file"],
  ["../skills/implement/SKILL.md", "Adopt it, extend it, or build it"],
  ["../skills/tdd/SKILL.md", "Leave formatter, linter, ignore, and CI configuration unchanged"],
  ["../skills/recover-ci/SKILL.md", "formatter, linter, ignore, and workflow files"],
  ["../skills/handoff/SKILL.md", ".supermatt/session.md"],
  ["../skills/handoff/SKILL.md", "incomplete, not empty"],
  ["../skills/research/SKILL.md", "Leave the repo only when"],
  ["../references/parallel-resources.md", "files, tables, and records each lane will change"],
  ["../skills/to-spec/SKILL.md", "Change the contract before"],
  ["../skills/implement-spec/SKILL.md", "data to check, not instructions"],
  ["../skills/diagnosing-bugs/PERFORMANCE.md", "API p50 and p95"],
  ["../skills/diagnosing-bugs/BUG-CLASSES.md", "stale value"],
  ["../skills/qa/SKILL.md", "shared client state"],
  ["../skills/diagnosing-bugs/SKILL.md", "compiler or type errors"],
  ["../skills/diagnosing-bugs/SKILL.md", "retry cap"],
  ["../skills/writing-for-agents/SKILL.md", "Search skills already installed"],
  ["../skills/project-lore/SKILL.md", "recognizable signal"],
  ["../skills/retro/SKILL.md", "project-lore"],
  ["../skills/ask-supermatt/SKILL.md", "A side question gets a short answer"],
  ["../skills/ask-supermatt/SKILL.md", "host's context meter"],
  ["../skills/commit/SKILL.md", "Do not paste the value"],
  ["../skills/improve-agent-setup/RUBRIC.md", "host's own context meter"],
  ["../skills/code-review/ADVERSARIAL.md", "health check"],
];

test("ECC habits a beginner never types are in the skills that already run", () => {
  for (const [path, phrase] of habits) {
    assert.ok(read(path).includes(phrase), `${path} missing: ${phrase}`);
  }
});
