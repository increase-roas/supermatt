import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const implement = readFileSync(new URL("../skills/implement/SKILL.md", import.meta.url), "utf8");
const commit = readFileSync(new URL("../skills/commit/SKILL.md", import.meta.url), "utf8");
const setup = readFileSync(new URL("../skills/improve-agent-setup/SKILL.md", import.meta.url), "utf8");

test("a settled multi-part job writes tickets and continues", () => {
  assert.match(implement, /When the idea is not settled/);
  assert.match(implement, /Do not ask which ticket/);
});

test("a behavior change gets a fresh reader before the commit", () => {
  assert.match(commit, /Before a commit that changes behavior/);
});

test("healthy means every area is 3", () => {
  assert.match(setup, /Healthy means every area is 3/);
  assert.match(setup, /A 2 is not the finish/);
});
