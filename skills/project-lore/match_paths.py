"""Match a lore `code:` path to a changed file. A path matches when it is the file or a parent directory of it."""


def matches(code_path, changed_file):
    code = _norm(code_path)
    changed = _norm(changed_file)
    if not code or not changed:
        return False
    return changed == code or changed.startswith(code.rstrip("/") + "/")


def _norm(path):
    return (path or "").strip().strip("`").lstrip("./").replace("\\", "/")
