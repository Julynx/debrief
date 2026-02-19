"""Handles gitignore pattern matching for file filtering."""

import fnmatch
import logging
import os
from pathlib import Path

from .constants import DEFAULT_IGNORE

logger = logging.getLogger(__name__)


def load_gitignore(
    root_path: str, extra_patterns: list[str] | None = None
) -> list[str]:
    """Loads the .gitignore file from the root path.

    Args:
        root_path: The root path of the project.
        extra_patterns: Optional list of additional patterns to exclude.

    Returns:
        A list of patterns read from the .gitignore file.
    """
    patterns = set(DEFAULT_IGNORE)
    gitignore_path = Path(root_path) / ".gitignore"
    if gitignore_path.exists():
        try:
            for raw_line in gitignore_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line)
        except Exception:
            logger.debug("Failed to read .gitignore", exc_info=True)
    if extra_patterns:
        patterns.update(extra_patterns)
    return list(patterns)


def is_ignored(path: str, root_path: str, patterns: list[str]) -> bool:
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
