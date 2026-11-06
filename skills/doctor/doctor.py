#!/usr/bin/env python3
"""Move leftover folders aside. Checkouts stay. Nothing is deleted."""
import subprocess
import sys
from pathlib import Path

from classify import classify

DEFAULT = Path.home() / "Documents" / "Codex"
ARCHIVE = "archive"


def plan(parent: Path):
    moves = []
    keeps = []
    for child in sorted(parent.iterdir(), key=lambda p: p.name.lower()):
        if child.name == ARCHIVE or child.is_symlink():
            keeps.append((child.name, "keep"))
            continue
        kind = classify(child)
        if kind == "dump":
            moves.append(child)
        else:
            keeps.append((child.name, kind))
    return moves, keeps


def same_remote_disagreement(parent: Path):
    """Two checkouts, one remote, different unpushed commits."""
    by_remote = {}
    for child in parent.iterdir():
        if classify(child) != "primary":
            continue
        url = subprocess.run(
            ["git", "-C", str(child), "remote", "get-url", "origin"],
            capture_output=True, text=True)
        if url.returncode != 0:
            continue
        head = subprocess.run(
            ["git", "-C", str(child), "rev-parse", "HEAD"],
            capture_output=True, text=True)
        by_remote.setdefault(url.stdout.strip(), []).append(
            (child.name, head.stdout.strip()))
    unsure = []
    for url, rows in by_remote.items():
        heads = {h for _, h in rows}
        if len(rows) > 1 and len(heads) > 1:
            unsure.append((url, [name for name, _ in rows]))
    return unsure


def fast_forward(path: Path) -> str:
    inside = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return "skip"
    subprocess.run(["git", "-C", str(path), "fetch", "--quiet"], capture_output=True)
    dirty = subprocess.run(
        ["git", "-C", str(path), "status", "--porcelain"],
        capture_output=True, text=True)
    if dirty.stdout.strip():
        return "dirty"
    counts = subprocess.run(
        ["git", "-C", str(path), "rev-list", "--left-right", "--count", "HEAD...@{u}"],
        capture_output=True, text=True)
    if counts.returncode != 0:
        return "no-upstream"
    ahead, behind = counts.stdout.split()
    if ahead == "0" and behind != "0":
        merged = subprocess.run(
            ["git", "-C", str(path), "merge", "--ff-only", "@{u}"],
            capture_output=True, text=True)
        return "forwarded" if merged.returncode == 0 else "behind"
    return "current"


def apply(parent: Path):
    parent = Path(parent)
    moves, keeps = plan(parent)
    archive = parent / ARCHIVE
    if moves:
        archive.mkdir(exist_ok=True)
    manifest = archive / "MANIFEST.tsv"
    lines = []
    for src in moves:
        dest = archive / src.name
        if dest.exists():
            raise SystemExit(f"archive already has {src.name}")
        src.rename(dest)
        lines.append(f"{src}\t{dest}\n")
    if lines:
        with manifest.open("a") as fh:
            fh.writelines(lines)
    return moves, keeps


def main(argv):
    parent = Path(argv[1]) if len(argv) > 1 else DEFAULT
    unsure = same_remote_disagreement(parent)
    if unsure:
        for url, names in unsure:
            print(f"unsure\t{url}\t{', '.join(names)}")
        return 2
    moves, keeps = apply(parent)
    for src in moves:
        print(f"moved\t{src.name}")
    for name, kind in keeps:
        print(f"kept\t{kind}\t{name}")
    for child in sorted(parent.iterdir(), key=lambda p: p.name.lower()):
        if child.name == ARCHIVE or classify(child) != "primary":
            continue
        print(f"checkout\t{fast_forward(child)}\t{child.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
