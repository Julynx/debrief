import ast
import os

from .ignore import is_ignored


class Analyzer:
    def __init__(self, root, linter, patterns):
        self.root = os.path.abspath(root)
        self.linter = linter
        self.patterns = patterns
        self.definitions = []
        # Maps relative file path -> set of imported relative file paths
        self.import_graph = {}

    def get_arg_str(self, arg):
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
        """
        Resolves an AST import node to a potential local file path.
        Returns the relative path from self.root if found, else None.
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

        # Candidate 1: module.py
        candidate_py = os.path.join(base_dir, *parts) + ".py"
        # Candidate 2: module/__init__.py
        candidate_pkg = os.path.join(base_dir, *parts, "__init__.py")

        target = None
        if os.path.isfile(candidate_py):
            target = candidate_py
        elif os.path.isfile(candidate_pkg):
            target = candidate_pkg

        if target and target.startswith(self.root):
            return os.path.relpath(target, self.root)

        return None

    def scan(self):
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [
                d
                for d in dirs
                if not is_ignored(os.path.join(root, d), self.root, self.patterns)
            ]
            for file in files:
                if file.endswith(".py"):
                    full = os.path.join(root, file)
                    if is_ignored(full, self.root, self.patterns):
                        continue
                    rel = os.path.relpath(full, self.root)
                    self.analyze_file(full, rel)

    def analyze_file(self, path, rel_path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception:
            return

        file_defs = []

        # Initialize import set for this file
        if rel_path not in self.import_graph:
            self.import_graph[rel_path] = set()

        for node in tree.body:
            # --- 1. Handle Imports ---
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

            # --- 2. Handle Classes ---
            elif isinstance(node, ast.ClassDef):
                self.linter.track_doc(node)
                bases = [ast.unparse(b) for b in node.bases]
                base_str = f"({', '.join(bases)})" if bases else ""
                file_defs.append(f"- class {node.name}{base_str}")
                file_defs.extend(self._format_docstring(node, 2))

                m_count = 0
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and not item.name.startswith(
                        "_"
                    ):
                        if m_count < 5:
                            self.linter.track_doc(item)
                            args = [self.get_arg_str(a) for a in item.args.args]
                            file_defs.append(f"  - def {item.name}({', '.join(args)})")
                            file_defs.extend(self._format_docstring(item, 4))
                            m_count += 1

            # --- 3. Handle Top-Level Functions ---
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    self.linter.track_doc(node)
                    args = [self.get_arg_str(a) for a in node.args.args]
                    ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
                    file_defs.append(f"- def {node.name}({', '.join(args)}){ret}")
                    file_defs.extend(self._format_docstring(node, 2))

        if file_defs:
            self.definitions.append(f"### {rel_path}\n")
            self.definitions.append("```text")
            self.definitions.extend(file_defs)
            self.definitions.append("```\n")

    def get_import_tree(self):
        """
        Generates a string representation of the local import tree.
        Subtrees that have been printed previously are abbreviated with (...).
        """
        if not self.import_graph:
            return "No imports found."

        # Find all files that are imported by at least one other file
        imported_files = set()
        for imports in self.import_graph.values():
            imported_files.update(imports)

        # Identify 'roots': files present in graph but not imported by others
        roots = sorted([f for f in self.import_graph if f not in imported_files])

        # Fallback if circular dependencies leave no roots
        if not roots:
            roots = sorted(self.import_graph.keys())

        output = []

        # Track which nodes have been fully expanded in the output already
        globally_visited = set()
        # Track current recursion path to detect immediate cycles
        current_path = set()

        def _build_tree(file_node, prefix=""):
            # Check for immediate recursion cycle
            if file_node in current_path:
                output.append(f"{prefix}- {file_node} (cycle)")
                return

            # Check if we have already printed the tree for this node elsewhere
            if file_node in globally_visited:
                output.append(f"{prefix}- {file_node} (...)")
                return

            # Print the node
            output.append(f"{prefix}- {file_node}")

            # Mark as visited globally so future references are abbreviated
            globally_visited.add(file_node)

            children = sorted(list(self.import_graph.get(file_node, [])))
            if children:
                current_path.add(file_node)
                for child in children:
                    _build_tree(child, prefix + "  ")
                current_path.remove(file_node)

        for root in roots:
            _build_tree(root)
            output.append("")

        return "\n".join(output).strip()
