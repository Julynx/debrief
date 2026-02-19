"""Directory tree generation utilities."""

import os

from .ignore import is_ignored


def generate_tree_at_depth(
    root_path: str,
    max_depth: int,
    patterns: list[str],
    max_siblings: int | None = None,
) -> str:
    """Generates a directory tree string up to a specific depth.

    Args:
        root_path: The root directory to start the tree from.
        max_depth: The maximum depth to traverse.
        patterns: List of gitignore patterns to exclude.
        max_siblings: Maximum number of items to show at each level.

    Returns:
        A string representing the directory tree.
    """
    lines: list[str] = []

    def walk(path: str, current_depth: int) -> None:
        if current_depth > max_depth:
            return
        try:
            items = os.listdir(path)
        except PermissionError:
            return

        items = sorted(
            items, key=lambda x: (not os.path.isdir(os.path.join(path, x)), x)
        )
        filtered_items = [
            item
            for item in items
            if not is_ignored(os.path.join(path, item), root_path, patterns)
        ]

        items_to_show = filtered_items
        hidden_count = 0
        if max_siblings is not None and len(filtered_items) > max_siblings:
            items_to_show = filtered_items[:max_siblings]
            hidden_count = len(filtered_items) - max_siblings

        for index, item in enumerate(items_to_show):
            is_last = index == len(items_to_show) - 1 and hidden_count == 0
            prefix = "└── " if is_last else "├── "
            indent = "    " * current_depth
            lines.append(f"{indent}{prefix}{item}")

            full = os.path.join(path, item)
            if os.path.isdir(full):
                walk(full, current_depth + 1)

        if hidden_count > 0:
            indent = "    " * current_depth
            lines.append(f"{indent}└── ... ({hidden_count} more items hidden)")

    lines.append(os.path.basename(root_path) + "/")
    walk(root_path, 0)
    return "\n".join(lines)


def get_adaptive_tree(
    root_path: str,
    max_lines: int,
    patterns: list[str],
    max_siblings: int | None = None,
) -> str:
    """Generates a directory tree that fits within a line budget.

    Iteratively increases depth until the tree exceeds max_lines,
    then returns the best fitting previous version.

    Args:
        root_path: The root directory.
        max_lines: The maximum number of lines allowed for the tree.
        patterns: List of gitignore patterns.
        max_siblings: Maximum number of items to show at each level.

    Returns:
        The generated tree string.
    """
    best_tree = ""
    last_count = 0
    for depth in range(1, 10):
        tree = generate_tree_at_depth(root_path, depth, patterns, max_siblings)
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
