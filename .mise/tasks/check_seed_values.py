# -*- coding: utf-8 -*-

"""
L1: scan the template dir for unique seed values that should have become
``{{ cookiecutter.xxx }}`` placeholders, and for parameters that matched
nothing in the seed. Exits 1 on any problem.

Only ``UNIQUE_SEED_VALUES`` are scanned for residue; generic values appear
legitimately elsewhere. Declared ``LEGAL_RESIDUES`` are allowed.
"""

import cctpl
import make_template


def main() -> int:
    dir_template = cctpl.dir_template / cctpl.TEMPLATE_DIR_NAME
    cctpl.require_dir(dir_template, "mise run make-template")

    allowed = {(name, path) for name, path, _ in make_template.LEGAL_RESIDUES}
    used: set[tuple[str, str]] = set()
    problems: list[str] = []

    # File and directory names
    for path in sorted(dir_template.rglob("*")):
        rel = str(path.relative_to(dir_template))
        for name, value in make_template.UNIQUE_SEED_VALUES.items():
            if value in path.name:
                problems.append(f"{rel}: [{name}] {value!r} in path name")

    # File contents
    for rel, text in cctpl.iter_text_files(dir_template):
        for name, value in make_template.UNIQUE_SEED_VALUES.items():
            if value not in text:
                continue
            if (name, rel) in allowed:
                used.add((name, rel))
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                if value in line:
                    problems.append(f"{rel}:{lineno}: [{name}] {line.strip()[:160]}")

    for name, path in sorted(allowed - used):
        print(f"WARNING: stale legal residue, no longer present: [{name}] {path}")

    # Every parameter must hit at least once; a context selector that no
    # longer matches the seed fails silently otherwise.
    corpus = [str(p.relative_to(cctpl.dir_template)) for p in cctpl.dir_template.rglob("*")]
    corpus.extend(text for _, text in cctpl.iter_text_files(cctpl.dir_template))
    corpus = "\n".join(corpus)
    for param in make_template.PARAMETERS:
        if param.custom_placeholder:
            needle = param.custom_placeholder
        else:
            needle = f"cookiecutter.{param.name}"
        if needle not in corpus:
            problems.append(
                f"[{param.name}] parameter matched nothing in the seed "
                f"(selector {param.selector[0]!r})"
            )

    if problems:
        print("=== Seed value problems ===")
        for line in problems:
            print(f"  {line}")
        print()
        print(
            f"FAILED: {len(problems)} problem(s). Add, scope, or fix a parameter in "
            f"make_template.py, or declare a legal residue (05-parameterization.md)."
        )
        return 1
    print(
        f"OK: no undeclared residue of {len(make_template.UNIQUE_SEED_VALUES)} unique "
        f"seed values ({len(used)} declared residues); all "
        f"{len(make_template.PARAMETERS)} parameters matched."
    )
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
