---
name: doctor
description: "Use when asked to clean up folders an agent left behind, save unfinished work safely, or check and repair a host's setup. Any folder a person looks at."
license: MIT
---

# Doctor

When someone asks to clean up after an agent, choose the path, run the check, and make the eligible repairs in the same turn. Use `doctor.py` beside this skill. For example, `python3 -B /path/to/doctor/doctor.py --dry-run "/path/to/folder"`. The person can ask in ordinary language or invoke this skill through their host.

## Folders and unfinished work

1. Use the folder they named or are looking at. Use `~/Documents/Codex` only when they did not name one. Start with `--dry-run`. Carry any excluded paths into each targeted run with `--exclude PATH`. Use absolute exclusions when switching targets. Javar paths, including Javar Testing, stay out of scope. Inspect only the requested area.
2. For a collection, inventory the likely leftovers and check which paths are still in use. Check open sessions or workspaces through the host's available read-only route, plus any project pointers that name the path. Treat a date or generated name as a clue. For a closed loose folder with no live references, preview its individual path with `--archive --dry-run`, then run it with `--archive`. Doctor keeps the entire folder under a plain name in the sibling `archive` and records where it went. If a run stops after recording a move and leaves the source in place, retry that same path. Keep active, referenced, linked, or uncertain paths in place and say why.
3. For each in-scope checkout with unfinished work, run its explicit path. Doctor saves eligible unstaged text on a separate snapshot branch and lists held nonignored paths with reasons. It counts ignored paths separately. When a checkout needs its own commit checks, keep the files in place and explain that its normal workflow applies. Git history, the original index, and checkout paths stay in place. Doctor publishes the snapshot only when it can verify the starting commit on the matching remote branch and then read back the snapshot commit. A local snapshot is a local save. Doctor also checks the current commit's remote status when there is no new snapshot to make. Keep linked checkouts in place, even when a snapshot reaches the remote.
4. Report what moved, what saved locally or reached the remote, and what still needs attention. Use the archive's completed rows and the remote commit readback as proof. Keep unmatched plans, skipped paths, and tool errors visible.

## Codex and connected tools

1. For a Codex setup request, target `~/.codex` or the active `CODEX_HOME`. Doctor announces the start of Codex's native diagnostic, gives it up to 75 seconds, and reports known check statuses. It expects installation, configuration, sign-in, and provider reachability statuses before reporting overall health. The diagnostic can initialize temporary runtime helpers. Doctor stops its process group on timeout or when the operator stops the command. If the diagnostic is missing, times out, or returns an incomplete report, report the exact gap and use the host's supported read-only check for the affected setting. Use the reported issue to choose the owning setup procedure. When a supported settings repair is in scope, load and follow the host's Codex settings procedure, then verify the changed setting where Codex uses it. Keep platform safety and unrelated settings intact.
2. If the request includes 1Password health, read the local `1password` tool card and list vaults on its dedicated read-only account. Report whether the route returned. Retry a transient error once on the same route. Keep credentials and item contents out of the output, and leave vaults untouched. Report when the host lacks the registered route. The folder command itself does not call 1Password.
