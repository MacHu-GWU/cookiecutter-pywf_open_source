# -*- coding: utf-8 -*-

"""
L5: verify the template as published on GitHub. Read-only on GitHub.

For each branch (default: ``main`` plus ``preset/<name>`` for every
``presets/<name>.json``; or the branches given as arguments):

1. Generate a project from ``gh:<owner>/<repo> --checkout <branch> --no-input``
   into ``tmp/cctpl/verify/<branch>/remote/``, using a private clone cache so
   no stale clone in ``~/.cookiecutters`` is reused.
2. Generate the same project from the local ``tmp/cctpl/template/`` with the
   branch's defaults into ``.../local/`` and compare: they must be identical.
   This catches files lost or stale in publishing, and wrong preset values.
3. Install the remote project and run its tests (06-verification.md, L5).

Exits 1 if any branch fails. Spec: 06-verification.md, "L5: After Publish".
"""

import os
import sys
import json
from pathlib import Path

from cookiecutter.main import cookiecutter

import cctpl


def _files(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and ".venv" not in p.relative_to(root).parts
    }


def _compare(dir_local: Path, dir_remote: Path) -> list[str]:
    local, remote = _files(dir_local), _files(dir_remote)
    problems = [f"{rel}: missing from published template" for rel in sorted(local.keys() - remote.keys())]
    problems += [f"{rel}: only in published template" for rel in sorted(remote.keys() - local.keys())]
    problems += [
        f"{rel}: content differs"
        for rel in sorted(local.keys() & remote.keys())
        if local[rel] != remote[rel]
    ]
    return problems


def verify(branch: str, overrides: dict, base_json: dict, config_file: Path) -> list[str]:
    dir_branch = cctpl.dir_verify / branch.replace("/", "--")
    dir_remote = dir_branch / "remote"
    dir_local = dir_branch / "local"
    dir_remote.mkdir(parents=True)
    dir_local.mkdir(parents=True)

    print(f"=== {branch}", flush=True)
    try:
        out_remote = Path(
            cookiecutter(
                f"gh:{cctpl.GITHUB_OWNER}/{cctpl.GITHUB_REPO}",
                checkout=branch,
                no_input=True,
                output_dir=str(dir_remote),
                config_file=str(config_file),
            )
        )
    except Exception as e:  # cookiecutter / git raise many exception types
        return [f"fetch failed: {type(e).__name__}: {e}"]

    out_local = Path(
        cookiecutter(
            str(cctpl.dir_template),
            no_input=True,
            extra_context=overrides,
            output_dir=str(dir_local),
        )
    )
    problems = [f"compare: {p}" for p in _compare(out_local, out_remote)]

    python = cctpl.apply_preset(base_json, overrides)["dev_python_version"]
    if not cctpl.run_project_tests(out_remote, python):
        problems.append("tests: install or tests failed (see output above)")
    return problems


def main() -> int:
    path_json = cctpl.dir_template / "cookiecutter.json"
    if not path_json.is_file():
        raise cctpl.TaskError(f"{path_json} does not exist. Run 'mise run make-template' first.")
    base_json = json.loads(path_json.read_text(encoding="utf-8"))

    presets = cctpl.load_presets()
    branches = sys.argv[1:] or ["main"] + [f"{cctpl.PRESET_BRANCH_PREFIX}{n}" for n in presets]

    cctpl.reset_dir(cctpl.dir_verify)
    dir_clones = cctpl.dir_verify / "_clones"
    config_file = cctpl.dir_verify / "cookiecutter-config.yaml"
    config_file.write_text(
        f'cookiecutters_dir: "{dir_clones}"\nreplay_dir: "{cctpl.dir_verify / "_replay"}"\n',
        encoding="utf-8",
    )

    results: dict[str, list[str]] = {}
    for branch in branches:
        name = branch.removeprefix(cctpl.PRESET_BRANCH_PREFIX)
        if branch.startswith(cctpl.PRESET_BRANCH_PREFIX) and name not in presets:
            results[branch] = [f"no presets/{name}.json for this branch"]
            continue
        overrides = presets.get(name, {}) if branch != "main" else {}
        results[branch] = verify(branch, overrides, base_json, config_file)

    print("\n=== Verify result")
    for branch, problems in results.items():
        print(f"{'PASS' if not problems else 'FAIL'}  {branch}")
        for p in problems[:20]:
            print(f"      {p}")
        if len(problems) > 20:
            print(f"      ... {len(problems) - 20} more")
    return 1 if any(results.values()) else 0


if __name__ == "__main__":
    os.environ.pop("VIRTUAL_ENV", None)
    cctpl.run_task(main)
