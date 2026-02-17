"""Handles gitignore pattern matching for file filtering."""

import fnmatch
import os

from .constants import DEFAULT_IGNORE


def load_gitignore(root_path):
    """Loads the .gitignore file from the root path.

    Args:
        root_path: The root path of the project.

    Returns:
        List[str]: A list of patterns read from the .gitignore file.
    """
    patterns = set(DEFAULT_IGNORE)
    gitignore_path = os.path.join(root_path, ".gitignore")
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as gitignore_file:
                for raw_line in gitignore_file:
                    line = raw_line.strip()
                    if line and not line.startswith("#"):
                        patterns.add(line)
        except Exception:
            pass
    return list(patterns)


def is_ignored(path, root_path, patterns):
    """Checks if a file path matches any of the ignore patterns.

    Args:
        path: Path to check.
        root_path: Project root directory.
        patterns: List of ignore patterns.

    Returns:
        True if the path should be ignored, False otherwise.
    """
    rel = os.path.relpath(path, root_path)
    if rel == ".":
        return False
    name = os.path.basename(path)
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
        if fnmatch.fnmatch(rel, pattern):
            return True
        if pattern.strip("/") in rel.split(os.sep):
            return True
    return False
