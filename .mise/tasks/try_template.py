# -*- coding: utf-8 -*-

"""
Local trial: try the template the way a human would.

    mise run try-template            # cookiecutter.json defaults
    mise run try-template sanhe      # defaults overridden by presets/sanhe.json

1. Make the template from the seed's current working tree.
2. Render one project with the chosen values into ``tmp/cctpl/try/<label>/``.
3. In that project run its own mise tasks: venv-create, inst, cov, build-doc.

Unlike test-output this goes through mise, so it exercises the generated
mise.toml, its tools, and its task scripts. mise is isolated from the tpl
repo: the project's mise.toml is trusted for this run only
(``MISE_TRUSTED_CONFIG_PATHS``, nothing is written to mise's trust store), and
``MISE_CEILING_PATHS`` stops mise from also loading the tpl repo's mise.toml.

Every step is logged to the console and to ``tmp/cctpl/try/<label>.log``.
Exits 1 at the first failing step. Spec: 08-verification.md, "Local Trial".
"""

import os
import sys
from pathlib import Path

from cookiecutter.main import cookiecutter

import cctpl

PROJECT_TASKS = ["venv-create", "inst", "cov", "build-doc"]


def main() -> int:
    preset = sys.argv[1] if len(sys.argv) > 1 else None
    presets = cctpl.load_presets()
    if preset and preset not in presets:
        raise cctpl.TaskError(
            f"unknown preset {preset!r}; available: {', '.join(presets) or '(none)'}"
        )
    label = preset or "default"
    overrides = presets.get(preset, {}) if preset else {}

    log = cctpl.StepLog("try", 2 + len(PROJECT_TASKS), cctpl.dir_try / f"{label}.log")

    # 1. template from the seed
    log.step("make the template from the seed (CCTPL_SEED_DIR)")
    code, _ = log.run(
        [sys.executable, str(Path(__file__).parent / "make_template.py")],
        cwd=cctpl.dir_project_root,
    )
    if code:
        log.write("FAILED: make-template")
        return 1

    # 2. render
    log.step(f"render a project with {label} values")
    dir_label = cctpl.dir_try / label
    cctpl.reset_dir(dir_label)
    log.write(f"    overrides: {', '.join(overrides) or '(none)'}")
    dir_project = Path(
        cookiecutter(
            str(cctpl.dir_template),
            no_input=True,
            extra_context=overrides,
            output_dir=str(dir_label),
        )
    )
    log.write(f"    -> {dir_project}")

    # 3. the project's own mise tasks
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("MISE_") and k not in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT")
    }
    env["MISE_TRUSTED_CONFIG_PATHS"] = str(dir_project)
    env["MISE_CEILING_PATHS"] = str(dir_project.parent)
    results = []
    for task in PROJECT_TASKS:
        log.step(f"mise run {task}")
        code, seconds = log.run(["mise", "run", task], cwd=dir_project, env=env)
        results.append((task, code, seconds))
        if code:
            break

    log.write("")
    log.write(f"=== Try result ({label})")
    for task, code, seconds in results:
        log.write(f"{'PASS' if code == 0 else 'FAIL'}  mise run {task}  ({seconds:.1f}s)")
    for task in PROJECT_TASKS[len(results):]:
        log.write(f"SKIP  mise run {task}")
    log.write(f"Project: {dir_project}")
    log.write(f"Log:     {log.path_log}")
    log.write("To continue by hand: cd into the project, run 'mise trust' once, then any mise task.")
    return 0 if all(code == 0 for _, code, _ in results) and len(results) == len(PROJECT_TASKS) else 1


if __name__ == "__main__":
    cctpl.run_task(main)
