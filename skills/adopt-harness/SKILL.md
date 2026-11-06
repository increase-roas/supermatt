---
name: adopt-harness
description: "Use when a GitHub harness already does it, or Alex asks what is missing. Also when he drops a plugin, skill, zip, or rules pack, or asks if anything in it is better than ours. Scan it and merge the better parts in the same turn. A comparison is not the finish."
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
| Which skill runs, or a rule every task must know | `~/.agents/skills/alex-director/references/controllers.md`, then `~/.agents/instructions/shared.md` |

## Steps

1. **Get the bytes.** A local folder is read in place. A zip unpacks under `/tmp`. A GitHub link clones into `/tmp` (`git clone --depth 1`). Do not edit the dropped copy, and do not copy it into `~/Documents`.
2. **List the pieces that change an action.** A start-file outline, a skill, a rule, a check, an anti-pattern. Skip course narrative, marketing, and demos. One line each: the action it changes.
3. **Match each piece to our owner.** If we already do it, leave theirs out. If ours is stricter, leave theirs out. A gate is stricter: never weaken the $10 spend allowance, a customer send, a user delete, or the never-rules (ad account, sub-account, campaign, file, DNS). Never add a new stop that waits on Alex.
4. **Rewrite the winner** with `writing-for-agents`. One owner. Point at a manifest, a skill description, or a doc we already have instead of pasting theirs.
5. **Prove each taken piece** with one check that can go red. A file that parses is not that check. Use the row that matches the piece:

   | Piece | Check |
   |---|---|
   | A skill | `writing-for-agents` "Testing a skill": the recorded miss, a fresh rerun, one pressure rerun, and a trigger check. A drop loads this skill. Scoring a repo loads `improve-agent-setup`. |
   | A gate or a guard | That file's existing test, plus one case for the new rule and one nearby case that still runs. |
   | A routing line or an always-on rule | Rebuild the rules and read the generated file. That shows the line shipped. When the line points at a skill, the skill row is the behavior proof. |
   | Code | The project's test for that behavior. `qa` when a person can see it. `code-review` on the diff. |

6. **Review the diff** before calling it working. Six things, each with the evidence from step 5:
   - Each taken line changes an action we missed. Course text stays out.
   - One owner. Generated copies come from the rebuild, not a hand edit.
   - Gates are unchanged or stricter. No new stop that waits on Alex.
   - The trigger check caught the drop and left a repo score alone.
   - The check for that piece passed on this turn.
   - Every leftover is named, with why ours already did it or was stricter.
7. **Commit and push** the repos whose checks passed. Config and this plugin go straight to main. A piece whose check could not run stays uncommitted and is named as not proven.
8. **Report** the taken and left-out table, and for each taken piece the command and the result.

Done when every piece is either proven and pushed, or named as left out or not proven.
