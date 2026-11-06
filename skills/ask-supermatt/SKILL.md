---
name: ask-supermatt
description: Ask which skill or flow fits your situation. A router over the skills in this repo.
argument-hint: "[your situation]"
license: MIT
---

# Ask SuperMatt

You don't remember every skill, so ask.

Skills are named here as `/name`. A bare `/code-review` on the Claude Code plugin is Claude Code's bundled review, not this one, so the plugin form is `/supermatt:name`. When a flow below names the next skill, load and follow that skill through the host's skill mechanism. Do not tell the user to type it. Preserve arguments.

A **flow** is a path through the skills. Most paths run along one **main flow**, and five **on-ramps** merge onto it. Everything else is standalone, or a vocabulary layer that runs underneath.

## The main flow: idea → ship

The route most work travels. You have an idea and want it built.

1. **Is the idea unsettled?** Use **`/grill-with-docs`** when there is a project directory for recording decisions in `GLOSSARY.md` and ADRs. Use **`/grill-me`** for an unsettled idea without project files. When the outcome and decisions are settled, go straight to step 3.
2. **Branch: can you settle every question in conversation?** If a question needs a runnable answer (state, business logic, a UI you have to see), detour through a prototype, bridged by **`/handoff`** in both directions (the prototype is a side task forked mid-phase, one of the narrow cases `/handoff` is for; see Phase boundaries):
   - **`/handoff`** out, then open a fresh session against that file,
   - **`/prototype`** to answer the question with throwaway code,
   - **`/handoff`** back what you learned, and reference it from the original idea thread.
3. **Branch: does the build have three or more parts, or need multiple sessions?**
   - **Yes** → **`/to-spec`** (turn the thread into a spec), then **`/to-tickets`** to split it into independently green tracer-bullet tickets, each declaring its **blocking edges**. For per-ticket work, start **`/implement`** on a ticket whose blockers are done, resetting context between tickets with the host's native control or a fresh session. On a local tracker the tickets are files under `.scratch/<feature>/issues/`; hosted trackers use native blocking links when available, otherwise the configured `Blocked by:` fallback. For a whole-spec build, use **`/implement-spec`**: native subagents work the ready frontier in separate worktrees and integrate into one branch for a single PR, without Herdr. It runs QA and review over the whole spec and leaves shipping to you. Keep tracker issues open until the default-branch merge; dependencies inside that run advance when their commits reach the integration branch.
   - **No** → **`/implement`** right here, in the same context window.

   Both implementation flows drive **`/tdd`** internally (focused checks during red-green cycles, then the full required gate for a completed behavior), commit, run **`/qa`** in a fresh subagent or session when available (otherwise in the current context with the independence gap reported), and close out with **`/code-review`**, a three-axis review (Standards, Spec, Adversarial) of the diff. QA drives the running program the way its user would, a terminal program in tmux or a web app in a browser, and checks every requested behavior. `/code-review` reads `docs/agents/cross-model.json`: `host-only` keeps every reader on the current host, `auto` uses only hardened Claude or Codex peers, and explicit modes can select Claude, Codex, Cursor Agent, or OMP under their disclosed limits. `/implement` verifies each ticket; `/implement-spec` verifies the combined integration branch against the whole spec. Follow-up QA and review carry the prior reports and check the fixes and affected behavior. When the work goes up as a pull request, **`/pr`** shapes the body: a summary diagram, before/after evidence, and the merge danger. Reach for **`/tdd`** on its own when you just want to build a concrete behaviour test-first without a full spec, **`/qa`** on its own whenever you want to see a branch actually work before anyone reads its code, and **`/code-review`** on its own whenever you want to review a branch or PR against a fixed point.

