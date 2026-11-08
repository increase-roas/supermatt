---
name: adopt-harness
description: "Use when an identifiable external wiki, plugin, skill pack, zip, or agent harness is being compared with ours and Alex asks what it includes or lacks, whether we missed or left out anything from it, or which of its capabilities we should add. Also when he supplies that source or asks if its parts are better than ours. For an authorized full adoption, inspect the complete relevant source, account for every actionable part, and implement useful missing improvements in the same turn. A partial list or comparison is not the finish when implementation was requested. Honor narrower requests, such as recommendation-only. For a standalone score of our own repository without an external source, use improve-agent-setup."
license: MIT
---

# Adopt a dropped harness

Someone else's plugin, skill, zip, or GitHub repo of agent skills and rules is a source to mine. Our harness stays the one pack. Take the parts that change an action we miss, rewrite them in our words, and land them in the same turn. Then say what was taken and what was left out.

`improve-agent-setup` scores one repo and does not edit. This skill is the one that edits.

## Our harness

Three owners. Edit the one that already owns the fact. Do not install the dropped pack beside SuperMatt.

| What changed | Owner |
|---|---|
| A workflow, a skill, or how an agent writes | `~/Projects/supermatt` |
| A gate (spend, a customer send, a delete, DNS) | `~/.agents/skills/alex-director/references/gates.md` |
| Which skill runs or what one agent must know on every task | That agent's instruction source in `~/.agents/instructions/<agent>.md`; use `~/.agents/tools/unify/build_instructions.py` to plan and apply supported generated copies |

## Steps

1. **Keep the whole request and its authority.** If this skill starts because the user asks what a source is missing or what it includes, treat later questions about omissions, feature examples, or next steps as continuations of that task. Preserve the finish and the authority: implement and prove useful gaps when the active request authorized improvement/adoption; a standalone explanation, comparison, or read-only repo score remains read-only. A follow-up never silently upgrades advice into installation; an explicit later scope change or narrowing takes effect immediately.
2. **Get the source for the requested scope.** For a full adoption, retrieve the complete relevant index and packages, not only the first promising page or a search excerpt. For a bounded question or recommendation-only request, read only enough source to answer that scope. A local folder is read in place. A zip unpacks under `/tmp`. A GitHub link clones into `/tmp` (`git clone --depth 1`). Do not edit the dropped copy, and do not copy it into `~/Documents`.
3. **Account for the full adoption.** When the user authorizes a full adoption, inventory the source's skills, workflows, start-file rules, capabilities, checks, and anti-patterns. Classify each item as already covered (with the owning path), useful and adopted, inapplicable, or blocked with a concrete reason. Skip course narrative, marketing, and demos. For a narrower request, stay within its limit: return the requested selection or explanation without completing a full inventory or implementing changes the user excluded.
4. **Match each candidate to our owner.** If we already do it, leave theirs out. If ours is stricter, leave theirs out. A gate is stricter: never weaken the $10 spend allowance, a customer send, a user delete, or the never-rules (ad account, sub-account, campaign, file, DNS). Never add a new stop that waits on Alex.
5. **Rewrite the winner** with `writing-for-agents`. One owner. Point at a manifest, a skill description, or a doc we already have instead of pasting theirs.
6. **Prove each taken piece** with one check that can go red. A file that parses is not that check. Use the row that matches the piece:

   | Piece | Check |
   |---|---|
   | A skill | `writing-for-agents` "Testing a skill": the recorded miss, a fresh rerun, one pressure rerun, and a trigger check. A drop loads this skill. Scoring a repo loads `improve-agent-setup`. |
   | A gate or a guard | That file's existing test, plus one case for the new rule and one nearby case that still runs. |
   | A routing line or an always-on rule | Rebuild the rules and read the generated file. That shows the line shipped. When the line points at a skill, the skill row is the behavior proof. |
   | Code | The project's test for that behavior. `qa` when a person can see it. `code-review` on the diff. |

7. **Review the diff** before calling it working. Six things, each with the evidence from step 6:
   - Each taken line changes an action we missed. Course text stays out.
   - One owner. Generated copies come from the rebuild, not a hand edit.
   - Gates are unchanged or stricter. No new stop that waits on Alex.
   - The trigger check caught the drop and left a repo score alone.
   - The check for that piece passed on this turn.
   - Every leftover is named, with why ours already did it or was stricter.
8. **Commit and push** the repos whose checks passed. Config and this plugin go straight to main. A piece whose check could not run stays uncommitted and is named as not proven.
9. **Report** the taken, already-covered, inapplicable, and blocked items. For each adopted item give its owner and check result. Link the complete source inventory so omissions are reviewable.

Done when the request's scope is complete. For an authorized full adoption, account for the full relevant source and prove every useful missing piece was adopted, or name why it remains unproven. For narrower advice or comparison, deliver only what the user asked for and make no excluded changes. Do not call a partial recommendation a complete adoption when full implementation was requested.
