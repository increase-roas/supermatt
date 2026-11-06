---
name: project-lore
description: "Use when a repo has docs/lore, or when the work surfaces a business rule, a pitfall, or a why that code, types, tests, and git history cannot show. Consult it before planning or fixing. Record the new fact. Before a commit, check the diff against entries whose code path matches. Vocabulary stays in GLOSSARY.md."
license: MIT
---

# Project lore

Lore is what a competent engineer cannot recover by reading the current code, the types, the tests, and the git history. A function's behavior, a structure the code already shows, and a fix already visible in git are not lore. Do not record them.

Store it in `docs/lore/<area>/`. A pitfall goes in `pitfalls.md`. A rule or a why goes in `business-rules.md`. Each entry is a heading, then one line: `` `code:` `` path, optional `→ symbol`, `` `updated:` `` date, `` `status:` `` `active`, `resolved`, or `obsolete`. The date is today's real date.

Words stay in the repo's glossary. Read `docs/agents/domain.md` when it exists. Otherwise `GLOSSARY.md`, or `CONTEXT.md` when that is the file the repo already uses. Do not create a second glossary. Banned names are that file's `_Avoid_` list. Changing a term is `domain-modeling`.

## Consult

Before a plan or a bug fix, when `docs/lore/` exists. Read `docs/lore/README.md`. Grep `` `code:` `` for the files this task will touch. A path matches when it is the file or a parent directory of it. Read only the matching active entries. Brief at most five bullets, each with its path. Flag an entry whose path is missing. Skip `resolved` and `obsolete` unless the task is about that entry.

## Capture

When you learn a pitfall, an intentional behavior, an API quirk, or the why behind a decision. Run the boundary test first. If an entry already covers it, update that entry. A failure lesson records the recognizable signal and the rule that should fire next time. A diary of the incident does not. If `docs/lore/` does not exist yet, create the folder, a `README.md` index, and one area taken from the top-level part of the code you are in. Add a new area to the index in the same change. Do not overwrite an entry that is already there.

## Guard

Before a commit, when `docs/lore/` exists. Take the changed files (`git diff --name-only HEAD`, plus new files that belong to the change). Match them to `` `code:` `` paths the same way consult does. Read the hunks. Report each match as violated, respected, or not applicable. A violation names the entry, the path, and the hunk that conflicts. Also flag a new name that hits the glossary's `_Avoid_` list when it names that concept. This pass edits nothing. Say how many entries were checked when none conflict.

## Maintain and check

When asked to tidy lore, or when a path is dead: re-read the code. An `updated:` date older than about 180 days means re-read it, not that it is stale. Mark an entry `obsolete` when it is no longer true, and point at the replacement when there is one. Do not delete the file.

When asked whether the lore is helping, report three lines and do not edit: how many entries fail the boundary test, how many `code:` paths are missing, and how many active entries are older than about 180 days. Do not collapse those into one score.

After a rewrite, replay the commit that broke the rule through the guard steps. A miss is either a bad `code:` path (the entry was never looked at) or a vague body (it was looked at and not applied).
