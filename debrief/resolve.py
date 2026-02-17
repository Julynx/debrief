"""Utilities for resolving project files and parsing metadata."""

import logging
import os
import tomllib
from pathlib import Path
from typing import List, Optional


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


def resolve_readme(root: str) -> Optional[str]:
    """Finds the README file in the project looking at standard locations.

    Logs success, warnings, or failures.

    Args:
        root: Project root directory.

    Returns:
        Absolute path to README or None.
    """
    min_readme_lines = 3
    candidates = [
        "README.md",
        "docs/README.md",
        ".github/README.md",
        "readme.md",
    ]

    for rel_path in candidates:
        abs_path = os.path.join(root, rel_path)
        if os.path.exists(abs_path):
            rel = os.path.relpath(abs_path, root)

            try:
                text = Path(abs_path).read_text(encoding="utf-8")
            except Exception as e:
                log("FAIL", f"Could not read {rel}: {e}")
                continue

            lines = text.splitlines()

            if not text.strip():
                log("FAIL", f"README found at {rel} is empty!")
                return abs_path

            if len(lines) < min_readme_lines:
                log("WARN", f"{rel} is poor (less than {min_readme_lines} lines).")
            else:
                log("OK", f"Found README at {rel}")

            return abs_path

    log("FAIL", "No README found! (Checked root, docs/, .github/)")
    return None


def resolve_pyproject(root: str) -> Optional[str]:
    """Finds and validates pyproject.toml.

    Args:
        root: Project root directory.

    Returns:
        Absolute path to pyproject.toml or None.
    """
    toml_path = os.path.join(root, "pyproject.toml")
    if os.path.exists(toml_path):
        try:
            content = Path(toml_path).read_text(encoding="utf-8")
            if 'description = ""' in content or "Add your description" in content:
                log("FAIL", "pyproject.toml has empty/default description.")
            else:
                log("OK", "Found pyproject.toml")
            return toml_path
        except Exception:
            return None
    return None


def resolve_requirements(root: str) -> Optional[str]:
    """Finds requirements.txt.

    Args:
        root: Project root directory.

    Returns:
        Absolute path to requirements.txt or None.
    """
    req_path = os.path.join(root, "requirements.txt")
    if os.path.exists(req_path):
        return req_path
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
    toml_path = os.path.join(root, "pyproject.toml")
    if not os.path.exists(toml_path):
        return None

    try:
        with open(toml_path, "rb") as toml_file:
            data = tomllib.load(toml_file)
            return data.get("project", {}).get("description")
    except Exception:
        return None


def get_project_dependencies(root: str) -> List[str]:
    """Extracts project dependencies from pyproject.toml or requirements.txt.

    Args:
        root: Project root directory.

    Returns:
        A list of dependency strings.
    """
    toml_path = os.path.join(root, "pyproject.toml")
    if os.path.exists(toml_path):
        try:
            with open(toml_path, "rb") as toml_file:
                data = tomllib.load(toml_file)
                deps = data.get("project", {}).get("dependencies")
                if isinstance(deps, list):
                    return deps
        except Exception:
            pass

    req_path = os.path.join(root, "requirements.txt")
    if os.path.exists(req_path):
        try:
            with open(req_path, "r", encoding="utf-8") as requirements_file:
                return [
                    line.strip()
                    for line in requirements_file
                    if line.strip() and not line.startswith("#")
                ]
        except Exception:
            pass

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
