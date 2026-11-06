#!/usr/bin/env python3
"""Preserve work in a scoped folder and report what was saved."""
import argparse
import fcntl
import json
import os
import re
import signal
import stat
import subprocess
import sys
import tempfile
from contextlib import ExitStack, suppress
from pathlib import Path
from urllib.parse import unquote, urlsplit

from classify import classify

DEFAULT = Path.home() / "Documents" / "Codex"
ARCHIVE = "archive"
MAX_FILE_BYTES = 2_000_000
MAX_SNAPSHOT_BYTES = 25_000_000
CODEX_DIAGNOSTIC_TIMEOUT = 75
PROTECTED_NAME = re.compile(r"(?:^|[^a-z0-9])javar(?:testing)?(?:$|[^a-z0-9])", re.I)
SECRET_PATH = re.compile(
    r"(?:^|[._-])(?:env|secrets?|credentials?|id_rsa|id_ed25519)(?:$|[._-])|"
    r"(?:^|\.)(?:envrc|netrc|npmrc|pypirc)$|"
    r"\.(?:pem|key|p12|pfx|age|b64|private|gz|zip|sqlite3?|db)$", re.I)
SECRET = re.compile(
    r"-----BEGIN [^-\n]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|"
    r"AIza[A-Za-z0-9_-]{35}|(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}|"
    r"npm_[A-Za-z0-9]{20,}|glpat-[A-Za-z0-9_-]{20,}|"
    r"eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{8,}|"
    r"xox[baprs]-|(?:AKIA|ASIA)[A-Z0-9]{16}|authorization\s*:\s*(?:bearer|basic)\s+\S+|"
    r"https?://[^\s/:]+:[^\s/@]+@|"
    r"""\b(?:api[_ -]?key|access[_ -]?token|auth[_ -]?token|client[_ -]?secret|"""
    r"""(?:aws[_ -]?)?secret[_ -]?access[_ -]?key|password|secret|token)['"]?\s*[:=]\s*['"]?\S""",
    re.I)
GIT_LOCATION = {
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE", "GIT_PREFIX",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_QUARANTINE_PATH",
}


def git(path, *args, data=None, index=None):
    env = {name: value for name, value in os.environ.items() if name not in GIT_LOCATION}
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    if index is not None:
        env["GIT_INDEX_FILE"] = str(index)
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(path), *args],
        input=data, capture_output=True, env=env, timeout=30)


def value(path, *args, **kwargs):
    result = git(path, *args, **kwargs)
    return os.fsdecode(result.stdout).removesuffix("\n") if result.returncode == 0 else None


def protected(path, exclusions):
    parts = tuple(part.casefold() for part in path.parts)
    return any(PROTECTED_NAME.search(part) for part in path.parts) or any(
        parts[:len(excluded.parts)] == tuple(part.casefold() for part in excluded.parts)
        for excluded in exclusions)


def checkout_root(path):
    top = value(path, "rev-parse", "--show-toplevel")
    return Path(top).resolve() if top else None


def status(path):
    result = git(path, "-c", "status.renames=false", "status", "--porcelain=v1", "-z",
                 "--untracked-files=all", "--ignored=matching", "--ignore-submodules=none")
    if result.returncode != 0:
        return None
    return [(entry[:2], entry[3:]) for entry in result.stdout.split(b"\0") if entry]


