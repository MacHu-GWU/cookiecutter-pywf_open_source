# -*- coding: utf-8 -*-

"""
Scan the generated template output directory for unresolved
``{{ cookiecutter.`` placeholders in file/directory names and file contents.
"""

import sys
from pathlib import Path

dir_output = Path(__file__).absolute().parent.parent.parent / "tmp" / "output"


def main() -> int:
    if not dir_output.exists():
        print(f"Output directory does not exist: {dir_output}")
        print("Run 'mise run test-template' first.")
        return 1

    errors = 0
    placeholder = "{{ cookiecutter."

    # Check file/directory names
    bad_names = [
        p for p in dir_output.rglob("*") if "cookiecutter" in p.name
    ]
    if bad_names:
        print("=== Unresolved placeholders in file/directory names ===")
        for p in bad_names:
            print(f"  {p.relative_to(dir_output)}")
        print()
        errors += len(bad_names)

    # Check file contents (skip binary files)
    bad_lines: list[tuple[Path, int, str]] = []
    for p in sorted(dir_output.rglob("*")):
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, ValueError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if placeholder in line:
                bad_lines.append((p, lineno, line.strip()))

    if bad_lines:
        print("=== Unresolved placeholders in file contents ===")
        for p, lineno, line in bad_lines:
            print(f"  {p.relative_to(dir_output)}:{lineno}: {line}")
        print()
        errors += len(bad_lines)

    if errors == 0:
        print("All good! No unresolved placeholders found.")
        return 0
    else:
        print(f"FAILED: Found {errors} unresolved placeholder(s).")
        return 1


if __name__ == "__main__":
    sys.exit(main())
