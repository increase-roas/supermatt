"""Match a lore `code:` path to a changed file. A path matches when it is the file or a parent directory of it.

`~` is expanded, so `~/x` and `/Users/me/x` match each other. Run as
`python3 match_paths.py <lore-dir> <file>...` to print the active entry titles that match.
"""
import os
import re
import sys


def matches(code_path, changed_file):
    code = _norm(code_path)
    changed = _norm(changed_file)
    if not code or not changed:
        return False
    return changed == code or changed.startswith(code.rstrip("/") + "/")


def _norm(path):
    p = (path or "").strip().strip("`").replace("\\", "/")
    if p.startswith("~"):
        p = os.path.expanduser(p)
    elif p.startswith("./"):
        p = p[2:]
    # expanduser on Windows writes backslashes, and those paths do not start
    # with "/", so slash-normalize again after absolute normalization.
    if os.path.isabs(p):
        p = os.path.normpath(p)
    else:
        p = p.lstrip("./")
    return p.replace("\\", "/")


_CODE = re.compile(r"`code:`\s*(.+?)\s*(?:→.*?)?\s*`updated:`")
_STATUS = re.compile(r"`status:`\s*(\w+)")


def scan(lore_dir, files):
    """Titles of active entries under lore_dir whose code: path matches any of files."""
    titles = []
    for root, _, names in os.walk(lore_dir):
        for name in sorted(names):
            if not name.endswith(".md"):
                continue
            title = None
            for line in open(os.path.join(root, name), encoding="utf-8"):
                if line.startswith("## "):
                    title = line[3:].strip()
                elif line.startswith("# "):
                    title = line[2:].strip()
                m = _CODE.search(line)
                if m and title:
                    st = _STATUS.search(line)
                    if st and st.group(1) != "active":
                        continue
                    if any(matches(m.group(1), f) for f in files):
                        titles.append(title)
    return titles


if __name__ == "__main__":
    for t in scan(sys.argv[1], sys.argv[2:]):
        print(t)
