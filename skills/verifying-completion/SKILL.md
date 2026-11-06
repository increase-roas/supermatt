---
name: verifying-completion
description: Prove a claim with fresh evidence before you make it. Use before saying work is done, fixed, passing, working, deployed, or ready, and before committing, handing off, or answering "did it work?"
metadata:
  credits-skill: verification-before-completion
  credits-author: Jesse Vincent
  credits-url: "https://github.com/obra/superpowers"
license: MIT
---

# Verifying Completion

A completion claim is a factual statement about the world: it needs evidence from this turn, not from memory, intent, or another agent's report. Inside `implement` and `implement-spec`, `qa` and `code-review` already do this for the whole change. This skill covers every other claim: a quick fix, a config change, a one-off script, a status answer.

## The gate

Before any claim that something is done, fixed, passing, or working:

1. **Name the check.** Which command, request, or observation would show the claim is true? For a bug, the original reproduction. For a config change, the setting read back from the live system after restart. For a file, its actual contents.
2. **Run it now.** A result from earlier in the session, before the last edit, no longer counts. Another agent's "done" is a claim to verify, not evidence.
3. **Read the output.** Exit code, counts, the specific value. "No errors printed" is not a pass when the check can fail silently.
4. **Claim only what it proved.** State the claim with the evidence beside it ("`npm test`: 237 pass, 0 fail"). If the check passed for part of the work, say which part. If it could not run, say so and say what remains unverified.

## Words that need the gate

"Done", "fixed", "works", "passing", "should work now", "all set", "verified", and any count or status you report. Softening ("should", "probably", "looks good") does not exempt a claim; it signals one that skipped the gate.

## Proportion

One check per claim, the cheapest one that can go red on it. Do not stack a second check for reassurance once the first decisively passed, and do not substitute a weaker check (a parse, a dry run, a log line reading `ok`) for the one that touches the real outcome.
