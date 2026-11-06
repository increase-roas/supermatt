# Agent setup anti-patterns

Each entry names a recurring mistake, how to spot it in a repository or session, and the usual fix. A match is a finding only with cited evidence.

## Architecture

- **Homemade agent.** A custom loop, prompt chain, or orchestration framework does what the host agent and its skills already do. *Spot:* code that calls a model API to plan, pick tools, or loop until done. *Fix:* move the procedure into a skill and let the host run it.
- **Agent where a script would do.** A deterministic job (format, convert, count, sync) runs through a model. *Spot:* a skill or prompt whose steps have one correct output. *Fix:* a script the skill calls.
- **No version control on steering.** Steering files, skills, or prompts live outside git or in an untracked folder. *Spot:* `git status` shows them untracked, or they live only in a host's settings. *Fix:* commit them where the repository can review them.

## Workflow

- **One giant prompt.** A single steering file or skill tries to plan, build, review, and ship. *Spot:* a skill over a few hundred lines covering unrelated phases, or an `AGENTS.md` holding procedures. *Fix:* split by phase into skills with their own triggers; keep `AGENTS.md` to pointers.
- **Author reviews own work.** The agent that wrote the change is the only reader that checks it. *Spot:* no review step, or review run in the implementing context. *Fix:* `/code-review` in a fresh context, or a second model through `docs/agents/cross-model.json`.
- **No validation.** Work is called done without running anything. *Spot:* no test, lint, or type command in a hook or CI; completion claims without command output. *Fix:* wire the repository's own check command into a pre-commit hook or CI job, and QA the running program.
- **Context never reset.** One session carries grilling, spec, implementation, and QA well past the point where reasoning degrades. *Spot:* a phase boundary with no compaction, reset, or handoff. *Fix:* reset or compact at phase boundaries, as `ask-supermatt` describes.

## Scope

- **Too many sources at once.** A task wires several data sources or services in one step. *Spot:* one ticket touching three or more integrations. *Fix:* one source per ticket, each with its own check.
- **Scope creep while building.** Features appear that no spec or ticket asked for. *Spot:* a diff larger than its ticket, or files no ticket names. *Fix:* return extras to `/to-spec` or `/triage` as new work.
- **Built for others first.** The setup serves imagined users before it works for its own maintainer. *Spot:* configuration for hosts or roles nobody runs. *Fix:* remove what no one uses; add it back when someone needs it.

## Context

- **Stale pointer.** A steering file names a path, command, or rule the code no longer has. *Spot:* a referenced path that does not exist. *Fix:* amend the pointer at its source.
- **Contradicting steering.** Two files give opposite instructions. *Spot:* the same topic with different rules in two steering files. *Fix:* keep one owner and point the other at it.
- **No-op padding.** Rules the model follows anyway ("be careful", "write clean code"). *Spot:* a rule no reviewer could fail. *Fix:* delete it.
