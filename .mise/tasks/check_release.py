# -*- coding: utf-8 -*-

"""
Check that the shared version is ready to publish. Read-only: it changes no
repo file and writes only ``tmp/cctpl/stage/`` and ``tmp/cctpl/template/``.
It reads the seed's and the tpl repo's remotes with ``git ls-remote``.
publish-template runs the same checks before it pushes anything.

1. The seed version is valid and documented (check-version).
2. The tpl repo carries the same version: ``pyproject.toml``, ``uv.lock``,
   ``cookiecutter.json`` (``_template_version``), ``README.rst``.
3. The artifacts are what the seed generates now (no sync pending).
4. The seed is clean, pushed, and tagged with the version on its HEAD, so
   the template is built from exactly the tagged seed commit.
5. ``release-history.rst`` of the tpl repo has a section for the version
   that starts with the link to the seed's section.
6. The tpl repo has no tag of the version yet: a version is never published
   twice.

Exits 1 on any problem, after reporting all of them.
Spec: 08-versioning-and-release.md.
"""

import sys
import json
import tomllib
import subprocess
from pathlib import Path

import cctpl
import check_version


def _git(dir_repo: Path, *args: str) -> str:
    res = subprocess.run(
        ["git", *args], cwd=dir_repo, check=True, capture_output=True, text=True
    )
    return res.stdout.strip()


def _remote_sha(dir_repo: Path, ref: str) -> str | None:
    """
    The commit ``ref`` points to on ``origin``, with an annotated tag peeled.
    """
    out = _git(dir_repo, "ls-remote", "origin", ref, f"{ref}^{{}}")
    shas = dict(line.split("\t")[::-1] for line in out.splitlines() if line)
    return shas.get(f"{ref}^{{}}") or shas.get(ref)


def _files(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()
    }


def check_tpl_versions(version: str, problems: list[str]) -> None:
    root = cctpl.dir_project_root
    tpl_version = cctpl.get_tpl_version()
    if tpl_version != version:
        problems.append(f"pyproject.toml: version {tpl_version}, seed {version}. Run 'mise run sync'")
    with open(root / "uv.lock", "rb") as f:
        locked = [
            p["version"]
            for p in tomllib.load(f).get("package", [])
            if p.get("source", {}).get("virtual") == "."
        ]
    if locked != [version]:
        problems.append(f"uv.lock: records version {locked}, expected {version}. Run 'mise run sync'")
    data = json.loads((root / "cookiecutter.json").read_text(encoding="utf-8"))
    if data.get("_template_version") != version:
        problems.append(
            f"cookiecutter.json: _template_version {data.get('_template_version')!r}, "
            f"expected {version}. Run 'mise run sync'"
        )
    if f"tags/{version}" not in (root / "README.rst").read_text(encoding="utf-8"):
        problems.append(f"README.rst: does not show version {version}. Run 'mise run sync'")


def check_artifacts(problems: list[str]) -> None:
    res = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "make_template.py")],
        cwd=cctpl.dir_project_root,
        capture_output=True,
        text=True,
    )
    if res.returncode:
        problems.append(f"make-template failed:\n{res.stdout}{res.stderr}")
        return
    if (cctpl.dir_template / "cookiecutter.json").read_bytes() != (
        cctpl.dir_project_root / "cookiecutter.json"
    ).read_bytes():
        problems.append("cookiecutter.json: differs from what the seed generates. Run 'mise run sync'")
    new =_files(cctpl.dir_template / cctpl.TEMPLATE_DIR_NAME)
    old = _files(cctpl.dir_project_root / cctpl.TEMPLATE_DIR_NAME)
    changed = sorted(k for k in new.keys() | old.keys() if new.get(k) != old.get(k))
    if changed:
        listed = ", ".join(changed[:5]) + (" ..." if len(changed) > 5 else "")
        problems.append(
            f"{cctpl.TEMPLATE_DIR_NAME}/: {len(changed)} file(s) differ from what the seed "
            f"generates ({listed}). Run 'mise run sync'"
        )


def check_seed_git(version: str, problems: list[str]) -> None:
    dir_seed = cctpl.get_seed_dir()
    if _git(dir_seed, "status", "--porcelain"):
        problems.append("seed: the working tree has uncommitted changes. Commit and push them")
    head = _git(dir_seed, "rev-parse", "HEAD")
    if _remote_sha(dir_seed, "refs/heads/main") != head:
        problems.append("seed: HEAD is not the remote main. Push the seed")
    tag_sha = _remote_sha(dir_seed, f"refs/tags/{version}")
    if tag_sha is None:
        problems.append(
            f"seed: no tag {version} on the remote. In the seed run 'mise run publish' and "
            "'mise run release' (user's yes each)"
        )
    elif tag_sha != head:
        problems.append(f"seed: tag {version} is on {tag_sha[:7]}, but HEAD is {head[:7]}")


def check_tpl_changelog(version: str, problems: list[str]) -> None:
    dir_seed = cctpl.get_seed_dir()
    seed_heading = cctpl.find_changelog_heading(
        (dir_seed / cctpl.SEED_CHANGELOG).read_text(encoding="utf-8"), version
    )
    if seed_heading is None:
        return  # reported by check-version
    expected = cctpl.tpl_section_header(version, seed_heading)
    lines = (cctpl.dir_project_root / cctpl.TPL_CHANGELOG).read_text(encoding="utf-8").splitlines()
    heading = cctpl.find_changelog_heading("\n".join(lines), version)
    if heading is None:
        problems.append(
            f"{cctpl.TPL_CHANGELOG}: no '{version} (YYYY-MM-DD)' section. Write it with /cctpl-changelog-cn"
        )
        return
    i = lines.index(heading) + 2
    if i >= len(lines) or lines[i] != expected:
        problems.append(
            f"{cctpl.TPL_CHANGELOG}:{i + 1}: the {version} section must start with exactly:\n"
            f"        {expected}"
        )


def collect_problems() -> list[str]:
    version = cctpl.get_seed_version()
    problems = check_version.collect_problems()
    check_tpl_versions(version, problems)
    check_artifacts(problems)
    check_seed_git(version, problems)
    check_tpl_changelog(version, problems)
    if _remote_sha(cctpl.dir_project_root, f"refs/tags/{version}") is not None:
        problems.append(
            f"tpl repo: tag {version} already exists on the remote. A published version is "
            "never overwritten; bump the version in the seed"
        )
    return problems


def main() -> int:
    version = cctpl.get_seed_version()
    problems = collect_problems()
    if problems:
        print(f"=== Version {version} is not ready to publish ===")
        for line in problems:
            print(f"  {line}")
        print()
        print(f"FAILED: {len(problems)} problem(s). See 08-versioning-and-release.md.")
        return 1
    print(f"OK: version {version} is ready to publish.")
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
