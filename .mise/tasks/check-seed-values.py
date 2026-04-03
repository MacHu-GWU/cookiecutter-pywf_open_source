# -*- coding: utf-8 -*-

"""
Scan the generated template directory for concrete seed values that should
have been replaced with ``{{ cookiecutter.xxx }}`` placeholders.

This runs AFTER ``make-template`` and BEFORE ``test-template``.
"""

import sys
import importlib.util
from pathlib import Path

# Import SeedValues from make-template.py
_spec = importlib.util.spec_from_file_location(
    "make_template",
    Path(__file__).absolute().parent / "make-template.py",
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


def main() -> None:
    if not dir_template.exists():
        print(f"Template directory does not exist: {dir_template}")
        print("Run 'mise run make-template' first.")
        return

    for label, value in CHECKS:
        print(f"--- [{label}] = \"{value}\" ---")

        # Check file/directory names
        for p in dir_template.rglob("*"):
            if value in p.name:
                print(f"  name: {p.relative_to(dir_template)}")

        # Check file contents
        for p in sorted(dir_template.rglob("*")):
            if not p.is_file():
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, ValueError):
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                if value in line:
                    print(f"  {p.relative_to(dir_template)}:{lineno}: {line.strip()}")

        print()


if __name__ == "__main__":
    main()
