# BRIEF: debrief

## 1. Overview (README)

```markdown

```

## 2. Dependencies

```text
_No requirements.txt found._
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
    - debrief\ignore.py
      - debrief\constants.py
  - debrief\ignore.py (...)
  - debrief\linting.py
  - debrief\resolve.py
  - debrief\tree.py
    - debrief\ignore.py (...)
```

## 5. Module Definitions

### debrief\analysis.py

```text
- class Analyzer
  - def get_arg_str(self, arg)
  - def scan(self)
  - def analyze_file(self, path, rel_path)
  - def get_import_tree(self)
    """
    Generates a string representation of the local import tree.
    Subtrees that have been printed previously are abbreviated with (...).
    """
```

### debrief\ignore.py

```text
- def load_gitignore(root_path)
  """
  Loads the .gitignore file from the root path
  
  Args:
      root_path (Path | str): The root path of the project.
  
  Returns:
      patterns (list): A list of patterns read from the
        .gitignore file
  """
- def is_ignored(path, root_path, patterns)
```

### debrief\linting.py

```text
- class ProjectLinter
  """
  Docstring for ProjectLinter
  """
  - def log(self, level, msg)
    """
    Docstring for log
    
    :param self: Description
    :param level: Description
    :param msg: Description
    """
  - def find_readme(self)
  - def check_metadata(self)
  - def track_doc(self, node)
  - def print_summary(self)
```

### debrief\main.py

```text
- def parse_arguments()
- def main()
```

### debrief\resolve.py

```text
- def log(level: str, msg: str) -> None
  """
  Log a message to stderr with an icon.
  
  :param level: keys: "FAIL", "WARN", "OK"
  :param msg: Message to log
  """
- def resolve_readme(root: str) -> Optional[str]
  """
  Find the README file in the project looking at standard locations.
  Logs success, warnings, or failures.
  
  :param root: Project root directory
  :return: Absolute path to README or None
  """
- def resolve_pyproject(root: str) -> Optional[str]
  """
  Find and validate pyproject.toml.
  
  :param root: Project root directory
  :return: Absolute path to pyproject.toml or None
  """
- def resolve_requirements(root: str) -> Optional[str]
  """
  Find requirements.txt.
  
  :param root: Project root directory
  :return: Absolute path to requirements.txt or None
  """
- def check_dependencies(root: str) -> None
  """
  Check if either pyproject.toml or requirements.txt exists.
  Logs WARN if neither is found.
  """
```

### debrief\tree.py

```text
- def generate_tree_at_depth(root_path, max_depth, patterns)
- def get_adaptive_tree(root_path, max_lines, patterns)
```
