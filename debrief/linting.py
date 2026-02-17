"""Project health metrics and linting utilities."""

import ast

from debrief.constants import DOC_THRESHOLD_OK, DOC_THRESHOLD_WARN
from debrief.resolve import check_dependencies, log


class ProjectLinter:
    """Computes project health metrics, such as docstring coverage."""

    def __init__(self, root_path):
        """Initializes the ProjectLinter.

        Args:
            root_path: Project root path.
        """
        self.root = root_path
        self.doc_stats = {"total": 0, "missing": 0}

    def check_metadata(self):
        """Checks for pyproject.toml / requirements.txt presence."""
        check_dependencies(self.root)

    def track_doc(self, node):
        """Updates docstring statistics for a given AST node.

        Args:
            node: The AST node (FunctionDef, ClassDef, etc).
        """
        self.doc_stats["total"] += 1
        if not ast.get_docstring(node):
            self.doc_stats["missing"] += 1

    def print_summary(self):
        """Prints a summary of the docstring coverage."""
        total = self.doc_stats["total"]
        if total > 0:
            missing = self.doc_stats["missing"]
            coverage = ((total - missing) / total) * 100
            if coverage > DOC_THRESHOLD_OK:
                level = "OK"
            elif coverage > DOC_THRESHOLD_WARN:
                level = "WARN"
            else:
                level = "FAIL"
            log(
                level,
                f"Docstring Coverage: {coverage:.1f}% ({total - missing}/{total})",
            )
