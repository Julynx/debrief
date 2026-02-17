"""Project-wide constants for debrief."""

DEFAULT_IGNORE = [
    ".git",
    ".github",
    "__pycache__",
    "*.pyc",
    "BRIEF.md",
    "venv",
    ".venv",
    "env",
    ".env",
    "node_modules",
    ".idea",
    ".vscode",
    "build",
    "dist",
    "*.egg-info",
    ".mypy_cache",
    ".pytest_cache",
]

DOC_THRESHOLD_OK = 80
DOC_THRESHOLD_WARN = 40
MAX_CLASS_METHODS = 5
