# -*- coding: utf-8 -*-

"""
Shared helpers for the cctpl mise tasks.

The contract these tasks follow lives in
``.claude/skills/cctpl-base-cn/references/07-mise-task-contract.md``.
"""

import os
import re
import sys
import json
import shutil
import time
import tomllib
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
dir_try = dir_cctpl / "try"

# Pair-specific facts live in pair.py; re-exported here for the task scripts.
from .pair import (
    GITHUB_OWNER,
    GITHUB_REPO,
    TEMPLATE_DIR_NAME,
    PYTHON_VERSION_VARIABLE,
    INSTALL_COMMAND,
    TEST_COMMAND,
    PROJECT_TASKS,
)

# --- release (08-versioning-and-release.md)
dir_presets = dir_project_root / "presets"
PRESET_BRANCH_PREFIX = "preset/"

# --- changelogs (08-versioning-and-release.md)
# The tpl repo's changelog, and the seed's own one. The seed's
# release-history.rst is template content, never a changelog of the seed.
TPL_CHANGELOG = "release-history.rst"
SEED_CHANGELOG = "release-history-seed-repo.rst"
SEED_TEMPLATE_CHANGELOG = "release-history.rst"


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


def get_seed_repo_name() -> str:
    """
    The seed's GitHub repo name, under the same owner as the tpl repo: the
    directory name of ``CCTPL_SEED_DIR``, its only source.
    """
    return get_seed_dir().name


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


def get_seed_version() -> str:
    """
    The version shared by the seed and the tpl repo. Its only source is
    ``[project].version`` in the seed's ``pyproject.toml``
    (08-versioning-and-release.md).
    """
    with open(get_seed_dir() / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


def get_tpl_version() -> str:
    """
    The version in the tpl repo's ``pyproject.toml``: a copy of the seed's,
    written by apply-template (``set_tpl_version``).
    """
    with open(dir_project_root / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


_RE_PYPROJECT_VERSION = re.compile(r'^version = "[^"]*"$', re.MULTILINE)


def set_tpl_version(version: str) -> bool:
    """
    Write ``version`` into the tpl repo's ``pyproject.toml``, then refresh
    ``uv.lock``, which records it too. Return True when it changed.
    """
    if get_tpl_version() == version:
        return False
    path = dir_project_root / "pyproject.toml"
    text, n = _RE_PYPROJECT_VERSION.subn(
        f'version = "{version}"', path.read_text(encoding="utf-8"), count=1
    )
    if n != 1:
        raise TaskError(f"no 'version = \"...\"' line in {path}")
    path.write_text(text, encoding="utf-8")
    subprocess.run(["uv", "lock"], cwd=dir_project_root, check=True)
    return True


def find_changelog_heading(text: str, version: str) -> str | None:
    """
    Return the section heading ``<version> (YYYY-MM-DD)`` of ``version`` in a
    changelog, or None when the changelog has no section for it.
    """
    pattern = rf"^({re.escape(version)} \(\d{{4}}-\d{{2}}-\d{{2}}\))\n~+$"
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else None


def github_anchor(heading: str) -> str:
    """
    The anchor GitHub gives a heading when it renders a file:
    ``3.0.0 (2026-10-23)`` becomes ``300-2026-10-23``.
    """
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def seed_changelog_url(version: str, heading: str) -> str:
    """
    The link to the seed's changelog section of ``version``, at the seed's
    git tag of that version.
    """
    return (
        f"https://github.com/{GITHUB_OWNER}/{get_seed_repo_name()}/blob/{version}/"
        f"{SEED_CHANGELOG}#{github_anchor(heading)}"
    )


def tpl_section_header(version: str, seed_heading: str) -> str:
    """
    The line every section of the tpl changelog starts with, right below its
    ``~`` underline: the link to the seed's section of the same version. The
    seed's tag of that version is the record of which seed commit the
    template was built from, so no commit is written here.
    """
    url = seed_changelog_url(version, seed_heading)
    return f"Seed repo changes: `{seed_heading} <{url}>`__"


def load_presets() -> dict[str, dict]:
    """
    Read every ``presets/<name>.json``, keyed by preset name.
    """
    if not dir_presets.is_dir():
        return {}
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(dir_presets.glob("*.json"))
    }


def apply_preset(cookiecutter_json: dict, overrides: dict) -> dict:
    """
    Return a copy of ``cookiecutter_json`` with the preset's defaults applied.
    For a choice variable the chosen value moves to the front of the list,
    which cookiecutter treats as the default; the rest keep their order.
    """
    data = json.loads(json.dumps(cookiecutter_json))
    for key, value in overrides.items():
        if key not in data or key.startswith("_"):
            raise TaskError(f"preset overrides unknown variable {key!r}")
        if isinstance(data[key], list):
            if value not in data[key]:
                raise TaskError(f"preset value {value!r} is not a choice of {key!r}")
            data[key] = [value] + [v for v in data[key] if v != value]
        else:
            data[key] = value
    return data


def run_project_tests(dir_project: Path, python: str) -> bool:
    """
    Create a uv virtual environment for a generated project, then run
    ``INSTALL_COMMAND`` and ``TEST_COMMAND`` from ``pair.py``, bypassing mise (06-verification.md, "Secrets"). Return True on success.
    """
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT")
    }
    steps = [
        ["uv", "venv", "--allow-existing", "--python", python],
        INSTALL_COMMAND,
        TEST_COMMAND,
    ]
    for cmd in steps:
        print(f"$ {' '.join(cmd)}  (in {dir_project})", flush=True)
        res = subprocess.run(cmd, cwd=dir_project, env=env)
        if res.returncode != 0:
            print(f"FAILED: '{' '.join(cmd)}' exited {res.returncode}")
            return False
    return True


