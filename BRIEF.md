# BRIEF: debrief

> Dynamically generated BRIEF.md summaries for your Python projects, to make them accessible to new contributors or coding agents.

## 1. Overview (README)

```markdown
# debrief: Project Summarizer

`debrief` generates a comprehensive `BRIEF.md` file designed to provide new contributors or coding agents with a high-density overview of a Python project.

## Installation

'''bash
pip install debrief
'''

## Usage

'''bash
debrief [path] [--output BRIEF.md]
'''

### Arguments

| Argument | Description | Default |
| :------- | :---------- | :------ |

... (truncated) [Read more](file:///D:/_DISK_/_Documentos_/Mis_repositorios/debrief/README.md)
```

## 2. Dependencies

```text
_No dependencies found._
```

## 3. Directory Structure

```text
debrief/
├── debrief
    ├── __init__.py
    ├── analysis.py
    ├── constants.py
    ├── ignore.py
    ├── linting.py
    ├── main.py
    ├── resolve.py
    └── tree.py
├── .gitignore
├── .python-version
├── README.md
├── TODO.md
├── pyproject.toml
└── uv.lock
```

## 4. Import Tree

```text
- debrief\__init__.py

- debrief\main.py
  - debrief\analysis.py
    - debrief\constants.py
    - debrief\ignore.py
      - debrief\constants.py (...)
    - debrief\resolve.py
  - debrief\ignore.py (...)
  - debrief\linting.py
    - debrief\constants.py (...)
    - debrief\resolve.py (...)
  - debrief\resolve.py (...)
  - debrief\tree.py
    - debrief\ignore.py (...)
```

## 5. Module Definitions

### debrief\analysis.py

```text
- class Analyzer
  """
  Analyzes the Python codebase to extract definitions and imports.
  """
  - def get_arg_str(self, arg)
    """
    Formats an argument node into a string representation.
    """
  - def scan(self)
    """
    Scans the project directory for Python files and analyzes them.
    """
  - def analyze_file(self, path, rel_path)
    """
    Parses and analyzes a single Python file.

    Extracts imports, classes, and functions, and records definitions.

    Args:
        path: Absolute path to the file.
        rel_path: Relative path from the project root.
    """
  - def get_import_tree(self)
    """
    Generates a string representation of the local import tree.

    Subtrees that have been printed previously are abbreviated with (...).

    Returns:
        A string representing the import tree.
    """
```

### debrief\ignore.py

```text
- def load_gitignore(root_path)
  """
  Loads the .gitignore file from the root path.

  Args:
      root_path: The root path of the project.

  Returns:
      List[str]: A list of patterns read from the .gitignore file.
  """
- def is_ignored(path, root_path, patterns)
  """
  Checks if a file path matches any of the ignore patterns.

  Args:
      path: Path to check.
      root_path: Project root directory.
      patterns: List of ignore patterns.

  Returns:
      True if the path should be ignored, False otherwise.
  """
```

### debrief\linting.py

```text
- class ProjectLinter
  """
  Computes project health metrics, such as docstring coverage.
  """
  - def check_metadata(self)
    """
    Checks for pyproject.toml / requirements.txt presence.
    """
  - def track_doc(self, node)
    """
    Updates docstring statistics for a given AST node.

    Args:
        node: The AST node (FunctionDef, ClassDef, etc).
    """
  - def print_summary(self)
    """
    Prints a summary of the docstring coverage.
    """
```

### debrief\main.py

```text
- def parse_arguments()
  """
  Parses command-line arguments.

  Returns:
      argparse.Namespace: The parsed arguments.
  """
- def main()
  """
  Main entry point for the debrief tool.

  Scans the project, resolves readme and requirements, generates a tree,
  analyzes the codebase, and writes a BRIEF.md file.
  """
```

### debrief\resolve.py

```text
- def log(level: str, msg: str) -> None
  """
  Logs a message with an icon based on the severity level.

  Args:
      level: The severity level ("FAIL", "WARN", "OK").
      msg: The message to log.
  """
- def resolve_readme(root: str) -> Optional[str]
  """
  Finds the README file in the project looking at standard locations.

  Logs success, warnings, or failures.

  Args:
      root: Project root directory.

  Returns:
      Absolute path to README or None.
  """
- def resolve_pyproject(root: str) -> Optional[str]
  """
  Finds and validates pyproject.toml.

  Args:
      root: Project root directory.

  Returns:
      Absolute path to pyproject.toml or None.
  """
- def resolve_requirements(root: str) -> Optional[str]
  """
  Finds requirements.txt.

  Args:
      root: Project root directory.

  Returns:
      Absolute path to requirements.txt or None.
  """
- def check_dependencies(root: str) -> None
  """
  Checks if either pyproject.toml or requirements.txt exists.

  Logs WARN if neither is found.

  Args:
      root: Project root directory.
  """
- def get_project_description(root: str) -> Optional[str]
  """
  Extracts the project description from pyproject.toml.

  Args:
      root: Project root directory.

  Returns:
      The project description string, or None if not found/error.
  """
- def get_project_dependencies(root: str) -> List[str]
  """
  Extracts project dependencies from pyproject.toml or requirements.txt.

  Args:
      root: Project root directory.

  Returns:
      A list of dependency strings.
  """
- def truncate_line(line: str, max_chars: int) -> str
  """
  Truncates a line to a maximum number of characters.

  Args:
      line: The line to truncate.
      max_chars: The maximum number of characters allowed.

  Returns:
      The truncated line with an ellipsis if it exceeded the limit.
  """
- def format_fenced_block(content: str, lang: str) -> str
  """
  Formats content into a fenced code block, replacing inner backticks.

  Replaces ''''' with "'''" inside the content to prevent breaking the
  outer markdown block.

  Args:
      content: The content to wrap in a fenced block.
      lang: The language identifier for the block.
... (truncated)
```
