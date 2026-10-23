# -*- coding: utf-8 -*-

"""
Regenerate the preset branches from the pushed ``main``. USER ONLY: agents
print this command, never run it (04-safety-rules.md).

1. Require ``main`` checked out, a clean tree, and ``main`` pushed: preset
   branches are derived from the published ``main``, never from local work.
2. For each ``presets/<name>.json``, reset branch ``preset/<name>`` to
   ``main``, write the preset's defaults into ``cookiecutter.json``, commit,
   and force-push. Everything but ``cookiecutter.json`` equals ``main``.
3. Switch back to ``main``, whatever happened.
4. Report remote ``preset/*`` branches that no longer have a preset file;
   they are not deleted automatically.

publish-template runs this as its last step. Run it alone to retry a failed
preset push, or after a change to ``presets/*.json`` only: preset branches
are derived and carry no tag, so a rerun is always safe and needs no new
version.

Spec: 02-repo-layout.md, "Preset Branches".
"""

import json
import subprocess

import cctpl

root = cctpl.dir_project_root


def git(*args: str, capture: bool = False) -> str:
    res = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=capture, text=True
    )
    return res.stdout if capture else ""


def check_main() -> None:
    """
    Fail unless ``main`` is checked out, clean, and equal to the remote ``main``.
    """
    branch = git("rev-parse", "--abbrev-ref", "HEAD", capture=True).strip()
    if branch != "main":
        raise cctpl.TaskError(f"run from 'main', current branch is {branch!r}")
    if git("status", "--porcelain", capture=True).strip():
        raise cctpl.TaskError("the working tree has uncommitted changes; commit and push main first")
    head = git("rev-parse", "HEAD", capture=True).strip()
    remote = git("ls-remote", "origin", "refs/heads/main", capture=True).split("\t")[0]
    if head != remote:
        raise cctpl.TaskError("local main is not the remote main; push main first")


def publish_presets() -> None:
    """
    Regenerate and force-push every preset branch, then report stale ones.
    Call ``check_main()`` first.
    """
    version = cctpl.get_tpl_version()
    presets = cctpl.load_presets()
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
        # Back to main, whatever happened above. -f drops a half-written
        # preset cookiecutter.json: preset branches are derived, nothing is lost,
        # and a dirty tree must not block the switch and hide the real error.
        git("checkout", "-f", "main")

    remote = git("ls-remote", "--heads", "origin", f"{cctpl.PRESET_BRANCH_PREFIX}*", capture=True)
    for line in remote.splitlines():
        ref = line.split("refs/heads/", 1)[-1]
        if ref[len(cctpl.PRESET_BRANCH_PREFIX):] not in presets:
            print(f"WARNING: remote branch {ref!r} has no preset file; delete it by hand if unused.")


def main() -> int:
    check_main()
    presets = cctpl.load_presets()
    print(f"Presets: {', '.join(presets) or '(none)'}")
    answer = input("This will force-push the preset branches. Type Y to proceed: ")
    if answer != "Y":
        print("Aborted.")
        return 0
    publish_presets()
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
