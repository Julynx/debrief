import fnmatch
import os

from .constants import DEFAULT_IGNORE


def load_gitignore(root_path):
    """
    Loads the .gitignore file from the root path

    Args:
        root_path (Path | str): The root path of the project.

    Returns:
        patterns (list): A list of patterns read from the
          .gitignore file
    """
    patterns = set(DEFAULT_IGNORE)
    gitignore_path = os.path.join(root_path, ".gitignore")
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.add(line)
        except Exception:
            pass
    return list(patterns)


def is_ignored(path, root_path, patterns):
    rel = os.path.relpath(path, root_path)
    if rel == ".":
        return False
    name = os.path.basename(path)
    for p in patterns:
        if fnmatch.fnmatch(name, p):
            return True
        if fnmatch.fnmatch(rel, p):
            return True
        if p.strip("/") in rel.split(os.sep):
            return True
    return False
