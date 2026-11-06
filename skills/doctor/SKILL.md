---
name: doctor
description: "Use when the AI left a mess: dated folders, random names, extra checkouts, or unsaved work. doctor cleans it up and gives the folders plain names."
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
- A checkout with work sitting in it is saved and pushed. The person running this command is not asked what that work is.
- An extra checkout git keeps beside the main one is saved, pushed, and then removed once the remote has that same commit. The checked cleanup in `safe-cleanup` does the removal. A folder with no remote stays, because removing it would throw the work away.
- A file that holds a key or a `.env` is left uncommitted and unprinted, and that folder stays.
- A machine name, a date, or a random two-word name is replaced with a short plain name from the folder's own title. The old name is written in `archive/MANIFEST.tsv`.
- `archive` itself stays. Run `doctor` again and it does not move the archive.

## 1Password

1Password stays the read-only Connectors route on the `1password` card, account `_1password_forby-paon`. After the folder pass, list the vaults. Do not print a secret, do not read a local env file, and do not write a vault item. That account cannot write. If the list fails, retry it once. If it fails again, say the route is down.

## Done

Done when the folder shows only checkouts, nests, files, and `archive`, the manifest has one row per folder that moved, and the vault list either returned or the retry failed.
