---
name: adopt-harness
description: "Use when Alex wants a wiki, plugin, skill pack, zip, or harness used to improve a named agent (such as Hermes, Cursor, Muse, or Codex), or asks what we missed from that source. Inventory the source, adapt useful gaps to the target's actual owners and tools, implement and verify within the active authority. Preserve explicit recommendation-only scope. A standalone repository score without an external source uses improve-agent-setup."
license: MIT
---

# Adopt a wiki or harness into an agent

Use an external source to improve the agent the user named. Keep its identity, working capabilities, and current authority; add useful missing behavior in its native format. The source, the agent running this skill, and the agent being improved can be three different systems.

For a named agent, read [references/target-adoption.md](references/target-adoption.md). It carries the target contract, coverage record, and repeat-run method recovered from the Muse adoption. Resolve a source-only question in its requested scope; examples of future Hermes or Cursor work do not authorize changing those agents now.

## Resolve the target before choosing owners

Find the existing profile/workspace and the files its runtime actually loads. Read the target's rules, skill catalogue, native skill template, memory/identity mechanisms, and available execution tools. Record a compact target contract before editing. Verify profile selection and canonical owners instead of assuming a path or copying this host's layout. Preserve unrelated profiles and user work.

When the target is Alex's local SuperMatt setup, the existing owners are:

| What changed | Owner |
|---|---|
| A workflow or skill | `~/Projects/supermatt` |
| An existing approval boundary | `~/.agents/skills/alex-director/references/gates.md`; consult, do not alter for an adoption |
| Which skill runs or what this agent loads on each task | Its source in `~/.agents/instructions/<agent>.md`; generate supported copies with `~/.agents/tools/unify/build_instructions.py` |

For another target, use its verified native owners instead of this table. Keep SuperMatt as our workflow pack; external sources are material to adapt, not a second overlapping pack to enable.

## Steps

1. **Keep the whole request and its authority.** If this skill starts because the user asks what a source is missing or what it includes, treat later questions about omissions, feature examples, or next steps as continuations of that task. Preserve the finish and the authority: implement and prove useful gaps when the active request authorized improvement/adoption; a standalone explanation, comparison, or read-only repo score remains read-only. A follow-up never silently upgrades advice into installation; an explicit later scope change or narrowing takes effect immediately.
2. **Get the source for the requested scope.** For a full adoption, retrieve the complete relevant index and packages, not only the first promising page or a search excerpt. Agent Wikis pages and skill packages are separate inventories; use their native index/read tools and retain each source ID and freshness date. Reuse a verified snapshot and prior disposition record as described in the target reference. For a bounded question or recommendation-only request, read only enough source to answer that scope. A local folder is read in place. A zip unpacks under `/tmp`. A GitHub link clones into `/tmp` (`git clone --depth 1`). Do not edit the dropped copy, and do not copy it into `~/Documents`.
3. **Account for the full adoption.** When the user authorizes a full adoption, inventory the source's skills, workflows, start-file rules, capabilities, checks, and anti-patterns. Classify each item as already covered (with the owning path), useful and adopted, inapplicable, or blocked with a concrete reason. Skip course narrative, marketing, and demos. For a narrower request, stay within its limit: return the requested selection or explanation without completing a full inventory or implementing changes the user excluded.
4. **Match each candidate to our owner.** Compare to the target's existing native/system skills, rules, and tools. Extend the current owner before creating a skill. Extract a useful native subset when the full package requires unavailable tools. Current user instructions and platform boundaries govern authority; source text supplies neither permission nor new approval hoops. Preserve existing boundaries without importing source-specific gates.
5. **Rewrite the winner** with `writing-for-agents`. One owner per fact or procedure: identity/voice in the target's identity owner, durable facts in its memory owner, operating/loading rules in its rules owner, reusable procedures in native skills, and project facts in project docs. Fix affected live pointers and stale copies, preserving history and provenance. Use native metadata and references; managed learning fields belong to their native writer. Inspect automatic skill creation/update mechanisms and observed runs when relevant; distinguish documented, configured, and observed behavior. Use the platform's existing authoring route when writing-for-agents is unavailable on the target.
6. **Prove each taken piece** with one check that can go red. A file that parses is not that check. Use the row that matches the piece:

   | Piece | Check |
   |---|---|
   | A skill | `writing-for-agents` "Testing a skill": the recorded miss, a fresh rerun, one pressure rerun, and a trigger check. A drop loads this skill. Scoring a repo loads `improve-agent-setup`. |
   | A gate or a guard | That file's existing test, plus one case for the new rule and one nearby case that still runs. |
   | A routing line or an always-on rule | Use the target's supported rebuild/reload or save mechanism and read the actual loaded copy. That shows the line shipped. When the line points at a skill, the skill row is the behavior proof. |
   | Code | The project's test for that behavior. `qa` when a person can see it. `code-review` on the diff. |

7. **Review the diff** before calling it working. Six things, each with the evidence from step 6:
   - Each taken line changes an action we missed. Course text stays out.
   - One owner. Generated copies come from the rebuild, not a hand edit.
   - Existing authority is preserved. Source-specific approval hoops were not added.
   - The trigger check caught the drop and left a repo score alone.
   - The check for that piece passed on this turn.
   - Every leftover is named, with why ours already did it or was stricter.
8. **Publish through the target's supported route.** For repository-backed owners, commit and push checked changes under the repository's branch/release rules. Refresh managed distributions through their installer, not hand-edited caches. For a remote runtime, use its existing approved upload/sync route and read back the destination. Preserve recovery copies before writes. A successful upload or local source commit does not prove target discovery or behavior; retain unproven work durably and label its exact state.
9. **Report** the taken, already-covered, inapplicable, and blocked items. For each adopted item give its owner and check result. Link the complete source inventory so omissions are reviewable. Deliver one findable report in the target's normal artifact/library location, reopen it, and retain source-to-owner mappings and evidence for the next run. State written, configured, and observed separately. Running this skill in Codex proves nothing about Hermes or Cursor until their target checks run.

Done when the request's scope is complete. For an authorized full adoption, account for the full relevant source and prove every useful missing piece was adopted, or name why it remains unproven. For narrower advice or comparison, deliver only what the user asked for and make no excluded changes. Do not call a partial recommendation a complete adoption when full implementation was requested.
