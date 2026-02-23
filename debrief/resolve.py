"""Utilities for resolving project files and parsing metadata."""

import logging
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Optional

from debrief.constants import (
    DEFAULT_DESCRIPTION,
    MIN_DESCRIPTION_CHARS,
    MIN_README_LINES,
)

logger = logging.getLogger(__name__)


def log(level: str, msg: str) -> None:
    """Logs a message with an icon based on the severity level.

    Args:
        level: The severity level ("FAIL", "WARN", "OK").
        msg: The message to log.
    """
    icon = "❌" if level == "FAIL" else "⚠️" if level == "WARN" else "✅"
    if level == "FAIL":
        logging.error(f"{icon}  {msg}")
    elif level == "WARN":
        logging.warning(f"{icon}  {msg}")
    else:
        logging.info(f"{icon}  {msg}")


@lru_cache(maxsize=16)
def _load_pyproject(root: Path) -> Optional[dict]:
    """Loads and caches the parsed pyproject.toml data.

    Args:
        root: Project root directory.

    Returns:
        The parsed TOML dictionary, or None on error.
    """
    toml_path = root / "pyproject.toml"
    if not toml_path.exists():
        return None
    try:
        data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        return data
    except Exception:
        logger.debug("Failed to parse pyproject.toml", exc_info=True)
        return None


def resolve_readme(root: str) -> Optional[str]:
    """Finds the README file in the project looking at standard locations.

    Logs success, warnings, or failures.

    Args:
        root: Project root directory.

    Returns:
        Absolute path to README or None.
    """
    root_path = Path(root)
    candidates = [
        "README.md",
        "docs/README.md",
        ".github/README.md",
        "readme.md",
    ]

    for rel_name in candidates:
        abs_path = root_path / rel_name
        if abs_path.exists():
            rel = abs_path.relative_to(root_path)

            try:
                text = abs_path.read_text(encoding="utf-8")
            except Exception:
                logger.debug("Could not read %s", rel, exc_info=True)
                log("FAIL", f"Could not read {rel}")
                continue

            if not text.strip():
                log("FAIL", f"README found at {rel} is empty!")
                return str(abs_path)

            non_empty_lines = [line for line in text.splitlines() if line.strip()]
            if len(non_empty_lines) < MIN_README_LINES:
                log(
                    "WARN",
                    f"{rel} is very short"
                    f" (less than {MIN_README_LINES} non-empty lines).",
                )
            else:
                log("OK", f"Found README at {rel}")

            return str(abs_path)

    log("FAIL", "No README found! (Checked root, docs/, .github/)")
    return None


def resolve_pyproject(root: str) -> Optional[str]:
    """Finds and validates pyproject.toml.

    Args:
        root: Project root directory.

    Returns:
        Absolute path to pyproject.toml or None.
    """
    root_path = Path(root)
    toml_path = root_path / "pyproject.toml"
    if not toml_path.exists():
        return None

    description = get_project_description(root)
    if not description or not description.strip():
        log("FAIL", "pyproject.toml has empty/missing description.")
    elif description.strip() == DEFAULT_DESCRIPTION:
        log("WARN", "pyproject.toml has the default uv description.")
    elif len(description.replace(" ", "")) < MIN_DESCRIPTION_CHARS:
        log(
            "WARN",
            f"pyproject.toml description is very short"
            f" (less than {MIN_DESCRIPTION_CHARS} non-whitespace chars).",
        )
    else:
        log("OK", "Found pyproject.toml")
    return str(toml_path)


def resolve_requirements(root: str) -> Optional[str]:
    """Finds requirements.txt.

    Args:
        root: Project root directory.

    Returns:
        Absolute path to requirements.txt or None.
    """
    req_path = Path(root) / "requirements.txt"
    if req_path.exists():
        return str(req_path)
    return None


def check_dependencies(root: str) -> None:
    """Checks if either pyproject.toml or requirements.txt exists.

    Logs WARN if neither is found.

    Args:
        root: Project root directory.
    """
    has_toml = resolve_pyproject(root) is not None
    has_req = resolve_requirements(root) is not None

    if not has_toml and not has_req:
        log("WARN", "No dependencies found (no requirements.txt or pyproject.toml).")


def get_project_description(root: str) -> Optional[str]:
    """Extracts the project description from pyproject.toml.

    Args:
        root: Project root directory.

    Returns:
        The project description string, or None if not found/error.
    """
    data = _load_pyproject(Path(root))
    if data is None:
        return None
    return data.get("project", {}).get("description")


def get_project_dependencies(root: str) -> list[str]:
    """Extracts project dependencies from pyproject.toml or requirements.txt.

    Args:
        root: Project root directory.

    Returns:
        A list of dependency strings.
    """
    data = _load_pyproject(Path(root))
    if data is not None:
        deps = data.get("project", {}).get("dependencies")
        if isinstance(deps, list):
            return deps

    req_path = Path(root) / "requirements.txt"
    if req_path.exists():
        try:
            return [
                line.strip()
                for line in req_path.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.startswith("#")
            ]
        except Exception:
            logger.debug("Failed to read requirements.txt", exc_info=True)

    return []


def truncate_line(line: str, max_chars: int = 300) -> str:
    """Truncates a line to a maximum number of characters.

    Args:
        line: The line to truncate.
        max_chars: The maximum number of characters allowed.

    Returns:
        The truncated line with an ellipsis if it exceeded the limit.
    """
    if len(line) <= max_chars:
        return line
    return line[: max_chars - 3] + "..."


def format_fenced_block(content: str, lang: str = "text") -> str:
    """Formats content into a fenced code block, replacing inner backticks.

    Replaces '```' with "'''" inside the content to prevent breaking the
    outer markdown block.

    Args:
        content: The content to wrap in a fenced block.
        lang: The language identifier for the block.

    Returns:
        The formatted fenced code block string.
    """
    safe_content = content.replace("```", "'''")
    return f"```{lang}\n{safe_content}\n```"
