# -*- coding: utf-8 -*-

"""
Shared helpers for the cctpl mise tasks.

The contract these tasks follow lives in
``.claude/skills/cctpl-base-cn/references/07-mise-task-contract.md``.
"""

import os
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

TEMPLATE_DIR_NAME = "{{ cookiecutter.package_name }}-project"

# --- release (08-versioning-and-release.md)
GITHUB_OWNER = "MacHu-GWU"
GITHUB_REPO = "cookiecutter-pywf_open_source"
dir_presets = dir_project_root / "presets"
PRESET_BRANCH_PREFIX = "preset/"


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


def get_tpl_version() -> str:
    """
    The tpl repo's own version, from its ``pyproject.toml`` (never the seed's).
    """
    with open(dir_project_root / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


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
    Install a generated project with uv and run its tests with pytest,
    bypassing mise (06-verification.md, "Secrets"). Return True on success.
    """
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT")
    }
    steps = [
        ["uv", "venv", "--allow-existing", "--python", python],
        ["uv", "sync", "--all-extras"],
        [".venv/bin/pytest", "tests", "-q"],
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
