# debrief: Project Summarizer

`debrief` generates a comprehensive `BRIEF.md` file designed to provide new contributors or coding agents with a high-density overview of a Python project.

## Installation

```bash
pip install debrief
```

## Usage

```bash
debrief [run|lint] [path] [--output BRIEF.md]
```

### Arguments

| Argument               | Description                                        | Default             |
| :--------------------- | :------------------------------------------------- | :------------------ |
| `mode`                 | `run` generates BRIEF.md, `lint` only runs checks. | `run`               |
| `path`                 | Project root path.                                 | `.`                 |
| `-o`, `--output`       | Output filename.                                   | `BRIEF.md`          |
| `--tree-budget`        | Max lines for Directory Tree (auto-depth).         | `60`                |
| `--max-tree-siblings`  | Max items at same level in tree.                   | `tree_budget/3`     |
| `--max-readme`         | Max lines to include from README.                  | `20`                |
| `--max-deps`           | Max lines for dependencies list.                   | `15`                |
| `--max-imports`        | Max lines for Import Tree.                         | `50`                |
| `--max-definitions`    | Max lines for Module Definitions.                  | `200`               |
| `--max-class-methods`  | Max public methods shown per class.                | `max_definitions/3` |
| `--max-module-defs`    | Max top-level defs shown per module.               | `max_definitions/3` |
| `--include-docstrings` | Include docstrings in the output.                  | `False`             |
| `--exclude`            | Additional patterns to exclude.                    | None                |

### Lint Mode

```bash
debrief lint [path]
```

Runs all quality checks without generating `BRIEF.md`:

| Check                  | Threshold         | Condition                        |
| :--------------------- | :---------------- | :------------------------------- |
| README non-empty lines | ≥ 2               | Always                           |
| Description length     | ≥ 16 non-ws chars | Always                           |
| Docstring length       | ≥ 16 non-ws chars | Only with `--include-docstrings` |

## Features

- **Project Metadata**: Extracts description and dependencies from `pyproject.toml` (with `requirements.txt` fallback).
- **Directory Tree**: Adaptive depth tree that fits within a line budget, respecting `.gitignore`.
- **Import Analysis**: Generates an import dependency tree to visualize project structure.
- **Code Definitions**: Extracts class and function signatures with docstrings for all Python files.
- **Optimized Output**:
  - **Truncation**: Automatically truncates long lines (>300 chars) and large sections.
  - **"Read more"**: Links to local files for truncated content.
  - **Markdown**: Formatted for optimal readability.

## Example Output (`BRIEF.md`)

The [BRIEF.md](BRIEF.md) file in this repository serves as a real example of the output of `debrief`.
