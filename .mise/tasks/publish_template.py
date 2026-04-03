# -*- coding: utf-8 -*-

"""
Publish the cookiecutter template to GitHub.

This script is meant to run AFTER ``mise run make-template`` and manual review.

Business logic:

1. Copy the generated template from ``tmp/`` to the project root, replacing the
   old ``{{ cookiecutter.package_name }}-project/`` directory.
2. Commit all changes on the ``main`` branch and push to the remote.
3. (Optional) For each extra branch (e.g. personalized variants like ``sanhe``),
   merge ``main`` into that branch and push. These branches carry customized
   ``cookiecutter.json`` defaults for specific users but share the same template.
4. Switch back to ``main``.
5. Create (or update) a GitHub release + tag on the latest commit of the default
   branch, using the seed project's version as the tag/release name.
"""

import os
import shutil
import subprocess
import importlib.util
from pathlib import Path

from pygithub_mate.api import BaseGitHubRepo

from cookiecutter_pywf_open_source.paths import path_enum
from make_template import SeedValues


# ---------------------------------------------------------------------------
# Import shared values from make_template.py
# ---------------------------------------------------------------------------
# We import from make_template.py to reuse:
# - `dir_here`: Project root directory path
# - `version_to_replace`: Seed project version (from seed's pyproject.toml)
#
# Why: This template's version is synchronized with the seed project's version.
# When we create a GitHub release, the tag/release name is the seed version.
version_to_replace = SeedValues.version

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Extra branches that carry personalized cookiecutter.json defaults.
# Each branch will be updated by merging main into it.
extra_branches: list[str] = [
    # "sanhe",
]

# ---------------------------------------------------------------------------
# Step 1 — Copy generated template to the project root
# ---------------------------------------------------------------------------
dir_project_root = path_enum.dir_project_root
dir_tmp_template = dir_project_root / "tmp" / "{{ cookiecutter.package_name }}-project"
dir_template = dir_project_root / "{{ cookiecutter.package_name }}-project"

shutil.rmtree(dir_template, ignore_errors=True)
shutil.copytree(dir_tmp_template, dir_template)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------
def switch_branch(branch_name: str):
    subprocess.run(["git", "checkout", branch_name], cwd=dir_project_root, check=True)


def git_push():
    subprocess.run(["git", "push"], cwd=dir_project_root, check=True)


def update_and_push_main():
    """Commit everything on main and push."""
    switch_branch("main")
    subprocess.run(["git", "add", "."], cwd=dir_project_root, check=True)
    try:
        subprocess.run(
            ["git", "commit", "-m", "update template"],
            cwd=dir_project_root,
            check=True,
        )
    except Exception as e:
        print(e)
    git_push()


def merge_and_push_branch(branch_name: str):
    """Merge main into the given branch and push."""
    switch_branch(branch_name)
    subprocess.run(["git", "merge", "main"], cwd=dir_project_root, check=True)
    subprocess.run(["git", "push"], cwd=dir_project_root, check=True)


# ---------------------------------------------------------------------------
# Step 2 — Commit and push main
# ---------------------------------------------------------------------------
update_and_push_main()

# ---------------------------------------------------------------------------
# Step 3 — Merge main into extra branches (if any)
# ---------------------------------------------------------------------------
for branch_name in extra_branches:
    merge_and_push_branch(branch_name=branch_name)
switch_branch("main")

# ---------------------------------------------------------------------------
# Step 4 — Create / update GitHub release
# ---------------------------------------------------------------------------
gh_repo = BaseGitHubRepo(
    github_kwargs=dict(login_or_token=os.environ["GITHUB_TOKEN"]),
    owner_name="MacHu-GWU",
    repo_name="cookiecutter-pywf_open_source",
)
gh_repo.put_release_on_latest_commit_on_default_branch(
    tag_name=version_to_replace,
    release_name=version_to_replace,
    release_message=f"Release {version_to_replace}",
)