class StepLog:
    """
    Key progress lines for humans and agents: every line is printed and also
    appended to a log file, prefixed with ``[<task> i/n]`` and a timestamp.
    """

    def __init__(self, task: str, total: int, path_log: Path):
        self.task = task
        self.total = total
        self.index = 0
        self.path_log = path_log
        path_log.parent.mkdir(parents=True, exist_ok=True)
        path_log.write_text("", encoding="utf-8")

    def write(self, line: str) -> None:
        print(line, flush=True)
        with self.path_log.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def step(self, title: str) -> None:
        self.index += 1
        stamp = time.strftime("%H:%M:%S")
        self.write(f"[{self.task} {self.index}/{self.total}] {stamp} {title}")

    def run(self, cmd: list[str], cwd: Path, env: dict | None = None) -> tuple[int, float]:
        """
        Run ``cmd``, streaming its output into the log. Return (exit code, seconds).
        """
        self.write(f"    $ {' '.join(cmd)}")
        self.write(f"    cwd: {cwd}")
        start = time.monotonic()
        proc = subprocess.Popen(
            cmd, cwd=cwd, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        for line in proc.stdout:
            self.write(f"    | {line.rstrip()}")
        code = proc.wait()
        seconds = time.monotonic() - start
        self.write(f"    -> exit {code} in {seconds:.1f}s")
        return code, seconds


def format_prompts(cookiecutter_json: dict) -> str:
    """
    Render the interactive prompts cookiecutter shows for ``cookiecutter_json``,
    answered with the defaults, as an indented RST code block body.
    """
    prompts = cookiecutter_json.get("__prompts__", {})
    names = [k for k in cookiecutter_json if not k.startswith("_")]
    lines = []
    for i, name in enumerate(names, 1):
        value = cookiecutter_json[name]
        text = prompts.get(name, name)
        if isinstance(value, list):
            lines.append(f"    [{i}/{len(names)}] {text}")
            for j, choice in enumerate(value, 1):
                lines.append(f"      {j} - {choice}")
            options = "/".join(str(j) for j in range(1, len(value) + 1))
            lines.append(f"      Choose from [{options}] (1): 1")
        else:
            lines.append(f"    [{i}/{len(names)}] {text} ({value}): {value}")
    return "\n".join(lines)


def render_readme(cookiecutter_json: dict, seed_repo: str) -> str:
    """
    Render README.rst from ``README.rst.jinja``. README.rst is an artifact:
    every fact in it comes from the repo, never typed by hand.
    """
    import jinja2

    with open(dir_project_root / "pyproject.toml", "rb") as f:
        dependencies = tomllib.load(f)["project"]["dependencies"]
    requirement = next(d for d in dependencies if d.startswith("cookiecutter>") or d.startswith("cookiecutter="))
    env = jinja2.Environment(keep_trailing_newline=True, undefined=jinja2.StrictUndefined)
    template = env.from_string(
        (Path(__file__).parent / "README.rst.jinja").read_text(encoding="utf-8")
    )
    return template.render(
        owner=GITHUB_OWNER,
        tpl_repo=GITHUB_REPO,
        seed_repo=seed_repo,
        version=get_tpl_version(),
        cookiecutter_requirement=requirement,
        prompts=format_prompts(cookiecutter_json),
    )
