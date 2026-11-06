---
name: fix-repos
description: "Use when a folder of repositories or Codex project folders is a pile of dated copies, worktrees, and one-off repairs, or Alex says fix all the repos, consolidate them, or update them one by one. Walks each folder, treats the layout as wrong until a check says otherwise, and fixes that one before the next."
license: MIT
---

# Fix the repos

A folder like `~/Documents/Codex` collects one checkout, a dated dump, and a worktree for every chat. The pass assumes that pile is wrong and fixes one child before it opens the next. `~/.codex` is the app config. This skill does not open it.

The classes come from `~/Projects/supermatt/skills/fix-repos/classify.py`. Run `python3 ~/Projects/supermatt/skills/fix-repos/classify.py <parent>` on the parent, or on a nest. A date in the name is not a class. `.git` as a directory is a checkout. `.git` as a file is a worktree.

## One child

Take the children in this order: misplaced, worktree, primary, dump, nest. A file is `skip` and stays.

- **misplaced.** A checkout sitting inside a folder named `worktrees`. Leave it. Name its remote and whether another primary checkout has the same remote. Do not delete it and do not move it in this pass.
- **worktree.** Read the gitdir. When `git status` is clean and `git ls-remote` shows the branch tip equals `HEAD`, load and follow `safe-cleanup` and use its checked executor. When either check fails, leave the folder and name the unsaved path. Do not `rm` it.
- **primary.** `git fetch`. When the worktree is clean and the branch is behind its remote, fast-forward it. When `AGENTS.md` and `CLAUDE.md` both carry rules, or the same skill exists twice, load and follow `improve-agent-setup` and do the fixes it ranks. Do not run the client-project skeleton on a tool repo or on the harness.
- **dump.** No `.git`. Leave it. If it holds source that is not already in a primary checkout, name that path. A dated folder is not junk by its name.
- **nest.** A folder named `worktrees`, a name ending in `-worktrees`, or a folder with no git of its own that directly contains a checkout or a worktree. Classify its children with the same rules, then come back.

## Stops

A file delete, a campaign delete, an ad-account delete, a sub-account delete, and a DNS change never run. Client data and anything under `~/Documents/BUSINESS 1-4` stay. The two gates in `~/.agents/skills/alex-director/references/gates.md` still stop the pass.

## Done

Done when every child has a class, and each one is either fixed or left with the check that failed. Then start the next child. Re-running the classifier on a fixed parent prints the same class for anything this pass did not change.
