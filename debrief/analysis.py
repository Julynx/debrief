"""Analyzes Python codebase to extract definitions and imports."""

import ast
import os

from .constants import MAX_CLASS_METHODS
from .ignore import is_ignored
from .resolve import format_fenced_block


class Analyzer:
    """Analyzes the Python codebase to extract definitions and imports."""

    def __init__(self, root, linter, patterns, include_docstrings=True):
        """Initializes the Analyzer.

        Args:
            root: Project root path.
            linter: ProjectLinter instance.
            patterns: List of gitignore patterns.
            include_docstrings: Whether to include docstrings in the output.
        """
        self.root = os.path.abspath(root)
        self.linter = linter
        self.patterns = patterns
        self.include_docstrings = include_docstrings
        self.definitions = []
        self.import_graph = {}

    def get_arg_str(self, arg):
        """Formats an argument node into a string representation."""
        sig = arg.arg
        if arg.annotation:
            try:
                sig += f": {ast.unparse(arg.annotation)}"
            except Exception:
                pass
        return sig

    def _format_docstring(self, node, indent_level):
        """Helper to format docstrings with correct indentation."""
        doc = ast.get_docstring(node)
        lines = []
        if doc:
            doc_str = f'"""\n{doc}\n"""'
            indent = " " * indent_level
            for line in doc_str.splitlines():
                lines.append(f"{indent}{line}")
        return lines

    def _resolve_import(self, current_file_abs, module, level=0):
        """Resolves an AST import node to a potential local file path.

        Args:
            current_file_abs: Absolute path of the current file.
            module: The module name being imported.
            level: The relative import level (0 for absolute).

        Returns:
            The relative path from self.root if found, else None.
        """
        if module is None:
            return None

        if level > 0:
            base_dir = os.path.dirname(current_file_abs)
            for _ in range(level - 1):
                base_dir = os.path.dirname(base_dir)
        else:
            base_dir = self.root

        parts = module.split(".")

        candidate_path = os.path.join(base_dir, *parts) + ".py"
        candidate_pkg = os.path.join(base_dir, *parts, "__init__.py")

        target = None
        if os.path.isfile(candidate_path):
            target = candidate_path
        elif os.path.isfile(candidate_pkg):
            target = candidate_pkg

        if target and target.startswith(self.root):
            return os.path.relpath(target, self.root)

        return None

    def scan(self):
        """Scans the project directory for Python files and analyzes them."""
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [
                dir_name
                for dir_name in dirs
                if not is_ignored(
                    os.path.join(root, dir_name), self.root, self.patterns
                )
            ]
            for file in files:
                if file.endswith(".py"):
                    full = os.path.join(root, file)
                    if is_ignored(full, self.root, self.patterns):
                        continue
                    rel = os.path.relpath(full, self.root)
                    self.analyze_file(full, rel)

    def _handle_import(self, node, path, rel_path):
        if isinstance(node, ast.Import):
            for alias in node.names:
                resolved = self._resolve_import(path, alias.name, level=0)
                if resolved:
                    self.import_graph[rel_path].add(resolved)
        elif isinstance(node, ast.ImportFrom):
            mod_name = node.module if node.module else ""
            resolved = self._resolve_import(path, mod_name, level=node.level)
            if resolved:
                self.import_graph[rel_path].add(resolved)

    def _handle_class(self, node, file_defs):
        self.linter.track_doc(node)
        bases = [ast.unparse(base_class) for base_class in node.bases]
        base_str = f"({', '.join(bases)})" if bases else ""
        file_defs.append(f"- class {node.name}{base_str}")
        if self.include_docstrings:
            file_defs.extend(self._format_docstring(node, 2))

        method_count = 0
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                if method_count < MAX_CLASS_METHODS:
                    self.linter.track_doc(item)
                    args = [self.get_arg_str(arg) for arg in item.args.args]
                    file_defs.append(f"  - def {item.name}({', '.join(args)})")
                    if self.include_docstrings:
                        file_defs.extend(self._format_docstring(item, 4))
                    method_count += 1

    def _handle_function(self, node, file_defs):
        if not node.name.startswith("_"):
            self.linter.track_doc(node)
            args = [self.get_arg_str(arg) for arg in node.args.args]
            ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
            file_defs.append(f"- def {node.name}({', '.join(args)}){ret}")
            if self.include_docstrings:
                file_defs.extend(self._format_docstring(node, 2))

    def analyze_file(self, path, rel_path):
        """Parses and analyzes a single Python file.

        Extracts imports, classes, and functions, and records definitions.

        Args:
            path: Absolute path to the file.
            rel_path: Relative path from the project root.
        """
        try:
            with open(path, "r", encoding="utf-8") as file_obj:
                tree = ast.parse(file_obj.read())
        except Exception:
            return

        file_defs = []

        if rel_path not in self.import_graph:
            self.import_graph[rel_path] = set()

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self._handle_import(node, path, rel_path)

            elif isinstance(node, ast.ClassDef):
                self._handle_class(node, file_defs)

            elif isinstance(node, ast.FunctionDef):
                self._handle_function(node, file_defs)

        if file_defs:
            self.definitions.append(f"\n### {rel_path}\n\n")
            block_content = "\n".join(file_defs)
            self.definitions.append(format_fenced_block(block_content, "text"))
            self.definitions.append("")

    def get_import_tree(self):
        """Generates a string representation of the local import tree.

        Subtrees that have been printed previously are abbreviated with (...).

        Returns:
            A string representing the import tree.
        """
        if not self.import_graph:
            return "No imports found."

        imported_files = set()
        for imports in self.import_graph.values():
            imported_files.update(imports)

        roots = sorted(
            [
                root_file
                for root_file in self.import_graph
                if root_file not in imported_files
            ]
        )

        if not roots:
            roots = sorted(self.import_graph.keys())

        output = []

        globally_visited = set()
        current_path = set()

        def _build_tree(file_node, prefix=""):
            if file_node in current_path:
                output.append(f"{prefix}- {file_node} (cycle)")
                return

            if file_node in globally_visited:
                output.append(f"{prefix}- {file_node} (...)")
                return

            output.append(f"{prefix}- {file_node}")

            globally_visited.add(file_node)

            children = sorted(self.import_graph.get(file_node, []))
            if children:
                current_path.add(file_node)
                for child in children:
                    _build_tree(child, prefix + "  ")
                current_path.remove(file_node)

        for root in roots:
            _build_tree(root)
            output.append("")

        return "\n".join(output).strip()
