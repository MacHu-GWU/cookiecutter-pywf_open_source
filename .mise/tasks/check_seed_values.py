# -*- coding: utf-8 -*-

"""
Scan the generated template directory for concrete seed values that should
have been replaced with ``{{ cookiecutter.xxx }}`` placeholders.

This runs AFTER ``make-template`` and BEFORE ``test-template``.
"""

import importlib.util
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Import SeedValues from make_template.py
_spec = importlib.util.spec_from_file_location(
    "make_template",
    Path(__file__).absolute().parent / "make_template.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SeedValues = _mod.SeedValues

dir_template = (
    Path(__file__).absolute().parent.parent.parent
    / "tmp"
    / "{{ cookiecutter.package_name }}-project"
)

# All seed values to scan for — (label, value)
CHECKS: list[tuple[str, str]] = [
    ("package_name", SeedValues.package_name),
    ("package_name_slug", SeedValues.package_name_slug),
    ("github_username", SeedValues.github_username),
    ("license", SeedValues.license),
    ("license_classifier", SeedValues.license_classifier),
    ("author", SeedValues.author),
    ("author_email", SeedValues.author_email),
    ("version", SeedValues.version),
    ("dev_python_version", SeedValues.dev_python_version),
    ("github_token_field", SeedValues.github_token_field),
    ("codecov_token_field", SeedValues.codecov_token_field),
    ("readthedocs_token_field", SeedValues.readthedocs_token_field),
]


def highlight_value(line: str, value: str) -> Text:
    """Build a Rich Text with all occurrences of ``value`` highlighted."""
    text = Text()
    start = 0
    while True:
        idx = line.find(value, start)
        if idx == -1:
            text.append(line[start:])
            break
        text.append(line[start:idx])
        text.append(value, style="bold red")
        start = idx + len(value)
    return text


def main() -> None:
    console = Console()

    if not dir_template.exists():
        console.print(
            f"[red]Template directory does not exist:[/red] {dir_template}"
        )
        console.print("Run 'mise run make-template' first.")
        return

    for label, value in CHECKS:
        table = Table(show_header=True, expand=True, show_lines=True)
        table.add_column("File", style="cyan", no_wrap=True, ratio=2)
        table.add_column("Line", style="yellow", justify="right", width=5)
        table.add_column("Content", ratio=5)

        # Check file/directory names
        for p in dir_template.rglob("*"):
            if value in p.name:
                rel = str(p.relative_to(dir_template))
                table.add_row(
                    highlight_value(rel, value),
                    "",
                    Text("(in path name)", style="dim"),
                )

        # Check file contents
        for p in sorted(dir_template.rglob("*")):
            if not p.is_file():
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, ValueError):
                continue
            rel = str(p.relative_to(dir_template))
            for lineno, line in enumerate(text.splitlines(), 1):
                if value in line:
                    table.add_row(
                        rel,
                        str(lineno),
                        highlight_value(line.strip(), value),
                    )

        panel = Panel(
            table if table.row_count > 0 else Text("No matches", style="green"),
            title=f"[bold]{label}[/bold] = [yellow]\"{value}\"[/yellow]",
            border_style="blue",
        )
        console.print(panel)


if __name__ == "__main__":
    main()
