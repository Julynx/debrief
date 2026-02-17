# TODO

- [x] Create a new resolve.py module and move all the logic to resolve paths to it. These functions will be imported and used in both linting and BRIEF.md generation.
  - Any functions that "fetch" from the project (eg. for getting the README.md file or the project dependencies), and any assumptions / deductions that are made to get there belong in this module.
  - These functions should try a reasonable set of conventions in the correct order, and warn if the target file is empty or missing, as well as if it has a default (unchanged) value.
  - For missing files, the error message should tell the user to ensure they are running the tool in the root of the project.
- [ ] Remove print statements entirely and replace them with logging calls of the appropriate severity.
- [ ] Remove all inline comments. Add/update high quality module, class and function/method docstrings to the project.
- [ ] Parse and display description from pyproject.toml
- [ ] Parse dependencies from pyproject.toml, falling back to requirements.txt if not present.
- [ ] Ellipsis and "read more" links for sections that are cut off by max lines budgets or other constraints.
- [ ] Max defintions in definition tree, plus ensure every single section has a max lines budget with a sensible default.
- [ ] Line width ellipsis for lines of any section that are too long (more than 300 chars).
