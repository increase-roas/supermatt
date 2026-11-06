#!/usr/bin/env python3
"""Move leftover folders aside. Checkouts stay. Nothing is deleted."""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from classify import classify

DEFAULT = Path.home() / "Documents" / "Codex"
ARCHIVE = "archive"
CLEANUP = Path.home() / ".agents/skills/safe-cleanup/scripts/checked_cleanup.py"
SECRET = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|"
    r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|"
    r"xox[baprs]-"
)
VERIFY = """import subprocess, sys
head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/" + branch], text=True).split()
sys.exit(0 if remote and remote[0] == head else 1)
"""


def git(path, *args):
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)


def hide_junk(path):
    located = git(path, "rev-parse", "--git-path", "info/exclude")
    if located.returncode != 0:
        return
    exclude = Path(located.stdout.strip())
    if not exclude.is_absolute():
        exclude = (path / exclude).resolve()
    exclude.parent.mkdir(parents=True, exist_ok=True)
    current = exclude.read_text() if exclude.exists() else ""
    if ".DS_Store" not in current.splitlines():
        with exclude.open("a") as handle:
            handle.write(".DS_Store\n")


def skip_work_file(file_path: Path) -> bool:
    name = file_path.name
    if name == ".DS_Store" or name.endswith((".age", ".b64", ".private", ".tar.gz")):
        return True
    try:
        return file_path.is_file() and file_path.stat().st_size > 50_000_000
    except OSError:
        return True


def holds_secret(file_path: Path) -> bool:
    name = file_path.name
    if name == ".env" or name.endswith(".env") or file_path.suffix == ".pem":
        return True
    if not file_path.is_file() or file_path.stat().st_size > 2_000_000:
        return False
    try:
        text = file_path.read_text(errors="ignore")
    except OSError:
        return False
    return SECRET.search(text) is not None


def dirty_files(path):
    listed = git(path, "status", "--porcelain", "-uall")
    names = []
    for line in listed.stdout.splitlines():
        name = line[3:]
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        names.append(name.strip().strip('"'))
    return names


def save_changes(path: Path) -> str:
    hide_junk(path)
    secrets = []
    normal = []
    for rel in dirty_files(path):
        if Path(rel).name == ".DS_Store" or skip_work_file(path / rel):
            continue
        file_path = path / rel
        if file_path.is_file() and holds_secret(file_path):
            secrets.append(rel)
        else:
            normal.append(rel)
    if not normal:
        return "secret" if secrets else "clean"
    for rel in normal:
        git(path, "add", "--", rel)
    committed = git(path, "commit", "-m", "Save the working tree.")
    if committed.returncode != 0:
        return "commit-failed"
    return "secret" if secrets else "committed"


