# -*- coding: utf-8 -*-

"""
L3: render the template with the seed's own values and compare the result
with the staged seed files. Exits 1 on any unexpected difference.

Allowed differences (03-parameterization.md, "Round Trip"):

- files matched by ``EXCLUDE`` exist only in the seed,
- files in ``HOOK_OUTPUTS`` may differ or exist only on one side.
"""

import difflib
from pathlib import Path

import pathspec
from cookiecutter.main import cookiecutter

import cctpl
import make_template


def _first_diff(a: bytes, b: bytes) -> str:
    try:
        lines_a = a.decode("utf-8").splitlines()
        lines_b = b.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return "    (binary content differs)"
    diff = difflib.unified_diff(lines_a, lines_b, "seed", "roundtrip", n=0, lineterm="")
    return "\n".join(f"    {line}" for line in list(diff)[2:8])


def main() -> int:
    dir_seed = cctpl.dir_stage / make_template.dir_seed.name
    cctpl.require_dir(dir_seed, "mise run make-template")
    cctpl.require_dir(cctpl.dir_template, "mise run make-template")

    cctpl.reset_dir(cctpl.dir_roundtrip)
    dir_out = Path(
        cookiecutter(
            str(cctpl.dir_template),
            no_input=True,
            extra_context=make_template.get_seed_context(),
            output_dir=str(cctpl.dir_roundtrip),
        )
    )

    excluded = pathspec.GitIgnoreSpec.from_lines(make_template.EXCLUDE)
    hook_outputs = set(make_template.HOOK_OUTPUTS)

    def files(root):
        return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}

    seed_files = files(dir_seed)
    out_files = files(dir_out)
    problems: list[str] = []

    for rel in sorted(seed_files - out_files):
        if rel in hook_outputs or excluded.match_file(rel):
            continue
        problems.append(f"{rel}: missing from round trip output")
    for rel in sorted(out_files - seed_files):
        if rel in hook_outputs:
            continue
        problems.append(f"{rel}: only in round trip output")
    for rel in sorted(seed_files & out_files):
        if rel in hook_outputs:
            continue
        a = (dir_seed / rel).read_bytes()
        b = (dir_out / rel).read_bytes()
        if a != b:
            problems.append(f"{rel}: content differs\n{_first_diff(a, b)}")

    if problems:
        print("=== Round trip differs from the seed ===")
        for line in problems:
            print(f"  {line}")
        print()
        print(f"FAILED: {len(problems)} difference(s). See 09-troubleshooting.md, L3.")
        return 1
    print(f"OK: round trip matches the seed ({len(seed_files & out_files)} files compared).")
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
