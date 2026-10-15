# -*- coding: utf-8 -*-

"""
Publish the template. USER ONLY: agents print this command, never run it
(04-safety-rules.md). Run it after Release Prep (/cctpl-release-cn).

1. Commit everything on ``main`` and push.
2. For each ``presets/<name>.json``, regenerate branch ``preset/<name>`` from
   ``main`` with the preset's defaults written into ``cookiecutter.json``, and
   force-push it. Preset branches are derived, never edited by hand.
3. Report remote ``preset/*`` branches that no longer have a preset file;
   they are not deleted automatically.
4. Switch back to ``main``.
5. Create or update the GitHub release on the latest ``main`` commit, named
   after the tpl repo's own version (``pyproject.toml``). Publishing the same
   version again moves its tag and release to the new commit on purpose: a
   publish is also a test, and bumping the version afterwards freezes it.

Spec: 08-versioning-and-release.md.
"""

import os
import json
import subprocess

from pygithub_mate.api import BaseGitHubRepo

import cctpl

root = cctpl.dir_project_root


def git(*args: str, capture: bool = False) -> str:
    res = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=capture, text=True
    )
    return res.stdout if capture else ""


def main() -> int:
    version = cctpl.get_tpl_version()
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

    print(f"Template version: {version}")
    print(f"Presets: {', '.join(presets) or '(none)'}")
    answer = input(
        "This will commit, push main, force-push preset branches, and create a "
        "GitHub release. Type Y to proceed: "
    )
    if answer != "Y":
        print("Aborted.")
        return 0

    # 1. main
    git("add", "-A")
    if git("status", "--porcelain", capture=True).strip():
        git("commit", "-m", f"Release {version}")
    git("push", "origin", "main")

    # 2. preset branches, derived from main
    path_json = root / "cookiecutter.json"
    base = json.loads(path_json.read_text(encoding="utf-8"))
    try:
        for name, overrides in presets.items():
            branch_name = f"{cctpl.PRESET_BRANCH_PREFIX}{name}"
            data = cctpl.apply_preset(base, overrides)
            git("checkout", "-B", branch_name, "main")
            path_json.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
            git("add", "cookiecutter.json")
            # A preset whose overrides all equal main's defaults leaves no
            # diff; its branch is then just main.
            if git("status", "--porcelain", capture=True).strip():
                git("commit", "-m", f"Preset {name} for {version}")
            git("push", "--force", "origin", branch_name)
            print(f"Published {branch_name}")
    finally:
        # 4. back to main, whatever happened above. -f drops a half-written
        # preset cookiecutter.json: preset branches are derived, nothing is lost,
        # and a dirty tree must not block the switch and hide the real error.
        git("checkout", "-f", "main")

    # 3. stale preset branches
    remote = git("ls-remote", "--heads", "origin", f"{cctpl.PRESET_BRANCH_PREFIX}*", capture=True)
    for line in remote.splitlines():
        ref = line.split("refs/heads/", 1)[-1]
        if ref[len(cctpl.PRESET_BRANCH_PREFIX):] not in presets:
            print(f"WARNING: remote branch {ref!r} has no preset file; delete it by hand if unused.")

    # 5. release
    gh_repo = BaseGitHubRepo(
        github_kwargs=dict(login_or_token=token),
        owner_name=cctpl.GITHUB_OWNER,
        repo_name=cctpl.GITHUB_REPO,
    )
    gh_repo.put_release_on_latest_commit_on_default_branch(
        tag_name=version,
        release_name=version,
        release_message=f"Release {version}",
    )
    print(f"Released {version}. Next: /cctpl-verify-cn")
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
