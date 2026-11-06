# Agent setup rubric

Score each area 0 to 3. Cite the evidence for every score.

| Score | Meaning |
|---|---|
| 0 | Missing, or actively misleads the agent |
| 1 | Present but weak: stale, bloated, unwired, or contradicted elsewhere |
| 2 | Works: an agent finds what it needs and the checks run |
| 3 | Strong: lean, current, enforced by checks, and maintained at its source |

## 1. Structure

Can an agent find the right file fast? Look for a short root `AGENTS.md` or `CLAUDE.md` that follows the start-file sections in `writing-for-agents` (project, stack, key files, unwritten conventions, limits, a skill pointer, tone only when the repo writes for people), a clear home for domain terms (`GLOSSARY.md`) and decisions (ADRs), and generated output kept out of authored folders. A 2 needs every steering file reachable from the root file.

## 2. Agent architecture

Does the repository use the host agent, or fight it? Look for homemade agent loops, prompt chains, or orchestration frameworks where the host's agent, skills, and subagents would do. A 2 needs every custom agent layer to justify a capability the host lacks.

## 3. Skills

Are repeated procedures captured as skills with sharp triggers? Look for procedures pasted into `AGENTS.md` that belong in a skill, skills whose description does not say when to use them, and skills that duplicate each other. A 2 needs each repeated workflow in one skill, triggered by its description.

## 4. Scope

Is each piece of work narrow enough to finish and check? Look for tasks that pull many data sources at once, features added without a plan, and specs or tickets that never close. A 2 needs a written plan or ticket for multi-step work and one data source wired at a time.

## 5. Context

Does the agent get enough input without noise? Look for steering files padded with no-ops, missing context pointers, stale paths, and long sessions that never reset between phases. A 2 needs every steering rule to change behavior and every pointer to resolve.

## 6. Safety

Can the agent do damage the setup does not catch? Look for secrets in tracked files, no secret scan, unguarded destructive commands, and production credentials reachable from a dev session. A 2 needs a secret scan in a hook or CI and no live credential in the repository.

## 7. Workflow

Is the work checked by something other than its author? Look for a pre-commit hook or CI job that runs lint, type, and test commands, review by a fresh reader, and QA that drives the running program. A 2 needs one guardrail that runs the repository's own checks and a review step independent of the implementer.

## Report template

```markdown
## Agent setup: <repo>, <date>

**Overall: <sum>/21** (<healthy | localized | systemic>)

| Area | Score | Evidence |
|---|---|---|
| Structure | n/3 | <path or finding> |
| Agent architecture | n/3 | ... |
| Skills | n/3 | ... |
| Scope | n/3 | ... |
| Context | n/3 | ... |
| Safety | n/3 | ... |
| Workflow | n/3 | ... |

### Anti-patterns found
- <name>: <evidence>

### Ranked fixes
1. <fix>: <file>, moves <area> from n to m, cost <small | medium | large>

### Unscored or unknown
- <area or file>: <missing evidence>

### Next step
<recommended fix and the `/implement` command for this host>
```

The verdict is **healthy** when every area scores 3. **Localized** when one or two areas fall below 3. **Systemic** when three or more do. A 2 is not healthy.
