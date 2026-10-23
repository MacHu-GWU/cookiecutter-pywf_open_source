# -*- coding: utf-8 -*-

"""
Check the shared version in the seed, before apply-template copies it into
the tpl repo. Local files only. Exits 1 on any problem.

- The seed version is ``major.minor.patch`` and not below the tpl version.
- The seed's own changelog (``release-history-seed-repo.rst``) has a section
  for it.
- The seed's ``release-history.rst``, which is template content, has no
  section for it: a seed release must never be recorded there.

Spec: 08-versioning-and-release.md.
"""

import cctpl


def _as_tuple(version: str) -> tuple[int, ...] | None:
    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return None
    return tuple(int(p) for p in parts)


def collect_problems() -> list[str]:
    """
    Return one line per problem with the seed version; empty when it is valid.
    """
    dir_seed = cctpl.get_seed_dir()
    version = cctpl.get_seed_version()
    tpl_version = cctpl.get_tpl_version()
    problems: list[str] = []

    seed_tuple = _as_tuple(version)
    if seed_tuple is None:
        problems.append(f"seed pyproject.toml: version {version!r} is not major.minor.patch")
    elif (tpl_tuple := _as_tuple(tpl_version)) and seed_tuple < tpl_tuple:
        problems.append(
            f"seed pyproject.toml: version {version} is below the tpl version {tpl_version}; "
            "the version only moves forward"
        )

    path_seed_log = dir_seed / cctpl.SEED_CHANGELOG
    if not path_seed_log.is_file():
        problems.append(f"seed {cctpl.SEED_CHANGELOG}: missing")
    elif cctpl.find_changelog_heading(path_seed_log.read_text(encoding="utf-8"), version) is None:
        problems.append(
            f"seed {cctpl.SEED_CHANGELOG}: no '{version} (YYYY-MM-DD)' section; "
            "write it with the seed's pywf-oss-changelog-seed-repo skill"
        )

    path_template_log = dir_seed / cctpl.SEED_TEMPLATE_CHANGELOG
    if path_template_log.is_file():
        text = path_template_log.read_text(encoding="utf-8")
        if cctpl.find_changelog_heading(text, version) is not None:
            problems.append(
                f"seed {cctpl.SEED_TEMPLATE_CHANGELOG}: has a section for {version}. It is "
                f"template content; move the section to {cctpl.SEED_CHANGELOG}"
            )
    return problems


def main() -> int:
    problems = collect_problems()
    if problems:
        print("=== Invalid seed version ===")
        for line in problems:
            print(f"  {line}")
        print()
        print(f"FAILED: {len(problems)} problem(s). See 08-versioning-and-release.md.")
        return 1
    print(f"OK: seed version {cctpl.get_seed_version()} is valid and documented.")
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
