# -*- coding: utf-8 -*-

"""
Check every ``presets/<name>.json`` against the freshly generated
``tmp/cctpl/template/cookiecutter.json``: each overridden variable must exist,
and a choice variable's override must be one of its choices. Exits 1 on any
problem.

Preset format: 02-repo-layout.md, "Preset Branches".
"""

import json

import cctpl

dir_presets = cctpl.dir_project_root / "presets"


def main() -> int:
    path_json = cctpl.dir_template / "cookiecutter.json"
    if not path_json.is_file():
        raise cctpl.TaskError(f"{path_json} does not exist. Run 'mise run make-template' first.")
    variables = {
        k: v
        for k, v in json.loads(path_json.read_text(encoding="utf-8")).items()
        if not k.startswith("_")
    }

    paths = sorted(dir_presets.glob("*.json")) if dir_presets.is_dir() else []
    if not paths:
        print("OK: no presets defined.")
        return 0

    problems: list[str] = []
    for path in paths:
        try:
            overrides = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"{path.name}: invalid JSON: {e}")
            continue
        if not isinstance(overrides, dict):
            problems.append(f"{path.name}: must be a JSON object")
            continue
        for key, value in overrides.items():
            if key not in variables:
                problems.append(f"{path.name}: [{key}] is not a variable in cookiecutter.json")
            elif isinstance(variables[key], list):
                if value not in variables[key]:
                    problems.append(
                        f"{path.name}: [{key}] {value!r} is not one of {variables[key]}"
                    )
            elif not isinstance(value, str):
                problems.append(f"{path.name}: [{key}] must be a string")

    if problems:
        print("=== Invalid presets ===")
        for line in problems:
            print(f"  {line}")
        print()
        print(f"FAILED: {len(problems)} problem(s).")
        return 1
    print(f"OK: {len(paths)} preset(s) valid: {', '.join(p.stem for p in paths)}.")
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
