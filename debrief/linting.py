import ast
import sys


class ProjectLinter:
    """
    Docstring for ProjectLinter
    """

    def __init__(self, root_path):
        self.root = root_path
        self.doc_stats = {"total": 0, "missing": 0}

    def log(self, level, msg):
        """
        Docstring for log

        :param self: Description
        :param level: Description
        :param msg: Description
        """
        icon = "❌" if level == "FAIL" else "⚠️" if level == "WARN" else "✅"
        print(f"{icon}  {msg}", file=sys.stderr)

    def find_readme(self):
        from debrief.resolve import resolve_readme

        return resolve_readme(self.root)

    def check_metadata(self):
        from debrief.resolve import check_dependencies

        check_dependencies(self.root)

    def track_doc(self, node):
        self.doc_stats["total"] += 1
        if not ast.get_docstring(node):
            self.doc_stats["missing"] += 1

    def print_summary(self):
        total = self.doc_stats["total"]
        if total > 0:
            missing = self.doc_stats["missing"]
            coverage = ((total - missing) / total) * 100
            level = "OK" if coverage > 80 else "WARN" if coverage > 40 else "FAIL"
            self.log(
                level,
                f"Docstring Coverage: {coverage:.1f}% ({total - missing}/{total})",
            )