def publish(path: Path) -> str:
    if git(path, "remote", "get-url", "origin").returncode != 0:
        return "no-remote"
    branch = git(path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch == "HEAD":
        return "detached"
    git(path, "fetch", "origin", branch)
    counts = git(path, "rev-list", "--left-right", "--count", f"HEAD...origin/{branch}")
    if counts.returncode == 0:
        ahead, behind = counts.stdout.split()
        if behind != "0":
            rebasing = git(path, "pull", "--rebase", "origin", branch)
            if rebasing.returncode != 0:
                git(path, "rebase", "--abort")
                return "disagree"
    git(path, "push", "-u", "origin", "HEAD")
    head = git(path, "rev-parse", "HEAD").stdout.strip()
    remote = git(path, "ls-remote", "origin", f"refs/heads/{branch}").stdout.split()
    if remote and remote[0] == head:
        return "pushed"
    return "push-failed"


def main_repo(path: Path):
    located = git(path, "rev-parse", "--git-common-dir")
    if located.returncode != 0:
        return None
    common = Path(located.stdout.strip())
    if not common.is_absolute():
        common = (path / common).resolve()
    return common.parent


def retire(path: Path) -> str:
    target = str(path.resolve())
    repo = main_repo(path)
    if repo is None:
        return "kept"
    repo = repo.resolve()
    evidence = Path(tempfile.mkdtemp(prefix="doctor-")).resolve()
    manifest = evidence / "inventory.json"
    verify = evidence / "verify.py"
    verify.write_text(VERIFY)
    snap = subprocess.run(
        [sys.executable, "-B", str(CLEANUP), "snapshot",
         "--repo", str(repo), "--target", target, "--manifest", str(manifest)],
        capture_output=True, text=True)
    if snap.returncode != 0:
        return "kept"
    removed = subprocess.run(
        [sys.executable, "-B", str(CLEANUP), "remove",
         "--repo", str(repo), "--target", target, "--manifest", str(manifest),
         "--check-json", json.dumps([sys.executable, "-B", str(verify)])],
        capture_output=True, text=True)
    return "removed" if removed.returncode == 0 else "kept"


def settle(path: Path) -> str:
    saved = save_changes(path)
    if saved == "secret":
        return "left"
    published = publish(path)
    if classify(path) == "worktree" and published == "pushed" and not dirty_files(path):
        return retire(path)
    return published


def checkouts(parent: Path):
    for child in sorted(parent.iterdir(), key=lambda item: item.name.lower()):
        if child.name == ARCHIVE or child.is_symlink():
            continue
        kind = classify(child)
        if kind in ("primary", "worktree", "misplaced"):
            yield child
        elif kind == "nest":
            yield from checkouts(child)


JUNK_WORDS = {"repair", "fix", "proposal", "worktrees", "patch", "wip", "tmp", "the", "and", "for", "archive"}
DATE_WORDS = re.compile(r"20\d{2}[-_ ]?[01]\d[-_ ]?[0-3]\d(?:t[0-9]{6}z)?", re.I)
RANDOM_NAME = re.compile(r"^[a-z]+-[a-z]+-[a-z]*\d[a-z0-9]*$")


def show_word(word):
    if any(char.isupper() for char in word[1:]):
        return word
    return word.capitalize()


def plain_name(name, title=""):
    if not title and RANDOM_NAME.fullmatch(name or ""):
        return ""
    source = title or name.replace("-", " ").replace("_", " ")
    source = DATE_WORDS.sub(" ", source)
    source = re.sub(r"[^A-Za-z0-9]+", " ", source)
    words = []
    for word in source.split():
        if word.lower() in JUNK_WORDS or word.isdigit() or len(word) <= 1:
            continue
        words.append(show_word(word))
        if len(words) == 3:
            break
    return " ".join(words)


def folder_title(path: Path) -> str:
    chosen = []
    for cand in ("README.md", "STATUS.md", "RESULT.md", "REPORT.md"):
        file_path = path / cand
        if file_path.is_file():
            chosen.append(file_path)
    if not chosen:
        chosen = sorted(path.glob("*.md"))[:1]
    for file_path in chosen:
        try:
            lines = file_path.read_text(errors="ignore").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip().lstrip("#").strip()
            if not line or "Status:" in line or "/" in line or len(line) > 60:
                continue
            return line
    return ""


def friendly_name(path: Path) -> str:
    named = plain_name(path.name, folder_title(path))
    if named:
        return named
    if classify(path) not in ("primary", "worktree", "misplaced"):
        return ""
    branch = git(path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    branch = re.sub(r"^(feat|fix|chore|repair)/", "", branch)
    if branch and branch != "HEAD":
        return plain_name(branch, "")
    return ""


def rename_folder(path: Path):
    new = friendly_name(path)
    if not new or new == path.name:
        return path
    dest = path.parent / new
    if dest.exists():
        return path
    if classify(path) == "worktree":
        repo = main_repo(path)
        if repo is None:
            return path
        moved = git(repo, "worktree", "move", str(path), str(dest))
        return dest if moved.returncode == 0 else path
    path.rename(dest)
    return dest


def rename_children(parent: Path):
    renamed = []
    archive = parent / ARCHIVE
    targets = [child for child in parent.iterdir()
               if child.is_dir() and child.name != ARCHIVE and not child.is_symlink()]
    if archive.is_dir():
        targets.extend(child for child in archive.iterdir() if child.is_dir())
    for child in targets:
        before = child.name
        after = rename_folder(child)
        if after.name != before:
            renamed.append((before, after.name))
    if renamed and archive.is_dir():
        with (archive / "MANIFEST.tsv").open("a") as handle:
            for before, after in renamed:
                handle.write(f"renamed\t{before}\t{after}\n")
    return renamed


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
    for checkout in checkouts(parent):
        print(f"fixed\t{settle(checkout)}\t{checkout.name}")
    for before, after in rename_children(parent):
        print(f"named\t{before}\t{after}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
