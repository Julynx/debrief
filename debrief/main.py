"""Main entry point for the debrief tool."""

import argparse
import logging
import os

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


def parse_arguments():
    """Parses command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Generate a BRIEF.md file.")
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

    return parser.parse_args()


def main():
    """Main entry point for the debrief tool.

    Scans the project, resolves readme and requirements, generates a tree,
    analyzes the codebase, and writes a BRIEF.md file.
    """
    args = parse_arguments()
    root = os.path.abspath(args.path)
    patterns = load_gitignore(root)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    logging.info(f"🔍 Scanning {root}...")
    linter = ProjectLinter(root)

    readme_path = resolve_readme(root)
    linter.check_metadata()

    readme_content = "_README is empty or missing._"
    if readme_path:
        with open(readme_path, "r", encoding="utf-8") as readme_file:
            lines = readme_file.read().splitlines()
            readme_content = "\n".join(
                [truncate_line(line) for line in lines[: args.max_readme]]
            )
            if len(lines) > args.max_readme:
                link = f"file:///{readme_path.replace(os.sep, '/')}"
                readme_content += f"\n... (truncated) [Read more]({link})"

    deps_content = "_No dependencies found._"
    deps = get_project_dependencies(root)
    if deps:
        dep_file_path = (
            "pyproject.toml"
            if os.path.exists(os.path.join(root, "pyproject.toml"))
            else "requirements.txt"
        )
        abs_dep_path = os.path.join(root, dep_file_path)

        deps_content = "\n".join(
            [truncate_line(dependency) for dependency in deps[: args.max_deps]]
        )
        if len(deps) > args.max_deps:
            link = f"file:///{abs_dep_path.replace(os.sep, '/')}"
            deps_content += f"\n... (truncated) [Read more]({link})"

    max_tree_siblings = (
        args.max_tree_siblings
        if args.max_tree_siblings is not None
        else max(1, args.tree_budget // 3)
    )
    tree_str = get_adaptive_tree(root, args.tree_budget, patterns, max_tree_siblings)
    tree_content = "\n".join([truncate_line(line) for line in tree_str.splitlines()])

    analyzer = Analyzer(
        root, linter, patterns, include_docstrings=args.include_docstrings
    )
    analyzer.scan()
    linter.print_summary()

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
