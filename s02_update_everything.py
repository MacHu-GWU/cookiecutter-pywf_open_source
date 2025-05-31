# -*- coding: utf-8 -*-

"""
After running the ``s01_run_cookiecutter_maker.py`` script,
manually check generated template directory, then you can use this script
to do git commit, git push, update other branches, and update GitHub release.
"""

import shutil
import subprocess

from home_secret import hs
from manage_github_release import GitHubReleaseManager
from s01_run_cookiecutter_maker import dir_here

dir_tmp_template = dir_here / "tmp" / "{{ cookiecutter.package_name }}-project"
dir_template = dir_here / "{{ cookiecutter.package_name }}-project"

shutil.rmtree(dir_template, ignore_errors=True)
shutil.copytree(dir_tmp_template, dir_template)


def switch_branch(branch_name: str):
    """
    Switch to the specified branch.
    """
    args = ["git", "checkout", branch_name]
    subprocess.run(args, cwd=dir_here, check=True)


def git_push():
    args = ["git", "push"]
    subprocess.run(args, cwd=dir_here, check=True)


def update_and_push_main():
    """
    Commit everything in the main branch and push to the remote repository.
    """
    switch_branch("main")
    args = ["git", "add", "."]
    subprocess.run(args, cwd=dir_here, check=True)

    args = ["git", "commit", "-m", "update template"]
    try:
        subprocess.run(args, cwd=dir_here, check=True)
    except Exception as e:
        print(e)
    git_push()


def merge_and_push_branch(branch_name: str):
    """
    Merge the main branch into the specified branch and push to the remote repository.
    """
    switch_branch(branch_name)
    args = ["git", "merge", "main"]
    subprocess.run(args, cwd=dir_here, check=True)
    args = ["git", "push"]
    subprocess.run(args, cwd=dir_here, check=True)


branch_name_list = [
    "sanhe",
]
update_and_push_main()
for branch_name in branch_name_list:
    merge_and_push_branch(branch_name=branch_name)
switch_branch("main")

manager = GitHubReleaseManager(
    version="0.1.2",
    github_account="MacHu-GWU",
    github_repo_name="cookiecutter-pywf_open_source",
    github_token=hs.v("providers.github.accounts.sh.users.sh.secrets.dev.value"),
)
manager.update_release()
