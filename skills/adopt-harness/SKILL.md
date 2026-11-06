---
name: adopt-harness
description: "Use when Alex drops a plugin, a skill, a zip, or a link to someone else's agent harness, GitHub skill repo, or rules pack, or asks if anything in it is better than ours. Scan it and merge the better parts into our harness in the same turn. A comparison is not the finish."
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
5. **Apply, commit, and push** the repos that changed. Config and this plugin go straight to main.
6. **Report** a short table: taken (their section, our file) and left out (why).

Done when every piece is either in our owner or named in the left-out list, and the commits are pushed.
