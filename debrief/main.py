import argparse
import os

from debrief.analysis import Analyzer
from debrief.ignore import load_gitignore
from debrief.linting import ProjectLinter
from debrief.tree import get_adaptive_tree


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate a BRIEF.md file."
    )
    parser.add_argument("path", nargs="?", default=".", help="Project root path")
    parser.add_argument("-o", "--output", default="BRIEF.md", help="Output filename")

    # Adaptive Limits
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

    return parser.parse_args()


def main():
    args = parse_arguments()
    root = os.path.abspath(args.path)
    patterns = load_gitignore(root)

    print(f"🔍 Scanning {root}...")
    linter = ProjectLinter(root)

    readme_path = linter.find_readme()
    linter.check_metadata()

    readme_content = "_README is empty or missing._"
    if readme_path:
        with open(readme_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            readme_content = "\n".join(lines[: args.max_readme])
            if len(lines) > args.max_readme:
                readme_content += "\n... (truncated)"

    deps_content = "_No requirements.txt found._"
    req_path = os.path.join(root, "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r") as f:
            lines = f.read().splitlines()
            deps_content = "\n".join(lines[: args.max_deps])

    tree_content = get_adaptive_tree(root, args.tree_budget, patterns)

    analyzer = Analyzer(root, linter, patterns)
    analyzer.scan()
    linter.print_summary()

    definitions = "\n".join(analyzer.definitions)
    final_md = f"""# BRIEF: {os.path.basename(root)}

## 1. Overview (README)

```markdown
{readme_content}
```

## 2. Dependencies

```text
{deps_content}
```

## 3. Directory Structure

```text
{tree_content}
```

## 4. Import Tree

```text
{analyzer.get_import_tree()}
```

## 5. Module Definitions

{definitions.strip()}
"""

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(final_md)

    print(f"\n✅ Done! Context written to {args.output}")


if __name__ == "__main__":
    main()
