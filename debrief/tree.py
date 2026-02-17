"""Directory tree generation utilities."""

import os

from .ignore import is_ignored


def generate_tree_at_depth(root_path, max_depth, patterns):
    """Generates a directory tree string up to a specific depth.

    Args:
        root_path: The root directory to start the tree from.
        max_depth: The maximum depth to traverse.
        patterns: List of gitignore patterns to exclude.

    Returns:
        A string representing the directory tree.
    """
    lines = []

    def walk(path, current_depth):
        if current_depth > max_depth:
            return
        try:
            items = os.listdir(path)
        except PermissionError:
            return

        items = sorted(
            items, key=lambda x: (not os.path.isdir(os.path.join(path, x)), x)
        )
        filtered_items = []
        for item in items:
            full_path = os.path.join(path, item)
            if not is_ignored(full_path, root_path, patterns):
                filtered_items.append(item)

        for index, item in enumerate(filtered_items):
            is_last = index == len(filtered_items) - 1
            prefix = "└── " if is_last else "├── "
            indent = "    " * current_depth
            lines.append(f"{indent}{prefix}{item}")

            full = os.path.join(path, item)
            if os.path.isdir(full):
                walk(full, current_depth + 1)

    lines.append(os.path.basename(root_path) + "/")
    walk(root_path, 0)
    return "\n".join(lines)


def get_adaptive_tree(root_path, max_lines, patterns):
    """Generates a directory tree that fits within a line budget.

    Iteratively increases depth until the tree exceeds max_lines,
    then returns the best fitting previous version.

    Args:
        root_path: The root directory.
        max_lines: The maximum number of lines allowed for the tree.
        patterns: List of gitignore patterns.

    Returns:
        The generated tree string.
    """
    best_tree = ""
    last_count = 0
    for depth in range(1, 10):
        tree = generate_tree_at_depth(root_path, depth, patterns)
        count = len(tree.splitlines())
        if count > max_lines:
            if 0 < last_count < (max_lines * 0.2):
                return tree
            if depth == 1:
                return tree
            return best_tree
        if count == last_count and depth > 1:
            return tree
        best_tree = tree
        last_count = count
    return best_tree
