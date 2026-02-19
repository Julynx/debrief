"""Tests for the lint variables and brief lint mode."""

import ast
import logging
import os
import textwrap

import pytest

from debrief.linting import ProjectLinter
from debrief.main import main
from debrief.resolve import resolve_pyproject, resolve_readme


@pytest.fixture()
def project_directory(tmp_path):
    """Creates a minimal project directory for testing."""
    return tmp_path


def _write_pyproject(directory, description=""):
    """Writes a minimal pyproject.toml with the given description."""
    content = textwrap.dedent(f"""\
        [project]
        name = "test-project"
        version = "0.1.0"
        description = "{description}"
    """)
    (directory / "pyproject.toml").write_text(content, encoding="utf-8")


def test_short_readme_warns(project_directory, caplog):
    """Verifies that a short README triggers a warning."""
    (project_directory / "README.md").write_text("# Title\n", encoding="utf-8")
    resolve_readme(str(project_directory))
    assert any("very short" in record.message for record in caplog.records)


def test_valid_readme_passes(project_directory, caplog):
    """Verifies that a README meeting the threshold logs OK."""
    (project_directory / "README.md").write_text(
        "# Title\nSome description here\n", encoding="utf-8"
    )
    with caplog.at_level(logging.DEBUG):
        resolve_readme(str(project_directory))
    assert any("Found README" in record.message for record in caplog.records)


def test_short_description_warns(project_directory, caplog):
    """Verifies that a short pyproject.toml description triggers WARN."""
    _write_pyproject(project_directory, description="Short")
    resolve_pyproject(str(project_directory))
    assert any("very short" in record.message for record in caplog.records)


def test_valid_description_passes(project_directory, caplog):
    """Verifies that a long enough description logs OK."""
    _write_pyproject(
        project_directory,
        description="A sufficiently long project description",
    )
    with caplog.at_level(logging.DEBUG):
        resolve_pyproject(str(project_directory))
    assert any("Found pyproject.toml" in record.message for record in caplog.records)


def test_short_docstring_warns(project_directory, caplog):
    """Verifies that a tiny docstring triggers WARN."""
    source_file = project_directory / "example.py"
    source_file.write_text(
        'def foo():\n    """Hi."""\n    pass\n',
        encoding="utf-8",
    )

    linter = ProjectLinter(str(project_directory), include_docstrings=True)
    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            linter.track_doc(node)

    linter.print_summary()
    assert any("very short" in record.message for record in caplog.records)


def test_docstring_skip_no_flag(project_directory, caplog):
    """Verifies short docstrings are ignored without the flag."""
    source_file = project_directory / "example.py"
    source_file.write_text(
        'def foo():\n    """Hi."""\n    pass\n',
        encoding="utf-8",
    )

    linter = ProjectLinter(str(project_directory), include_docstrings=False)
    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            linter.track_doc(node)

    linter.print_summary()
    assert not any("very short" in record.message for record in caplog.records)


def test_lint_mode_no_brief(project_directory, monkeypatch):
    """Verifies that lint mode does not produce a BRIEF.md file."""
    (project_directory / "README.md").write_text(
        "# Title\nSome description\n", encoding="utf-8"
    )
    _write_pyproject(
        project_directory,
        description="A sufficiently long project description",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["debrief", "lint", str(project_directory)],
    )

    with pytest.raises(SystemExit) as raised_exit:
        main()

    assert raised_exit.value.code == 0
    brief_path = os.path.join(str(project_directory), "BRIEF.md")
    assert not os.path.exists(brief_path)
