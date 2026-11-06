#!/usr/bin/env python3
"""Classify one child of a folder of repos. A name is not evidence."""
import sys
from pathlib import Path


def classify(path: Path) -> str:
    path = Path(path)
    if not path.exists():
        return "missing"
    if not path.is_dir():
        return "skip"
    git = path / ".git"
    if git.is_file():
        return "worktree"
    if git.is_dir():
        if path.parent.name == "worktrees":
            return "misplaced"
        return "primary"
    if path.name == "worktrees" or path.name.endswith("-worktrees"):
        return "nest"
    if _holds_checkout(path):
        return "nest"
    return "dump"


def _holds_checkout(path: Path) -> bool:
    try:
        children = list(path.iterdir())
    except OSError:
        return False
    for child in children:
        git = child / ".git"
        if git.is_file() or git.is_dir():
            return True
    return False


def main(argv):
    target = Path(argv[1])
    if classify(target) in ("dump", "nest"):
        for child in sorted(target.iterdir(), key=lambda p: p.name.lower()):
            print(f"{classify(child)}\t{child.name}")
        return 0
    print(classify(target))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