4. **Ship.** **`/fix-findings`** applies the findings of the last review or check (a finding's text works too, from another session). **`/refactor the changes on this branch since origin/main`** cleans up what the branch added without changing behavior, and stops when the code is already clean. **`/ship-pr`** commits, pushes, opens the pull request, diagnoses and repairs CI within bounded attempts, squash merges only on green checks, verifies post-merge workflows, and closes the issues the branch finished, which unblocks the tickets waiting on them. **`/babysit-pr`** is the same road without the merge: it opens the PR when the branch has none, handles review feedback before CI, keeps the branch current, and stops at a ready PR for you to merge; run it again on the same PR to resume with the same budgets. Both recover CI through **`/recover-ci`**: two repair cycles and one transient rerun. **`/commit`** commits on the current branch when you are not ready to ship. Then **`/retro`** on the session, so the next one starts from what this one learned.

Both implementation flows consult `codebase-design` before changing data contracts, state transitions, shared mutable state, or retryable effects. Adversarial review checks duplicate execution and recovery after interruption against the intended contract.

### Unattended: `/orchestrate`

When the issues are triaged and you want the queue worked without you, **`/orchestrate`** runs the main flow per issue from inside a Herdr pane in Claude Code, Codex, Cursor, or OMP, when Herdr can start that host's corresponding CLI. It reads GitHub issues or the configured local Markdown queue; local tickets stay in the main checkout while code ships through GitHub PRs. Its workers and every restart use the same harness that started it. An `orchestrate` run with a lane count, for example 3, works that many issues in parallel, each in its own pane and git worktree. A branch that conflicts with one merged before it loads and follows `resolving-merge-conflicts`. It opens a worker session in the lane's pane for each phase: `triage` for an untriaged bug, `implement`, `fix-findings` for what the review left, `refactor`, `ship-pr`, then a report-only `retro`. Retrospective candidates return to the operator; applying them is separate work, with no automatic lessons PR or external edits. It answers the workers' questions and dialogs itself through `what-would-you-do`, verifies each spec once its tickets close, and notifies you only when the queue is done or it needs you.

Claude Code and Codex keep their phase-specific model policies. Cursor and OMP inherit the active session's authoritative model ID, or the harness default when that ID is unavailable. Cursor and OMP require matching Herdr integrations for durable session evidence and discoverable SuperMatt skills. Shipping includes bounded CI recovery and follow-up repair PRs for failed post-merge workflows. A default-branch failure holds further merges until recovery succeeds; exhausted recovery parks with evidence. Shipping keeps the active worktree through verification and reporting; the orchestrator stops the worker before removing that worktree.

An explicit `orchestrate` run delegates its listed worker skills only within that run, under the [orchestrator dispatch contract](../../references/harnesses.md#orchestrator-dispatch). Every other flow loads the next skill through the host's skill mechanism. Do not tell the user to type it. Safety gates stay as they are.

### Context hygiene

Keep steps 1-3 in **one unbroken context window** so the grilling, spec, and tickets all build on the same thinking. For multi-session builds, each `/implement` starts fresh, working from its ticket; single-session builds continue in the current context. Run `/retro` in the session it examines before resetting context; afterward, provide that session's log instead. For `/implement-spec`, retain the worker session references alongside the coordinator's log.

The limit is the **[smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone)**, the window (about 150k tokens) within which the model still reasons sharply. Read the host's context meter when it shows one. Do not estimate live context by reading the tree. If a session approaches the limit before `/to-tickets`, use the host's compaction control at the nearest phase boundary. If none exists, create a handoff and start a fresh session (see Phase boundaries).

A side question gets a short answer, then you return to the task you were on. It does not replace the objective or restart the plan.

## On-ramps

A starting situation that generates work, then merges onto the main flow.

- **No idea yet, and you want candidates** → **`/ideate`**. It grounds itself in the repo when available, otherwise in external sources and explicit reasoning, generates ideas through six frames, and has a fresh subagent or session try to refute each one. When fresh context is unavailable, it performs the check itself and reports the missing independent verifier. It writes the ranked **survivors** to `docs/ideation/`, or reports that no idea passed. Each survivor carries a standalone prompt with its original evidence that takes it into **`/grill-with-docs`** in a fresh session, where the main flow starts. It finds *what* to build; `/grill-with-docs` shapes the one you pick.

- **Bugs and requests piling up** → **`/triage`**. It moves issues through triage roles and produces agent-ready issues, which **`/implement`** later picks up. When you explicitly delegate decisions, it records its choices within your issue or queue scope; missing facts and separate approval gates still block dependent work.

  Triage is for raw issues that are **not already agent-ready**: bug reports, incoming feature requests, anything that arrives raw. Specs and tickets that `/to-spec` and `/to-tickets` produced are already agent-ready, so **don't triage them**; `/triage` leaves them out of its queue.

- **Something's broken** → **`/diagnosing-bugs`**. Fix it in the same turn. For the hard ones: the bug that resists a first glance, the intermittent flake, the regression that crept in between two known-good states. It refuses to theorise until it has a **tight feedback loop** (one command that already goes red on *this* bug), then fixes with a regression test, checks the reported symptom is gone in the running program with **`/qa`**, and reviews the fix with **`/code-review`**. When the cause depends on a product, an API, a version, or a platform limit, run `research-with-sources`: Exa, and that company's official docs, then fix. After the fix, run **`/retro`** in the same session to identify what would have prevented the bug. When the finding is a missing test seam, use **`/improve-architecture`** and keep going.

- **An AI agent run failed** (stuck, looped on a tool call, used the wrong tool or arguments, ignored its instructions, or said done without finishing) → **`/diagnosing-agent-runs`**. It reconstructs the run from its traces, tests the runtime contract behind the first deviation (tool schema, MCP error kind, permissions, instruction loading, turn limits, resume), makes the smallest repair, and verifies the task outcome as PASS, FAIL, or PENDING without replaying uncertain effects. A failure inside ordinary tool or harness code goes to **`/diagnosing-bugs`**.

- **A huge, foggy effort: a greenfield project or a huge feature build, too big for one session** → **`/wayfinder`**, the most cognitively demanding flow here. When the way from here to the destination isn't visible yet, it charts a **shared map** of **decision tickets** on the issue tracker and resolves them one at a time, producing **decisions, not deliverables**, until the fog is pushed back and the way is clear. Where the tracker lacks exclusive acquisition, one recorded coordinator grants session-owned claims before tickets run in parallel. Where **`/grill-with-docs`** sharpens an idea you can hold in one session, wayfinder is for the idea you can't, and it's slower and denser, so save it for exactly that, never a well-scoped feature.

  When the map clears, **it hands off, it doesn't build**: merge onto the main flow at **`/to-spec`**, which collapses the map's linked decisions into a buildable plan, then `/to-tickets` and `/implement` as usual. Looping the map straight into `/implement` skips that collapse and throws the linked detail away, so go straight to `/implement` only when the effort turned out genuinely small.

## Codebase health

Not feature work, just upkeep.

- **`/retro`** looks back at a finished session (this one by default) and suggests changes to the agent's **environment**: automated checks, context pointers, coding-standards rules, stale or contradictory instructions, a leaner `AGENTS.md`. Run it after a session that went badly, so the next one doesn't repeat the mistake.

- **`/improve-architecture`** runs whenever you have a spare moment to keep the codebase good for agents to operate in. When the architecture is healthy, it says so and stops. Otherwise it maps the structure, lists **deepening opportunities**, grills you on the one you pick, designs its interface, and writes a plan that merges onto the main flow at step 3 (`/to-spec`, or `/implement` for a small change). It's the survey that finds the candidates; **`/codebase-design`** (below) is the bench you design the chosen one on.
- **`/refactor`** is the code-level counterpart: complexity, duplication, naming, and dead code inside modules whose boundaries are fine. It assesses first and stops when the code is clean, and it refuses to change code no test covers until you decide. Before a mechanical sweep, it checks automation against verified manual examples in scratch.
- **`/improve-file-structure`** handles file placement: crowded folders, scattered feature files, unclear ownership, and unnecessary nesting. It respects language and framework conventions, stops when the layout is healthy, and produces a move map and verification plan for `/implement` (or `/to-spec` for a multi-session migration, retaining the approved map in the spec and linking it from each affected ticket). It changes no project files. Use `/improve-architecture` when responsibilities or interfaces need redesign, and `/refactor` for code-level cleanup.
- **`/improve-agent-setup`** scores the repository's agent setup (steering files, skills, guardrails, context, scope, safety, workflow) across seven areas, stops when it is healthy, and otherwise ranks the fixes into a plan for `/implement`. It is the repository-wide survey; `/retro` learns from one finished session. It does not edit.
- **`/doctor`** checks and repairs Codex setup, saves eligible unfinished work separately, and puts closed leftover folders away under plain names. It keeps active paths and worktrees in place.
- **`/adopt-harness`** runs when a plugin, skill, zip, or a link to someone else's harness shows up, or when the question is whether anything in it is better than ours. It scans that pack, merges the better parts into our harness, and proves each taken piece before the commit. A comparison is not the finish. A piece whose check could not run stays uncommitted.
- **`/improve-tests`** cuts a slow or bloated test suite to the tests that catch real bugs: it times the suite first, deletes or demotes the tests that catch nothing, fixes slow setup, and proves each cut keeps the checks that matter.

## Vocabulary underneath

Two model-invoked references that run *beneath* the other skills, each the single source of truth for its vocabulary. Reach for them directly when the **words**, not the process, are the problem; or let the skills above pull them in.

- **`/domain-modeling`**: sharpen the project's *domain* language: challenge a fuzzy term, resolve an overloaded word ("account" doing three jobs), record a hard-to-reverse decision as an ADR. It's the active discipline `/grill-with-docs` drives to keep `GLOSSARY.md` a clean glossary.
- **`/project-lore`**: the facts the code cannot show. Before a plan or a bug fix, read `docs/lore/` for the files you will touch. When you learn a pitfall or a why, record it there. Before a commit, check the diff against entries whose `code:` path matches. Words stay in `GLOSSARY.md`.
- **`/codebase-design`** is the deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality) for designing a module's *shape*: a lot of behaviour behind a small interface at a clean seam. `/tdd` and `/improve-architecture` both speak it. Its state-contract guidance covers valid states, input validation, shared writes, and recovery for implementation flows.

## Phase boundaries

A **phase** is a chunk of work inside a session: the grilling, the implementation, the QA. At the **boundary** between two of them you have five options, and picking between them is the fuzziest decision in this whole map:

- **Continue**: stay put. Costs nothing, loses nothing.
- **Reset context**: use the host's native reset control, such as `/clear` where supported, or start a fresh session when no reset exists.
- **`/handoff`** writes a portable markdown file and updates `.supermatt/session.md` so the next session can resume. Use it for a **new harness**, a **new directory**, a **colleague**, a side task **mid-phase**, before a compact, and before a multi-step task stops. A checkpoint is a save. The job continues.
- **Subagent**: send a tightly-scoped task to its own window and get a report back.
- **Compact**: use the host's native compaction control, such as `/compact` where supported. If none exists, hand off to a fresh session. This is the **default**, at the bottom of the tree rather than the first reach.

Read [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) for the ordered tree: the five questions, the reasoning behind each branch, and why the primary-source cost makes **Continue** the one to rule out first. Make the decision **at** a boundary; mid-phase, continue, split the rest into subagents, or fork a side task with `/handoff`.

## Standalone

Off the main flow entirely.

- **`/grill-me`**: the same relentless interview as `/grill-with-docs`, but **stateless**: it saves nothing locally and builds no `GLOSSARY.md`. Reach for it when you are **not working in a working directory** (sharpening a plan, a design, a piece of writing, anything with no repo under it). If you are in a working directory, use `/grill-with-docs` instead: it runs the same interview and leaves a paper trail, so it is strictly the better one.
- **`/grilling`** is the interview primitive itself: rounds, the frontier, facts are the agent's job and decisions are yours. `/grill-me` and `/grill-with-docs` are the two named ways in, and `/triage`, `/wayfinder` and `/improve-architecture` all run it internally. Reach for it directly only when you want the interview with no wrapper around it.
- **`/resolving-merge-conflicts`** works an in-progress merge or rebase conflict hunk by hunk, resolving by **intent** traced to each side's primary source rather than by picking lines, then finishes the operation. It never runs `--abort`. Reach for it when you are already mid-conflict; `/orchestrate` and `/implement-spec` also use it when integrating work stops on conflicts.
- **`/prototype`** is a small, throwaway program that answers one design question: does this state model feel right, or what should this UI look like. Two rules, skills, or hooks that can send the same situation to different next steps are the logic branch: follow LOGIC.md before adding another rule or another owner. Throwaway is a constraint on how the code is written, not a promise to destroy it: the answer folds into the real code, and the prototype itself is kept as a **primary source** on a `prototype/<name>` branch out of main, pointed at from the issue that asked the question (or the handoff, before an issue exists). It's the detour in step 2 of the main flow, but reach for it any time a design question is hard to settle on paper.
- **`/research`**: delegate reading legwork to a **background agent** when available, otherwise use a fresh session or research directly with the independence gap reported. It reads this repo first, uses evidence the caller already supplied, then investigates against **primary sources**, and leaves a cited Markdown file in the repo. Keep working while delegated research runs. The file it produces is something to take *into* the main flow at `/grill-with-docs`, since research feeds the thinking rather than replacing it.
- **`/to-questionnaire`** comes in when the thing blocking you isn't in your head or the codebase but in **someone else's**, and it writes them a questionnaire to fill in. It's the inverse of `/grill-me`: instead of interviewing you about the subject, it interviews you about the **send** (who it's going to, what you need back) and aims the questions at the gap. What comes back is material for `/grill-with-docs`.
- **`/wait-what`** is the corrective for a message that didn't land. Use it mid-conversation, inside any other skill, and the agent re-pitches what it just said with the context you were missing, in plain English, using the `GLOSSARY.md` vocabulary. It works after the fact; `/grill-with-docs` is the upfront cure, because a shared language agreed early is what stops the jargon arriving at all.
- **`/what-would-you-do`** explains a pending question, weighs each option, and recommends one. On a choice that is not a gate (a charge over $10, or a message a customer would receive) it then does the recommended option and says what it chose. A charge of $10 or less is done and reported. A gate stops after the recommendation. A jury line is offered only when you asked for a jury or the decision is a gate.
- **`/jury`** puts a hard decision to a panel of 3 or 5 independent seats: validated blind votes, one anonymous review round, and one committed verdict with the dissent and a first action. If no valid blind vote succeeds, it reports the jury unavailable instead of inventing a verdict. Its external seat follows `docs/agents/cross-model.json`; `host-only` keeps the full panel on host subagents.
- **`/verifying-completion`** is the gate before any done, fixed, or passing claim outside the main flow: name the check, run it now, read the output, and claim only what it proved. The model reaches for it by itself; inside `/implement`, `/qa` and `/code-review` already cover it.
- **`/dependency-vetting`** checks that a package is authentic before anything installs, adds, or recommends it. The model reaches for it by itself whenever a task adds a dependency.
- **`/teach`**: learn a concept over multiple sessions, using the current directory as a stateful workspace.
- **`/writing-for-agents`** is the reference for writing documents agents consume: skills, AGENTS.md, pointed-at docs.

## Precondition

**`/setup-supermatt-skills`**: run before your first engineering flow to configure the issue tracker, triage labels, doc layout, and `docs/agents/cross-model.json` peer policy that `code-review` and `jury` use. Custom issue trackers also work.