def eligible_file(path, relative):
    rel = Path(os.fsdecode(relative))
    if not rel.parts or rel.is_absolute() or ".." in rel.parts:
        return None, "could not verify the file path"
    if rel.name.casefold() == ".ds_store":
        return None, "system metadata"
    if any(SECRET_PATH.search(part) for part in rel.parts):
        return None, "credential or archive filename"
    try:
        with ExitStack() as stack:
            directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            parent = os.open(path, directory_flags)
            stack.callback(os.close, parent)
            for part in rel.parts[:-1]:
                parent = os.open(part, directory_flags, dir_fd=parent)
                stack.callback(os.close, parent)
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
            handle = stack.enter_context(os.fdopen(os.open(rel.name, flags, dir_fd=parent), "rb"))
            before = os.fstat(handle.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                return None, "linked or special file"
            if before.st_size > MAX_FILE_BYTES:
                return None, "larger than the snapshot file limit"
            content = handle.read(MAX_FILE_BYTES + 1)
            after = os.fstat(handle.fileno())
        if len(content) != before.st_size or before.st_mtime_ns != after.st_mtime_ns:
            return None, "changed while being read"
        decoded = content.decode("utf-8")
    except (OSError, RuntimeError):
        return None, "linked or unreadable file"
    except UnicodeDecodeError:
        return None, "nontext file"
    if any(ord(char) < 32 and char not in "\r\n\t" for char in decoded):
        return None, "nontext file"
    if SECRET.search(decoded):
        return None, "possible credential in the file"
    mode = "100755" if before.st_mode & stat.S_IXUSR else "100644"
    return (mode, content), None


def snapshot_tree(path, head, files):
    with tempfile.TemporaryDirectory(prefix="supermatt-doctor-") as temporary:
        index = Path(temporary) / "index"
        if git(path, "read-tree", head, index=index).returncode != 0:
            return None
        entries = []
        for relative, mode, content in files:
            oid = value(path, "hash-object", "-w", "--stdin", data=content)
            if oid is None:
                return None
            entries.append(f"{mode} {oid}\t".encode() + relative + b"\0")
        if git(path, "update-index", "-z", "--index-info", index=index,
               data=b"".join(entries)).returncode != 0:
            return None
        return value(path, "write-tree", index=index)


def has_commit_hooks(path):
    location = value(path, "config", "--path", "--get", "core.hooksPath")
    if location is None:
        location = value(path, "rev-parse", "--git-path", "hooks")
    if location is None:
        return True
    hooks = path / location
    return any(os.access(hooks / hook, os.X_OK) for hook in
               ("pre-commit", "prepare-commit-msg", "commit-msg"))


def save_snapshot(path, head, tree):
    branch = f"doctor/save-{head[:12]}-{tree[:12]}"
    ref = f"refs/heads/{branch}"
    existing = value(path, "rev-parse", "--verify", ref)
    if existing is None:
        commit = value(path, "commit-tree", tree, "-p", head, "-m", "Save work with SuperMatt Doctor")
        if commit and git(path, "update-ref", ref, commit, "0" * len(head)).returncode == 0:
            return branch, commit
        existing = value(path, "rev-parse", "--verify", ref)
    if existing and value(path, "show", "-s", "--format=%T %P", existing) == f"{tree} {head}":
        return branch, existing
    return None


def remote_ref(path, ref):
    result = git(path, "ls-remote", "--exit-code", "origin", ref)
    if result.returncode == 2:
        return ""
    fields = result.stdout.split()
    if result.returncode == 0 and len(fields) == 2 and fields[1] == ref.encode():
        return fields[0].decode("ascii")
    return None


def remote_problem(path, exclusions):
    fetch_urls = value(path, "remote", "get-url", "--all", "origin")
    push_urls = value(path, "remote", "get-url", "--push", "--all", "origin")
    if not fetch_urls or fetch_urls != push_urls or "\n" in fetch_urls:
        return "the push and readback need one matching remote"
    if PROTECTED_NAME.search(unquote(fetch_urls)):
        return "the remote destination is excluded"
    try:
        parsed = urlsplit(fetch_urls) if "://" in fetch_urls else None
    except ValueError:
        return "the remote route could not be verified"
    if parsed and parsed.scheme == "file":
        file_url = parsed
        if file_url.netloc.casefold() not in ("", "localhost") or not file_url.path.startswith("/"):
            return "the local remote path could not be verified"
        local = Path(unquote(file_url.path))
    elif parsed:
        if parsed.scheme not in ("https", "http", "ssh", "git"):
            return "the remote route could not be verified"
        return None
    elif fetch_urls.startswith("file:"):
        return "the local remote path could not be verified"
    elif re.fullmatch(r"(?:[^/@:]+@)?(?:\[[^\]]+\]|[^/:]+):(?!:).+", fetch_urls):
        return None
    elif "::" in fetch_urls:
        return "the remote route could not be verified"
    else:
        local = path / fetch_urls
    try:
        resolved = local.resolve()
    except (OSError, RuntimeError, ValueError):
        return "the local remote path could not be verified"
    if protected(local, exclusions) or protected(resolved, exclusions):
        return "the remote destination is excluded"
    common_dir = value(resolved, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if not common_dir:
        return "the local remote's Git data could not be verified"
    if protected(Path(common_dir).resolve(), exclusions):
        return "the remote destination is excluded"
    return None


def report_durability(path, head, exclusions):
    source_ref = value(path, "symbolic-ref", "-q", "HEAD")
    try:
        problem = remote_problem(path, exclusions)
        if problem or not source_ref:
            print(f"Remote backup is unverified because {problem or 'this checkout has no current branch'}.")
            return
        current = remote_ref(path, source_ref)
        if current == head:
            print("The remote branch confirms the checkout's current commit.")
        elif current and git(path, "merge-base", "--is-ancestor", current, head).returncode == 0:
            print("The current commit is ahead of its remote branch. This commit is only verified locally.")
        elif current == "":
            print("The remote has no matching branch. The current commit is only verified locally.")
        else:
            print("The remote did not confirm the current commit. Remote backup is unverified.")
    except subprocess.TimeoutExpired:
        print("Remote backup is unverified because the check timed out.")


def publish_snapshot(path, head, branch, commit, exclusions):
    problem = remote_problem(path, exclusions)
    if problem:
        return problem
    source_ref = value(path, "symbolic-ref", "-q", "HEAD")
    if not source_ref or remote_ref(path, source_ref) != head:
        return "the checked-out commit differs from the remote or could not be verified"
    destination = f"refs/heads/{branch}"
    remote = remote_ref(path, destination)
    if remote == commit:
        return None
    if remote != "":
        return "the snapshot branch is already in use or could not be checked"
    git(path, "push", "--no-follow-tags", "--recurse-submodules=no",
        "origin", f"{commit}:{destination}")
    if remote_ref(path, destination) != commit:
        return "the remote did not confirm the saved commit"
    return None


def settle(path, dry_run, exclusions):
    marker = path / ".git"
    if marker.is_symlink():
        print("Kept in place. The checkout's Git data is linked elsewhere.")
        return 1
    if marker.is_file():
        with marker.open("rb") as handle:
            pointer = os.fsdecode(handle.readline(4096)).strip()
        if not pointer.startswith("gitdir: ") or protected(
                (path / pointer.removeprefix("gitdir: ")).resolve(), exclusions):
            print("Skipped. The checkout's Git data is excluded or unavailable.")
            return 1
    git_dir = value(path, "rev-parse", "--absolute-git-dir")
    common_dir = value(path, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if not git_dir or not common_dir or any(
            protected(Path(location).resolve(), exclusions) for location in (git_dir, common_dir)):
        print("Skipped. The checkout's Git data is excluded or unavailable.")
        return 1
    if checkout_root(path) != path:
        print("Kept in place. Git could not confirm this checkout.")
        return 1
    head = value(path, "rev-parse", "--verify", "HEAD")
    entries = status(path)
    if entries is None:
        print("Kept in place. Git could not check the saved and unsaved files.")
        return 1
    files = []
    size = 0
    candidates = [relative for state, relative in entries if state in (b" M", b"??")
                  and not protected(path / os.fsdecode(relative), exclusions)]
    ignored = {relative for state, relative in entries if state == b"!!"}
    if candidates:
        ignore_check = git(path, "check-ignore", "--no-index", "-z", "--stdin",
                           data=b"\0".join(candidates) + b"\0")
        if ignore_check.returncode not in (0, 1):
            print("Kept on disk. Git could not verify which files to leave out.")
            return 1
        ignored.update(item for item in ignore_check.stdout.split(b"\0") if item)
    for state, relative in entries:
        if relative in ignored:
            continue
        name = os.fsdecode(relative)
        if protected(path / name, exclusions):
            reason = "excluded path"
        elif state == b" D":
            reason = "working copy records a deletion"
        elif state not in (b" M", b"??"):
            reason = "staged, conflicting, or changed file type"
        else:
            found, reason = eligible_file(path, relative)
            if found:
                mode, content = found
                if size + len(content) <= MAX_SNAPSHOT_BYTES:
                    files.append((relative, mode, content))
                    size += len(content)
                    continue
                reason = "snapshot size limit"
        display = "[credential-like filename]" if SECRET.search(name) else repr(name)
        print(f"Kept {display} on disk ({reason}).")
    if ignored:
        print(f"Git reports {len(ignored)} ignored path(s), including any grouped folders. They stay on disk.")
    if head is None:
        print("Kept on disk. This checkout has no starting commit yet.")
        return 0
    if not files:
        print("No eligible unsaved files needed a snapshot. The checkout stays in place.")
        if not dry_run:
            report_durability(path, head, exclusions)
        return 0
    if has_commit_hooks(path):
        print("Kept on disk. This checkout needs its normal commit workflow to run its checks.")
        return 0
    if dry_run:
        print(f"Preview. {len(files)} file(s) qualify for a separate snapshot.")
        return 0
    if head != value(path, "rev-parse", "--verify", "HEAD") or entries != status(path):
        print("Kept on disk. The checkout changed during the check.")
        return 1
    base = value(path, "rev-parse", f"{head}^{{tree}}") if head else None
    if base is None:
        print("Kept on disk. Git could not verify the starting commit.")
        return 1
    tree = snapshot_tree(path, head, files)
    if tree == base:
        print("The eligible files already match the starting commit.")
        return 0
    saved = save_snapshot(path, head, tree) if tree else None
    if saved is None:
        print("Kept on disk. Git could not create a separate snapshot.")
        return 1
    branch, commit = saved
    try:
        reason = publish_snapshot(path, head, branch, commit, exclusions)
    except subprocess.TimeoutExpired:
        reason = "the remote check timed out"
    if reason:
        print(f"Saved {len(files)} file(s) locally on {branch}. Kept local because {reason}.")
    else:
        print(f"Saved {len(files)} file(s) on {branch} and verified remote commit {commit}.")
    print("The checkout and its original branch stay in place.")
    return 0


JUNK_WORDS = {"repair", "fix", "proposal", "worktrees", "patch", "wip", "tmp", "the", "and", "for", "archive"}
DATE_WORDS = re.compile(r"20\d{2}[-_ ]?[01]\d[-_ ]?[0-3]\d(?:t[0-9]{6}z)?", re.I)
RANDOM_NAME = re.compile(r"^[a-z]+-[a-z]+-[a-z]*\d[a-z0-9]*$")


def plain_name(name, title=""):
    if not title and RANDOM_NAME.fullmatch(name):
        return ""
    words = re.findall(r"[A-Za-z0-9]+", DATE_WORDS.sub(" ", title or name))
    words = [word for word in words if word.lower() not in JUNK_WORDS
             and not word.isdigit() and len(word) > 1]
    return " ".join(word if any(char.isupper() for char in word[1:]) else word.capitalize()
                    for word in words[:3])


def folder_title(path):
    for name in ("README.md", "STATUS.md", "RESULT.md", "REPORT.md"):
        candidate = path / name
        if not candidate.is_file():
            continue
        with candidate.open("rb") as handle:
            content = handle.read(4096).decode("utf-8", errors="replace")
        for line in content.splitlines():
            title = line.removeprefix("# ").strip()
            if line.startswith("# ") and len(title) <= 60 and not SECRET.search(title):
                return title
    return ""


def walk_error(error):
    raise error


def bare_repository(path):
    return ((path / "HEAD").is_file() and (path / "objects").is_dir()
            and any((path / name).exists() for name in ("refs", "reftable", "packed-refs")))


def open_archive_record(path, write):
    flags = os.O_NOFOLLOW | os.O_NONBLOCK
    flags |= os.O_RDWR | os.O_APPEND | os.O_CREAT if write else os.O_RDONLY
    record = os.fdopen(os.open(path, flags, 0o600), "a+" if write else "r",
                       encoding="utf-8", errors="replace")
    try:
        info = os.fstat(record.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise OSError("archive record must be one regular file")
        fcntl.flock(record.fileno(), fcntl.LOCK_EX if write else fcntl.LOCK_SH)
        if os.fstat(record.fileno()).st_nlink != 1:
            raise OSError("archive record gained a link")
    except OSError:
        record.close()
        raise
    return record


def pending_move(record, paths):
    record.seek(0)
    pending = False
    for row in record:
        action, _, written_paths = row.rstrip("\n").partition("\t")
        if written_paths == paths and action in ("planned", "moved"):
            pending = action == "planned"
    return pending


def archive_folder(path, dry_run, exclusions):
    if (Path.cwd().is_relative_to(path) or Path.home().is_relative_to(path)
            or ARCHIVE in (part.casefold() for part in path.parts)
            or any(part.startswith(".") for part in path.parts)
            or checkout_root(path) is not None or classify(path) != "dump"):
        print("Kept in place. This is an active path, system folder, archive, or checkout.")
        return 1
    for directory, folders, files in os.walk(path, onerror=walk_error):
        if "HEAD" in files and "objects" in folders and bare_repository(Path(directory)):
            print("Kept in place. This folder is or contains a bare Git repository.")
            return 1
        for name in folders + files:
            entry = Path(directory) / name
            if name == ".git" or entry.is_symlink() or protected(entry, exclusions):
                print("Kept in place. The folder contains a checkout, link, or excluded path.")
                return 1
    archive = path.parent / ARCHIVE
    name = plain_name(path.name, folder_title(path)) or "Saved Folder"
    container = archive / name
    dest = container / "Files"
    manifest = archive / "MANIFEST.tsv"
    if protected(manifest, exclusions) or manifest.is_symlink():
        print("Kept in place. The archive record is excluded or linked.")
        return 1
    if (archive.is_symlink() or (archive / ".git").exists() or bare_repository(archive)
            or container.is_symlink() or protected(dest, exclusions)):
        print("Kept in place. The archive path is excluded, linked, or already in use.")
        return 1
    if container.exists() and not manifest.exists():
        print("Kept in place. The archive name is already in use.")
        return 1
    if dry_run and not manifest.exists():
        print(f"Preview. Would put the closed folder in {dest}.")
        return 0
    if not dry_run:
        archive.mkdir(exist_ok=True)
    try:
        record = open_archive_record(manifest, write=not dry_run)
    except OSError:
        print("Kept in place. The archive record is linked, unavailable, or a special file.")
        return 1
    with record:
        paths = "\t".join(json.dumps(str(item)) for item in (path, dest))
        pending = pending_move(record, paths)
        if container.exists() and (not pending or not container.is_dir() or any(container.iterdir())):
            print("Kept in place. The archive name is already in use.")
            return 1
        if dry_run:
            print(f"Preview. Would put the closed folder in {dest}.")
            return 0
        if not pending:
            record.write(f"planned\t{paths}\n")
            record.flush()
            os.fsync(record.fileno())
        if not container.exists():
            container.mkdir()
        before = path.stat()
        path.rename(dest)
        if path.exists() or not os.path.samestat(before, dest.stat()):
            print("The archive move could not be confirmed. Check the planned move in the receipt.")
            return 1
        record.write(f"moved\t{paths}\n")
        record.flush()
        os.fsync(record.fileno())
    print(f"Moved the closed folder to {dest}. The move is recorded in {manifest}.")
    return 0


def inspect_collection(path, exclusions):
    for child in sorted(path.iterdir(), key=lambda item: item.name.casefold()):
        if protected(child, exclusions):
            print(f"Skipped excluded path {child.name!r}.")
        elif child.is_symlink() or child.name == ARCHIVE:
            print(f"Kept {child.name!r} in place.")
        elif child.is_dir():
            if (child / ".git").exists():
                print(f"Found checkout {child.name!r}. Use that path to save eligible work.")
            elif bare_repository(child):
                print(f"Kept bare Git repository {child.name!r} in place.")
            elif child.name == "worktrees" or child.name.endswith("-worktrees"):
                print(f"Found checkout group {child.name!r}. Check each checkout individually.")
            else:
                print(f"Found folder {child.name!r}. It can be moved if it is closed and independent.")
    print("Collection check complete. Use a specific folder path to apply changes.")
    return 0


def run_codex_diagnostic(path):
    stop_requested = False
    waiting = False

    def terminate(signum, _frame):
        nonlocal stop_requested
        if not stop_requested:
            stop_requested = True
            if waiting:
                raise SystemExit(128 + signum)

    previous_handler = signal.signal(signal.SIGTERM, terminate)
    try:
        # Defer termination during launch until we have the process group to stop.
        process = subprocess.Popen(
            ["codex", "doctor", "--json"], cwd=path, env=dict(os.environ, CODEX_HOME=str(path)),
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        completed = False
        try:
            try:
                waiting = True
                if stop_requested:
                    raise SystemExit(128 + signal.SIGTERM)
                stdout, _ = process.communicate(timeout=CODEX_DIAGNOSTIC_TIMEOUT)
                completed = True
            finally:
                waiting = False
        finally:
            process.stdout.close()
            if not completed:
                # The launcher can exit while a descendant still holds the output pipe.
                with suppress(ProcessLookupError):
                    os.killpg(process.pid, signal.SIGKILL)
                with suppress(subprocess.TimeoutExpired):
                    process.wait(timeout=1)
    finally:
        signal.signal(signal.SIGTERM, previous_handler)
        if stop_requested:
            raise SystemExit(128 + signal.SIGTERM)
    return stdout, process.returncode


def codex_health(path):
    states = {"ok": "passed", "warning": "warning", "fail": "failed",
              "skipped": "skipped", "info": "information"}
    required_checks = ("installation", "config.load", "auth.credentials", "network.provider_reachability")
    labels = {
        "installation": "Codex installation",
        "config.load": "Codex configuration",
        "auth.credentials": "Codex sign-in",
        "mcp.config": "Connected tools configuration",
        "desktop.app_server.handshake": "Desktop connection",
        "desktop.security.enforcement": "Desktop security checks",
        "network.provider_reachability": "Connection to the model provider",
        "state.paths": "Codex state paths",
        "state.rollout_db_parity": "Session history consistency",
        "terminal.env": "Terminal environment",
    }
    print(f"Running the native Codex diagnostic (up to {CODEX_DIAGNOSTIC_TIMEOUT} seconds).", flush=True)
    try:
        stdout, returncode = run_codex_diagnostic(path)
    except subprocess.TimeoutExpired:
        print(f"Codex health could not be verified. The native diagnostic timed out after {CODEX_DIAGNOSTIC_TIMEOUT} seconds.")
        return 1
    except OSError:
        print("Codex health could not be verified. The native diagnostic was unavailable.")
        return 1
    try:
        report = json.loads(stdout)
        checks = report["checks"]
        overall = report["overallStatus"]
        if overall not in states or not all(checks[key]["status"] in states for key in required_checks):
            raise ValueError
    except (ValueError, TypeError, KeyError):
        print("Codex health could not be verified. The native diagnostic returned an incomplete or invalid report.")
        return 1
    print("Codex checked its installation and settings.")
    for key, label in labels.items():
        entry = checks.get(key)
        check_status = entry.get("status") if isinstance(entry, dict) else None
        if isinstance(check_status, str) and check_status in states:
            print(f"{label}: {states[check_status]}.")
    print(f"Overall Codex health: {states[overall]}.")
    if overall == "fail" and returncode == 0:
        return 1
    return returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a folder or save eligible work in one checkout.")
    parser.add_argument("target", nargs="?", default=str(DEFAULT), help="folder to check or checkout to save")
    parser.add_argument("--exclude", action="append", default=[], metavar="PATH",
                        help="skip this path and its contents (relative to the target)")
    parser.add_argument("--dry-run", action="store_true", help="show what could be done")
    parser.add_argument("--archive", action="store_true", help="move one closed, independent folder to archive")
    args = parser.parse_args(argv)
    try:
        requested = Path(args.target).expanduser().absolute()
        if protected(requested, ()):
            print("Skipped the excluded folder.")
            return 0
        path = requested.resolve()
        exclusions = [(path / Path(item).expanduser()).resolve() for item in args.exclude]
        if protected(path, exclusions):
            print("Skipped the excluded folder.")
            return 0
        if requested != path and requested.is_symlink():
            print("Kept in place. The target is a link.")
            return 1
        if not path.is_dir():
            if args.archive:
                print(f"The source folder is unavailable. If it moved, check {path.parent / ARCHIVE / 'MANIFEST.tsv'}.")
            else:
                print("That folder is unavailable.")
            return 1
        codex_home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser().resolve()
        config_homes = (codex_home, (Path.home() / ".codex").resolve())
        if path in config_homes:
            return codex_health(path)
        if any(path.is_relative_to(home) for home in config_homes):
            print("Kept in place. Use the Codex configuration folder to check its settings.")
            return 1
        if args.archive:
            if any(home.is_relative_to(path) for home in config_homes):
                print("Kept in place. This path contains the Codex configuration folder.")
                return 1
            return archive_folder(path, args.dry_run, [*exclusions, *config_homes])
        if bare_repository(path):
            print("Kept the bare Git repository in place.")
            return 0
        if (path / ".git").exists():
            return settle(path, args.dry_run, exclusions)
        return inspect_collection(path, exclusions)
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        print("The check stopped because a local file or tool was unavailable. Review the folder and any archive receipt.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
