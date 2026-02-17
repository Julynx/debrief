import os
import sys
from pathlib import Path
from typing import Optional


def log(level: str, msg: str) -> None:
    """
    Log a message to stderr with an icon.

    :param level: keys: "FAIL", "WARN", "OK"
    :param msg: Message to log
    """
    icon = "❌" if level == "FAIL" else "⚠️" if level == "WARN" else "✅"
    print(f"{icon}  {msg}", file=sys.stderr)


def resolve_readme(root: str) -> Optional[str]:
    """
    Find the README file in the project looking at standard locations.
    Logs success, warnings, or failures.

    :param root: Project root directory
    :return: Absolute path to README or None
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
                return abs_path  # Return path even if empty so caller knows it exists

            if len(lines) < min_readme_lines:
                log("WARN", f"{rel} is poor (less than {min_readme_lines} lines).")
            else:
                log("OK", f"Found README at {rel}")

            return abs_path

    log("FAIL", "No README found! (Checked root, docs/, .github/)")
    return None


def resolve_pyproject(root: str) -> Optional[str]:
    """
    Find and validate pyproject.toml.

    :param root: Project root directory
    :return: Absolute path to pyproject.toml or None
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
    """
    Find requirements.txt.

    :param root: Project root directory
    :return: Absolute path to requirements.txt or None
    """
    req_path = os.path.join(root, "requirements.txt")
    if os.path.exists(req_path):
        # We don't log OK for requirements.txt in the original code unless
        # specifically asked, but the original code verified dependencies presence.
        # The original code logged WARN if NEITHER pyproject or requirements.txt existed.
        # We'll just return the path here.
        return req_path
    return None


def check_dependencies(root: str) -> None:
    """
    Check if either pyproject.toml or requirements.txt exists.
    Logs WARN if neither is found.
    """
    has_toml = resolve_pyproject(root) is not None
    has_req = resolve_requirements(root) is not None

    if not has_toml and not has_req:
        log("WARN", "No dependencies found (no requirements.txt or pyproject.toml).")
