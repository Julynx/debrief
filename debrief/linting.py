"""Project health metrics and linting utilities."""

import ast

from debrief.constants import (
    DOC_THRESHOLD_OK,
    DOC_THRESHOLD_WARN,
    MIN_DOCSTRING_CHARS,
)
from debrief.resolve import check_dependencies, log


class ProjectLinter:
    """Computes project health metrics, such as docstring coverage."""

    def __init__(self, root_path, include_docstrings=False):
        """Initializes the ProjectLinter.

        Args:
            root_path: Project root path.
            include_docstrings: Whether docstring length checks are active.
        """
        self.root = root_path
        self.include_docstrings = include_docstrings
        self.doc_stats = {"total": 0, "missing": 0}
        self.short_docstrings = []

    def check_metadata(self):
        """Checks for pyproject.toml / requirements.txt presence."""
        check_dependencies(self.root)

    def track_doc(self, node):
        """Updates docstring statistics for a given AST node.

        Args:
            node: The AST node (FunctionDef, ClassDef, etc).
        """
        self.doc_stats["total"] += 1
        docstring = ast.get_docstring(node)

        if not docstring:
            self.doc_stats["missing"] += 1
            return

        if self.include_docstrings:
            non_whitespace_count = len(
                docstring.replace(" ", "").replace("\n", "").replace("\t", "")
            )
            if non_whitespace_count < MIN_DOCSTRING_CHARS:
                name = getattr(node, "name", "<unknown>")
                self.short_docstrings.append(name)

    def print_summary(self):
        """Prints a summary of the docstring coverage."""
        total = self.doc_stats["total"]
        if total > 0:
            missing = self.doc_stats["missing"]
            coverage = ((total - missing) / total) * 100
            if coverage >= DOC_THRESHOLD_OK:
                level = "OK"
            elif coverage >= DOC_THRESHOLD_WARN:
                level = "WARN"
            else:
                level = "FAIL"
            log(
                level,
                f"Docstring Coverage: {coverage:.1f}% ({total - missing}/{total})",
            )

        for name in self.short_docstrings:
            log(
                "WARN",
                f"Docstring for '{name}' is very short"
                f" (less than {MIN_DOCSTRING_CHARS} non-whitespace chars).",
            )
