---
name: improve-agent-setup
description: "Score a repository's agent setup across seven areas. Healthy means every area is 3. A 2 is not the finish. When an area is below 3, do the fix in the same turn."
argument-hint: "[repo path or area]"
license: MIT
---

# Improve Agent Setup

Score how well a repository supports the coding agents that work in it, then name the few changes that would help most. Where `retro` learns from one finished session, this skill surveys the whole repository: its steering files, skills, checks, and conventions, whether or not a session has gone wrong yet. A score on its own changes no project files. Any area below 3 is fixed in the same turn. End with a ranked plan for `/implement`, or a healthy verdict of 21.

If the input is someone else's plugin, skill, zip, or a link to their harness, this is the wrong skill. Load `adopt-harness`. That one merges the better parts into our harness in the same turn.

## Principles

- **Evidence over checklists.** Every score cites a path, a line, a command output, or the absence of something you looked for. A rubric row you cannot ground stays **unscored**, not guessed.
- **The agent is the reader.** Judge each file by what an agent working here would do differently because of it. Use the `writing-for-agents` terms: a rule another artifact already enforces is **duplication**, a rule the model follows by default is a **no-op**.
- **Small and owned beats complete.** A lean `AGENTS.md` with context pointers, one guardrail that runs, and skills with sharp triggers outscore a large setup nobody maintains.
- **Healthy means every area is 3.** A 2 works and is not the finish. Lean, current, enforced by a check, and maintained at its source is the finish. Do not stop at 2. Do not ask him to say that again.

## Process

### Step 1: Map the setup

Read `AGENTS.md` and `CLAUDE.md` at the root and below, `docs/agents/`, any `GLOSSARY.md` and ADRs, repository skills, hook and lint configuration, CI workflows, and the commands used to build, test, and check the code. Note which host-specific files exist and which hosts they serve. Record what is generated or synced from elsewhere: those files are fixed at their source, not here.

Done when: every steering file, skill, and guardrail in scope is listed with its role, and every unknown is named.

### Step 2: Score the seven areas

Score each area 0 to 3 using [RUBRIC.md](RUBRIC.md): structure, agent architecture, skills, scope, context, safety, workflow. Check the setup against [ANTI-PATTERNS.md](ANTI-PATTERNS.md) as you go, and record every match with its evidence.

Done when: each area has a score with cited evidence, or is marked unscored with the missing evidence named.

### Step 3: Rank the fixes

For each area below 3, propose the smallest change that raises it to 3, with the file it touches, the anti-pattern it removes, and the cost. Prefer a deterministic check over a new instruction, an amended file over a new one, and a pointer over pasted content. Rank by benefit against effort. Do every one of those fixes in the same turn. Changes to code structure belong in `/improve-architecture`, file placement in `/improve-file-structure`, and slow or low-value tests in `/improve-tests`: name the handoff instead of planning that work here.

Done when: every proposed fix names its file, its evidence, and the score it should move.

### Step 4: Report and hand off

Write the report in the conversation using the template in [RUBRIC.md](RUBRIC.md), unless the user asks for a saved file. When any area is below 3, do those fixes in this turn. Do not ask which, and do not wait for him to say fix it. A report that stops at 2 is not the finish.
