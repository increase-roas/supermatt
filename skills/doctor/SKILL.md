---
name: doctor
description: "Use when Alex says doctor, fix all the repos, organize the Codex folder, or fix 1Password. One command. It assumes he was building a harness, moves the leftover folders out of the way, and asks only when two live checkouts disagree."
license: MIT
---

# Doctor

The command is `doctor`. It assumes the person was building a harness and that the folder in front of it is leftover chats, copies, and one-off repairs. It does not ask which folder, which file, or whether to continue. It asks only when two live checkouts have the same remote and different unpushed commits, because it cannot tell which one was the real direction.

The default folder is `~/Documents/Codex`. `~/.codex` is the app config. This command does not open it.

```sh
doctor
```

That runs `python3 ~/Projects/supermatt/skills/doctor/doctor.py`. A path argument replaces the default folder.

## What it does

The class comes from `classify.py` in this folder. `.git` as a directory is a checkout. `.git` as a file is a worktree. A date in the name decides nothing.

- A child with no git moves into `archive/` in the same folder. The bytes stay. `archive/MANIFEST.tsv` records the old path and the new path. A symlink stays where it is.
- A checkout, a worktree, and a nest stay. Removing them would delete files, and a file delete never runs.
- `archive` itself stays. Run `doctor` again and it does not move the archive.
- A checkout is fetched. When it is clean and behind its remote, it is fast-forwarded.
- When `AGENTS.md` and `CLAUDE.md` in a checkout both carry rules, load and follow `improve-agent-setup` and do the fixes it ranks. Do not lay the client-project skeleton onto a tool repo or onto the harness.

## 1Password

1Password stays the read-only Connectors route on the `1password` card, account `_1password_forby-paon`. After the folder pass, list the vaults. Do not print a secret, do not read a local env file, and do not write a vault item. That account cannot write. If the list fails, retry it once. If it fails again, say the route is down.

## Done

Done when the folder shows only checkouts, nests, files, and `archive`, the manifest has one row per folder that moved, and the vault list either returned or the retry failed.
