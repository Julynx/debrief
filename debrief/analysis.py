"""Analyzes Python codebase to extract definitions and imports."""

import ast
import logging
import os
from pathlib import Path

from .ignore import is_ignored
from .resolve import format_fenced_block

logger = logging.getLogger(__name__)


class Analyzer:
    """Analyzes the Python codebase to extract definitions and imports."""

    def __init__(
        self,
        root: str,
        linter: "ProjectLinter",  # noqa: F821
        patterns: list[str],
        include_docstrings: bool = True,
        max_class_methods: int = 5,
        max_module_defs: int = 20,
    ) -> None:
        """Initializes the Analyzer.

        Args:
            root: Project root path.
            linter: ProjectLinter instance.
            patterns: List of gitignore patterns.
            include_docstrings: Whether to include docstrings in the output.
            max_class_methods: Max public methods to show per class.
            max_module_defs: Max top-level definitions to show per module.
        """
        self.root = os.path.abspath(root)
        self.linter = linter
        self.patterns = patterns
        self.include_docstrings = include_docstrings
        self.max_class_methods = max_class_methods
        self.max_module_defs = max_module_defs
        self.definitions: list[str] = []
        self.import_graph: dict[str, set[str]] = {}

    def get_arg_str(self, arg: ast.arg) -> str:
        """Formats an argument node into a string representation."""
        sig = arg.arg
        if arg.annotation:
            try:
                sig += f": {ast.unparse(arg.annotation)}"
            except Exception:
                logger.debug(
                    "Failed to unparse annotation for %s", arg.arg, exc_info=True
                )
        return sig

    def _format_docstring(self, node: ast.AST, indent_level: int) -> list[str]:
        """Helper to format docstrings with correct indentation."""
        doc = ast.get_docstring(node)
        lines: list[str] = []
        if doc:
            doc_str = f'"""\n{doc}\n"""'
            indent = " " * indent_level
            for line in doc_str.splitlines():
                lines.append(f"{indent}{line}")
        return lines

    def _resolve_import(
        self, current_file_abs: str, module: str, level: int = 0
    ) -> str | None:
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

    def scan(self) -> None:
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

    def _handle_import(
        self, node: ast.Import | ast.ImportFrom, path: str, rel_path: str
    ) -> None:
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

    def _handle_class(self, node: ast.ClassDef, file_defs: list[str]) -> None:
        self.linter.track_doc(node)
        bases = [ast.unparse(base_class) for base_class in node.bases]
        base_str = f"({', '.join(bases)})" if bases else ""
        file_defs.append(f"- class {node.name}{base_str}")
        if self.include_docstrings:
            file_defs.extend(self._format_docstring(node, 2))

        method_count = 0
        for item in node.body:
            if isinstance(
                item, (ast.FunctionDef, ast.AsyncFunctionDef)
            ) and not item.name.startswith("_"):
                if method_count < self.max_class_methods:
                    self.linter.track_doc(item)
                    args = [self.get_arg_str(arg) for arg in item.args.args]
                    prefix = (
                        "async def" if isinstance(item, ast.AsyncFunctionDef) else "def"
                    )
                    file_defs.append(f"  - {prefix} {item.name}({', '.join(args)})")
                    if self.include_docstrings:
                        file_defs.extend(self._format_docstring(item, 4))
                    method_count += 1

    def _handle_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, file_defs: list[str]
    ) -> None:
        if not node.name.startswith("_"):
            self.linter.track_doc(node)
            args = [self.get_arg_str(arg) for arg in node.args.args]
            ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
            prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            file_defs.append(f"- {prefix} {node.name}({', '.join(args)}){ret}")
            if self.include_docstrings:
                file_defs.extend(self._format_docstring(node, 2))

    def analyze_file(self, path: str, rel_path: str) -> None:
        """Parses and analyzes a single Python file.

        Extracts imports, classes, and functions, and records definitions.

        Args:
            path: Absolute path to the file.
            rel_path: Relative path from the project root.
        """
        try:
            source = Path(path).read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            logger.debug("Failed to parse %s", rel_path, exc_info=True)
            return

        file_defs: list[str] = []
        def_count = 0

        if rel_path not in self.import_graph:
            self.import_graph[rel_path] = set()

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self._handle_import(node, path, rel_path)

            elif isinstance(node, ast.ClassDef):
                if def_count < self.max_module_defs:
                    self._handle_class(node, file_defs)
                    def_count += 1

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if def_count < self.max_module_defs:
                    self._handle_function(node, file_defs)
                    def_count += 1

        if file_defs:
            self.definitions.append(f"\n### {rel_path}\n\n")
            block_content = "\n".join(file_defs)
            self.definitions.append(format_fenced_block(block_content, "text"))
            self.definitions.append("")

    def _find_root_files(self) -> list[str]:
        """Finds root files that are not imported by any other file.

        Returns:
            List of root file paths sorted alphabetically.
        """
        imported_files: set[str] = set()
        for imports in self.import_graph.values():
            imported_files.update(imports)

        roots = [
            file_object
            for file_object in self.import_graph
            if file_object not in imported_files
        ]
        return sorted(roots) if roots else sorted(self.import_graph.keys())

    def _format_visited_node(
        self, file_node: str, prefix: str, children: list[str]
    ) -> str:
        """Formats a previously visited node with or without ellipsis.

        Args:
            file_node: The file node to format.
            prefix: The indentation prefix.
            children: List of child nodes.

        Returns:
            Formatted string for the node.
        """
        suffix = " (...)" if children else ""
        return f"{prefix}- {file_node}{suffix}"

    def get_import_tree(self) -> str:
        """Generates a string representation of the local import tree.

        Subtrees that have been printed previously are abbreviated with (...).

        Returns:
            A string representing the import tree.
        """
        if not self.import_graph:
            return "No imports found."

        roots = self._find_root_files()
        output: list[str] = []
        globally_visited: set[str] = set()
        current_path: set[str] = set()

        def _build_tree(file_node: str, prefix: str = "") -> None:
            if file_node in current_path:
                output.append(f"{prefix}- {file_node} (cycle)")
                return

            children = sorted(self.import_graph.get(file_node, []))
            if file_node in globally_visited:
                output.append(self._format_visited_node(file_node, prefix, children))
                return

            output.append(f"{prefix}- {file_node}")
            globally_visited.add(file_node)

            if children:
                current_path.add(file_node)
                for child in children:
                    _build_tree(child, prefix + "  ")
                current_path.remove(file_node)

        for root in roots:
            _build_tree(root)
            output.append("")

        return "\n".join(output).strip()
