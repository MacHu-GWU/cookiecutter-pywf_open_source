# -*- coding: utf-8 -*-

"""
Publish the template. USER ONLY: agents print this command, never run it
(04-safety-rules.md). Run it after Release Prep (/cctpl-release-cn).

0. Run the check-release checks; any problem stops here, before anything is
   pushed. Among them: the tpl repo has no tag of the version yet. The
   version is the seed's (``cctpl.get_seed_version``), which sync has
   already copied into this repo.
1. Commit everything on ``main`` and push.
2. Create the tag and the GitHub release of the version on the pushed
   ``main`` commit, in one API call. An existing tag is never moved: a bad
   release is fixed by a new version.
3. Regenerate the preset branches from the pushed ``main``
   (``publish_presets.py``, also its own task ``mise run publish-presets``).
   They carry no tag, so a failed preset push is retried with that task
   alone.

The seed is not touched: its tag comes from its own ``mise run release``.

Spec: 08-versioning-and-release.md.
"""

import os
import subprocess

from pygithub_mate.api import BaseGitHubRepo

import cctpl
import check_release
import publish_presets

root = cctpl.dir_project_root


def git(*args: str, capture: bool = False) -> str:
    res = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=capture, text=True
    )
    return res.stdout if capture else ""


def main() -> int:
    version = cctpl.get_seed_version()
    presets = cctpl.load_presets()

    branch = git("rev-parse", "--abbrev-ref", "HEAD", capture=True).strip()
    if branch != "main":
        raise cctpl.TaskError(f"publish from 'main', current branch is {branch!r}")
    # mise.toml reads the token with '|| true', so a missing secret arrives as
    # an empty string; fail now, before anything is pushed.
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise cctpl.TaskError(
            "GITHUB_TOKEN is empty: the secret in mise.toml [env] could not be read. "
            "The GitHub release step needs it."
        )

    # 0. the same checks as 'mise run check-release'
    problems = check_release.collect_problems()
    if problems:
        print(f"=== Version {version} is not ready to publish ===")
        for line in problems:
            print(f"  {line}")
        raise cctpl.TaskError(f"{len(problems)} problem(s); nothing was pushed")

    print(f"Template version: {version}")
    print(f"Presets: {', '.join(presets) or '(none)'}")
    answer = input(
        f"This will commit, push main, create the tag and GitHub release {version}, "
        "and force-push the preset branches. Type Y to proceed: "
    )
    if answer != "Y":
        print("Aborted.")
        return 0

    # 1. main
    git("add", "-A")
    if git("status", "--porcelain", capture=True).strip():
        git("commit", "-m", f"Release {version}")
    git("push", "origin", "main")
    sha = git("rev-parse", "HEAD", capture=True).strip()

    # 2. tag and release, created together on the pushed main commit; GitHub
    # refuses if the tag already exists, so nothing is ever overwritten.
    heading = cctpl.find_changelog_heading(
        (root / cctpl.TPL_CHANGELOG).read_text(encoding="utf-8"), version
    )
    changelog_url = (
        f"https://github.com/{cctpl.GITHUB_OWNER}/{cctpl.GITHUB_REPO}/blob/{version}/"
        f"{cctpl.TPL_CHANGELOG}#{cctpl.github_anchor(heading)}"
    )
    gh_repo = BaseGitHubRepo(
        github_kwargs=dict(login_or_token=token),
        owner_name=cctpl.GITHUB_OWNER,
        repo_name=cctpl.GITHUB_REPO,
    )
    gh_repo.create_release(
        tag_name=version,
        release_name=version,
        release_message=f"Release {version}. Changes: {changelog_url}",
        create_git_release_kwargs=dict(target_commitish=sha),
    )
    print(f"Released {version}")

    # 3. preset branches, derived from the pushed main
    publish_presets.check_main()
    publish_presets.publish_presets()
    print("Next: /cctpl-verify-cn")
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
