# Project Context: project-inspector

## 1. Overview (README)

```markdown
_README is empty or missing._
```

## 2. Dependencies

```text
_No requirements.txt found._
```

## 3. Directory Structure

```text
project-inspector/
├── project_inspector
    ├── __init__.py
    ├── analysis.py
    ├── constants.py
    ├── ignore.py
    ├── linting.py
    ├── main.py
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
- project_inspector\__init__.py

- project_inspector\main.py
  - project_inspector\analysis.py
    - project_inspector\ignore.py
      - project_inspector\constants.py
  - project_inspector\ignore.py (...)
  - project_inspector\linting.py
  - project_inspector\tree.py
    - project_inspector\ignore.py (...)
```

## 5. Module Definitions

### project_inspector\analysis.py

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

### project_inspector\ignore.py

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

### project_inspector\linting.py

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

### project_inspector\main.py

```text
- def parse_arguments()
- def main()
```

### project_inspector\tree.py

```text
- def generate_tree_at_depth(root_path, max_depth, patterns)
- def get_adaptive_tree(root_path, max_lines, patterns)
```
