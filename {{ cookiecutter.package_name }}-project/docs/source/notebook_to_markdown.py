# -*- coding: utf-8 -*-

import subprocess
from {{ cookiecutter.package_name }}.paths import dir_docs_source, dir_venv_bin

bin_jupyter = dir_venv_bin / "jupyter"

for path_notebook in dir_docs_source.glob("**/*.ipynb"):
    if ".ipynb_checkpoints" in str(path_notebook):
        continue
    path_markdown = path_notebook.parent / f"{path_notebook.stem}.md"
    args = [
        f"{bin_jupyter}",
        "nbconvert",
        "--to",
        "markdown",
        str(path_notebook),
        "--output",
        str(path_markdown),
    ]
    cmd = " ".join(args)
    print(f"run command: {cmd}")
    subprocess.run(args, check=True)