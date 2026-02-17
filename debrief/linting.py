import ast
import os
import sys
from pathlib import Path


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
        min_readme_lines = 3

        candidates = [
            os.path.join(self.root, "README.md"),
            os.path.join(self.root, "docs", "README.md"),
            os.path.join(self.root, ".github", "README.md"),
            os.path.join(self.root, "readme.md"),
        ]
        for path in candidates:
            if not os.path.exists(path):
                self.log("FAIL", "No README found! (Checked root, docs/, .github/)")
                return None

            rel = os.path.relpath(path, self.root)
            text = Path(path).read_text()
            lines = text.splitlines()

            if not text.strip():
                self.log("FAIL", f"README found at {rel} is empty!")
                return None

            if len(lines) < min_readme_lines:
                self.log("WARN", f"{rel} is poor (less than {min_readme_lines} lines).")
            else:
                self.log("OK", f"Found README at {rel}")

            return path

    def check_metadata(self):
        toml = os.path.join(self.root, "pyproject.toml")
        if os.path.exists(toml):
            try:
                with open(toml, "r") as f:
                    content = f.read()
                    if (
                        'description = ""' in content
                        or "Add your description" in content
                    ):
                        self.log(
                            "FAIL", "pyproject.toml has empty/default description."
                        )
                    else:
                        self.log("OK", "Found pyproject.toml")
            except Exception:
                pass
        elif not os.path.exists(os.path.join(self.root, "requirements.txt")):
            self.log(
                "WARN", "No dependencies found (no requirements.txt or pyproject.toml)."
            )

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
