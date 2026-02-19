"""Main entry point for the debrief tool."""

import argparse
import logging
import os
import sys
from pathlib import Path

from debrief.analysis import Analyzer
from debrief.ignore import load_gitignore
from debrief.linting import ProjectLinter
from debrief.resolve import (
    format_fenced_block,
    get_project_dependencies,
    get_project_description,
    resolve_readme,
    truncate_line,
)
from debrief.tree import get_adaptive_tree

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Generate a BRIEF.md file.")

    parser.add_argument(
        "mode",
        nargs="?",
        default="run",
        choices=["run", "lint"],
        help="Mode: 'run' generates BRIEF.md (default), 'lint' only runs checks",
    )
    parser.add_argument("path", nargs="?", default=".", help="Project root path")
    parser.add_argument("-o", "--output", default="BRIEF.md", help="Output filename")

    parser.add_argument(
        "--tree-budget",
        type=int,
        default=60,
        help="Max lines for Directory Tree (auto-depth)",
    )
    parser.add_argument(
        "--max-readme", type=int, default=20, help="Max lines from README"
    )
    parser.add_argument(
        "--max-deps", type=int, default=15, help="Max lines from requirements.txt"
    )
    parser.add_argument(
        "--max-imports", type=int, default=50, help="Max lines for Import Tree"
    )
    parser.add_argument(
        "--max-definitions",
        type=int,
        default=200,
        help="Max lines for Module Definitions",
    )

    parser.add_argument(
        "--include-docstrings",
        action="store_true",
        help="Include docstrings in the output",
    )
    parser.add_argument(
        "--max-tree-siblings",
        type=int,
        default=None,
        help="Max items at same level in tree (default: tree_budget/3)",
    )
    parser.add_argument(
        "--max-class-methods",
        type=int,
        default=None,
        help="Max public methods per class (default: max_definitions/3)",
    )
    parser.add_argument(
        "--max-module-defs",
        type=int,
        default=None,
        help="Max top-level defs per module (default: max_definitions/3)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        help="Additional patterns to exclude (can be used multiple times)",
    )

    return parser.parse_args()


def _read_readme(root: str, max_lines: int) -> str:
    """Reads the README file and returns its truncated content.

    Args:
        root: Absolute path to the project root.
        max_lines: Maximum number of lines to include.

    Returns:
        The README content as a string.
    """
    readme_path = resolve_readme(root)
    if not readme_path:
        return "_README is empty or missing._"

    try:
        text = Path(readme_path).read_text(encoding="utf-8")
    except Exception:
        logger.debug("Could not read README at %s", readme_path, exc_info=True)
        return "_README is empty or missing._"

    lines = text.splitlines()
    content = "\n".join([truncate_line(line) for line in lines[:max_lines]])
    if len(lines) > max_lines:
        link = f"file:///{readme_path.replace(os.sep, '/')}"
        content += f"\n... (truncated) [Read more]({link})"
    return content


def _build_deps_content(root: str, max_deps: int) -> str:
    """Builds the dependencies content string.

    Args:
        root: Absolute path to the project root.
        max_deps: Maximum number of dependency lines to include.

    Returns:
        The dependencies content as a string.
    """
    deps = get_project_dependencies(root)
    if not deps:
        return "_No dependencies found._"

    dep_file_path = (
        "pyproject.toml"
        if Path(root, "pyproject.toml").exists()
        else "requirements.txt"
    )
    abs_dep_path = Path(root) / dep_file_path

    content = "\n".join([truncate_line(dependency) for dependency in deps[:max_deps]])
    if len(deps) > max_deps:
        link = f"file:///{str(abs_dep_path).replace(os.sep, '/')}"
        content += f"\n... (truncated) [Read more]({link})"
    return content


def main() -> None:
    """Main entry point for the debrief tool.

    Scans the project, resolves readme and requirements, generates a tree,
    analyzes the codebase, and writes a BRIEF.md file.
    """
    args = parse_arguments()
    root = os.path.abspath(args.path)
    patterns = load_gitignore(root, args.exclude)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    logging.info(f"🔍 Scanning {root}...")

    readme_content = _read_readme(root, args.max_readme)

    linter = ProjectLinter(root, include_docstrings=args.include_docstrings)
    linter.check_metadata()

    max_class_methods = (
        args.max_class_methods
        if args.max_class_methods is not None
        else max(1, args.max_definitions // 3)
    )
    max_module_defs = (
        args.max_module_defs
        if args.max_module_defs is not None
        else max(1, args.max_definitions // 3)
    )

    analyzer = Analyzer(
        root,
        linter,
        patterns,
        include_docstrings=args.include_docstrings,
        max_class_methods=max_class_methods,
        max_module_defs=max_module_defs,
    )
    analyzer.scan()
    linter.print_summary()

    if args.mode == "lint":
        sys.exit(0)

    deps_content = _build_deps_content(root, args.max_deps)

    max_tree_siblings = (
        args.max_tree_siblings
        if args.max_tree_siblings is not None
        else max(1, args.tree_budget // 3)
    )
    tree_str = get_adaptive_tree(root, args.tree_budget, patterns, max_tree_siblings)
    tree_content = "\n".join([truncate_line(line) for line in tree_str.splitlines()])

    import_lines = analyzer.get_import_tree().splitlines()
    import_tree = "\n".join(
        [truncate_line(line) for line in import_lines[: args.max_imports]]
    )
    if len(import_lines) > args.max_imports:
        import_tree += "\n... (truncated)"

    def_lines = analyzer.definitions
    split_defs = []
    for block in def_lines:
        split_defs.extend(block.splitlines())

    definitions = "\n".join(
        [truncate_line(line) for line in split_defs[: args.max_definitions]]
    )
    if len(split_defs) > args.max_definitions:
        definitions += "\n... (truncated)"

    description = get_project_description(root)
    display_description = f"> {description}" if description else ""

    readme_block = format_fenced_block(readme_content, "markdown")
    deps_block = format_fenced_block(deps_content, "text")
    tree_block = format_fenced_block(tree_content, "text")
    import_block = format_fenced_block(import_tree, "text")

    final_markdown = f"""# BRIEF: {os.path.basename(root)}

{display_description}

## 1. Overview (README)

{readme_block}

## 2. Dependencies

{deps_block}

## 3. Directory Structure

{tree_block}

## 4. Import Tree

{import_block}

## 5. Module Definitions

{definitions.strip()}
"""

    with open(args.output, "w", encoding="utf-8") as output_file:
        output_file.write(final_markdown)

    logging.info(f"\n✅ Done! Context written to {args.output}")


if __name__ == "__main__":
    main()
