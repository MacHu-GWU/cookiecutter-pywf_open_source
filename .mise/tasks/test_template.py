# -*- coding: utf-8 -*-

"""
L2: generate projects from ``tmp/cctpl/template/`` into ``tmp/cctpl/output/``.

- ``output/<project>/``: default values from ``cookiecutter.json``.
- ``output/choices/<variable>-<value>/<project>/``: one generation per extra
  value of each variable in ``CHOICE_COVERAGE``, everything else default.

Exits 1 if any generation fails.
"""

import json

from cookiecutter.main import cookiecutter

import cctpl
import make_template


def main() -> int:
    path_json = cctpl.dir_template / "cookiecutter.json"
    if not path_json.is_file():
        raise cctpl.TaskError(f"{path_json} does not exist. Run 'mise run make-template' first.")
    variables = json.loads(path_json.read_text(encoding="utf-8"))

    cctpl.reset_dir(cctpl.dir_output)
    runs: list[tuple[str, dict, object]] = [("default", {}, cctpl.dir_output)]
    for name in make_template.CHOICE_COVERAGE:
        choices = variables.get(name)
        if not isinstance(choices, list):
            raise cctpl.TaskError(f"CHOICE_COVERAGE names {name!r}, which is not a choice variable")
        for value in choices[1:]:
            runs.append(
                (
                    f"{name}={value}",
                    {name: value},
                    cctpl.dir_output / "choices" / f"{name}-{value}",
                )
            )

    failed = 0
    for label, context, dir_out in runs:
        dir_out.mkdir(parents=True, exist_ok=True)
        try:
            cookiecutter(
                str(cctpl.dir_template),
                no_input=True,
                extra_context=context,
                output_dir=str(dir_out),
            )
            print(f"OK: generated [{label}] -> {dir_out}")
        except Exception as e:  # cookiecutter raises many exception types
            failed += 1
            print(f"FAILED: [{label}] {type(e).__name__}: {e}")

    if failed:
        print(f"FAILED: {failed} of {len(runs)} generation(s).")
        return 1
    print(f"OK: {len(runs)} generation(s). Output: {cctpl.dir_output}")
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
