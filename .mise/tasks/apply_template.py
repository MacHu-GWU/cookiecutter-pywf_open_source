# -*- coding: utf-8 -*-

"""
Apply the generated artifacts to the tpl repo root: replace
``cookiecutter.json`` and the template dir **together** with the ones in
``tmp/cctpl/template/``, and render ``README.rst`` from
``.mise/tasks/cctpl/README.rst.jinja``. ``hooks/`` is source and is never touched.

Run it only after the checks pass; ``mise run sync`` does that.
"""

import json
import shutil

import cctpl
import make_template


def main() -> int:
    src_json = cctpl.dir_template / "cookiecutter.json"
    src_dir = cctpl.dir_template / cctpl.TEMPLATE_DIR_NAME
    if not (src_json.is_file() and src_dir.is_dir()):
        raise cctpl.TaskError(
            f"{cctpl.dir_template} is incomplete. Run 'mise run make-template' first."
        )

    dst_json = cctpl.dir_project_root / "cookiecutter.json"
    dst_dir = cctpl.dir_project_root / cctpl.TEMPLATE_DIR_NAME

    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)
    shutil.copy2(src_json, dst_json)

    seed_repo = make_template.dir_seed.name
    readme = cctpl.render_readme(json.loads(src_json.read_text(encoding="utf-8")), seed_repo)
    (cctpl.dir_project_root / "README.rst").write_text(readme, encoding="utf-8")

    print(f"Applied {dst_json.name}, {dst_dir.name}/ and README.rst from {cctpl.dir_template}")
    print("Review the artifact diff with: git diff --stat -- cookiecutter.json "
          f"'{cctpl.TEMPLATE_DIR_NAME}'")
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
