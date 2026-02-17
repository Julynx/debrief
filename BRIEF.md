# BRIEF: debrief

> Dynamically generated BRIEF.md summaries for your Python projects, to make them accesible to new contributors or coding agents.

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

| Argument            | Description                                | Default    |
| :------------------ | :----------------------------------------- | :--------- |
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
  - def get_arg_str(self, arg)
  - def scan(self)
  - def analyze_file(self, path, rel_path)
  - def get_import_tree(self)
```

### debrief\ignore.py

```text
- def load_gitignore(root_path)
- def is_ignored(path, root_path, patterns)
```

### debrief\linting.py

```text
- class ProjectLinter
  - def log(self, level, msg)
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
- def resolve_readme(root: str) -> Optional[str]
- def resolve_pyproject(root: str) -> Optional[str]
- def resolve_requirements(root: str) -> Optional[str]
- def check_dependencies(root: str) -> None
- def get_project_description(root: str) -> Optional[str]
- def get_project_dependencies(root: str) -> List[str]
- def truncate_line(line: str, max_chars: int) -> str
- def format_fenced_block(content: str, lang: str) -> str
```

### debrief\tree.py

```text
- def generate_tree_at_depth(root_path, max_depth, patterns)
- def get_adaptive_tree(root_path, max_lines, patterns)
```
