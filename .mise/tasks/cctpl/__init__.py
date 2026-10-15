# -*- coding: utf-8 -*-

"""
Shared helpers for the cctpl mise tasks.

The contract these tasks follow lives in
``.claude/skills/cctpl-base-cn/references/04-mise-task-contract.md``.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

dir_project_root = Path(__file__).absolute().parent.parent.parent.parent

# --- workspace (02-repo-layout.md, "workspace 规则")
dir_tmp = dir_project_root / "tmp"
dir_cctpl = dir_tmp / "cctpl"
dir_stage = dir_cctpl / "stage"
dir_template = dir_cctpl / "template"
dir_output = dir_cctpl / "output"
dir_roundtrip = dir_cctpl / "roundtrip"
dir_verify = dir_cctpl / "verify"

TEMPLATE_DIR_NAME = "{{ cookiecutter.package_name }}-project"


class TaskError(Exception):
    """A task precondition or check failed; the message tells the user why."""


def get_seed_dir() -> Path:
    """
    Return the seed repo directory from ``CCTPL_SEED_DIR``.
    """
    value = os.environ.get("CCTPL_SEED_DIR")
    if not value:
        raise TaskError(
            "CCTPL_SEED_DIR is not set. Define it in the [env] section of mise.toml "
            "and run the task through 'mise run'."
        )
    dir_seed = Path(value).expanduser()
    if not dir_seed.is_dir():
        raise TaskError(f"CCTPL_SEED_DIR does not point to a directory: {dir_seed}")
    return dir_seed


def reset_dir(path: Path) -> None:
    """
    Delete ``path`` and recreate it empty. Refuses anything outside ``tmp/cctpl/``.
    """
    if dir_cctpl not in path.parents:
        raise TaskError(f"refusing to reset a directory outside {dir_cctpl}: {path}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def list_git_visible_files(dir_repo: Path) -> list[str]:
    """
    List the files git sees in ``dir_repo``: tracked files plus untracked files
    that are not ignored. Tracked files deleted from the working tree are skipped.
    """
    res = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=dir_repo,
        check=True,
        capture_output=True,
    )
    paths = [p for p in res.stdout.decode("utf-8").split("\0") if p]
    return sorted(p for p in set(paths) if (dir_repo / p).is_file())


def stage_git_visible_files(dir_repo: Path, dir_dst: Path) -> int:
    """
    Copy the git-visible files of ``dir_repo`` into ``dir_dst``, keeping relative
    paths and file modes. Return the number of files copied.
    """
    files = list_git_visible_files(dir_repo)
    for rel in files:
        src = dir_repo / rel
        dst = dir_dst / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return len(files)


def iter_text_files(dir_root: Path):
    """
    Yield ``(relative path, text)`` for every UTF-8 text file under ``dir_root``.
    Binary files are skipped.
    """
    for path in sorted(dir_root.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, ValueError):
            continue
        yield str(path.relative_to(dir_root)), text


def require_dir(path: Path, hint: str) -> None:
    """
    Fail with a hint naming the task to run first when ``path`` is missing.
    """
    if not path.is_dir():
        raise TaskError(f"{path} does not exist. Run '{hint}' first.")


def run_task(main) -> None:
    """
    Run a task's ``main()`` and exit with its return code; a ``TaskError``
    prints its message and exits 1.
    """
    try:
        sys.exit(main())
    except TaskError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
