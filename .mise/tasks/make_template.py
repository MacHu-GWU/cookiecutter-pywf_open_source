# -*- coding: utf-8 -*-

"""
Convert the seed repo into a cookiecutter template.

Input: the git-visible files of the seed repo (``CCTPL_SEED_DIR``).
Output: ``tmp/cctpl/template/``, a complete cookiecutter template root.

Rules: ``.claude/skills/cctpl-base-cn/references/03-parameterization.md``.
"""

import sys
import json
import tomllib

from cookiecutter_maker.api import Parameter, Maker

import cctpl

try:
    dir_seed = cctpl.get_seed_dir()
except cctpl.TaskError as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

with open(dir_seed / "pyproject.toml", "rb") as f:
    _pyproject = tomllib.load(f)
with open(dir_seed / "mise.toml", "rb") as f:
    _mise_config = tomllib.load(f)


class SeedValues:
    """Concrete values in the seed repo that become cookiecutter variables."""

    # --- identity
    package_name = "cookiecutter_pywf_open_source_demo"
    package_name_slug = "cookiecutter-pywf-open-source-demo"
    github_username = "MacHu-GWU"

    # --- license
    license = "MIT"

    # --- author
    author = "Sanhe Hu"
    author_email = "husanhe@gmail.com"

    # --- versioning (read from the seed)
    version = _pyproject["project"]["version"]
    dev_python_version = _mise_config["tools"]["python"]

    # --- secret token fields
    github_token_field = "github.accounts.sh.users.sh.secrets.dev.value"
    codecov_token_field = "codecov_io.accounts.sh.users.sh.secrets.dev.value"
    readthedocs_token_field = "readthedocs.accounts.sh.users.sh.secrets.dev.value"
    pypi_token_field = "pypi.accounts.sh.token"


_parts = SeedValues.version.split(".")
assert len(_parts) == 3 and all(v.isdigit() for v in _parts), (
    f"Invalid version: {SeedValues.version}"
)

_HOME_SECRET_HELP = (
    "Read https://github.com/MacHu-GWU/home_secret_toml-project to learn how to "
    "set up your tokens using home_secret.toml"
)

PARAMETERS = [
    Parameter(
        selector=[SeedValues.package_name],
        name="package_name",
        default="your_package_name",
        prompt="Your Python package name, in snake case (e.g. my_package)",
    ),
    Parameter(
        selector=[SeedValues.package_name_slug],
        name="package_name_slug",
        custom_placeholder="{{ cookiecutter.package_name | slugify }}",
        in_cookiecutter_json=False,
    ),
    # The seed also links to the maintainer's own projects (plugin marketplace,
    # home_secret_toml, docfly). Those links must stay literal, so the files that
    # only mention them are excluded from this parameter.
    Parameter(
        selector=[SeedValues.github_username],
        name="github_username",
        default="your_github_username",
        prompt="Your GitHub username, the owner of the new repo",
        exclude=[
            ".claude/settings.local.json.example",
            ".claude/skills/pywf-oss-base/references/01-secrets.md",
            ".claude/skills/pywf-oss-base/references/14-docfly.md",
        ],
    ),
    # Generic value: only the project license field in pyproject.toml.
    Parameter(
        selector=[f'license = "{SeedValues.license}"', SeedValues.license],
        name="license",
        choice=["MIT", "AGPL-3.0-or-later", "Proprietary"],
        prompt="Pick an open source license, see https://choosealicense.com/ for details",
        include=["pyproject.toml"],
    ),
    Parameter(
        selector=[SeedValues.author],
        name="author",
        default="Firstname Lastname",
        prompt="Author name for pyproject.toml",
    ),
    Parameter(
        selector=[SeedValues.author_email],
        name="author_email",
        default="firstname.lastname@email.com",
        prompt="Author email for pyproject.toml",
    ),
    # Generic value: only the project version line in pyproject.toml.
    Parameter(
        selector=[f'version = "{SeedValues.version}"', SeedValues.version],
        name="version",
        default="0.1.1",
        prompt="Semantic Version, in {major}.{minor}.{micro} (e.g. 0.1.1)",
        include=["pyproject.toml"],
    ),
    # Generic value: only the dev Python pin in mise.toml.
    Parameter(
        selector=[
            f'python = "{SeedValues.dev_python_version}"',
            SeedValues.dev_python_version,
        ],
        name="dev_python_version",
        default=SeedValues.dev_python_version,
        prompt=f"Python version for local development, in {{major}}.{{minor}} (e.g. {SeedValues.dev_python_version})",
        include=["mise.toml"],
    ),
    Parameter(
        selector=[SeedValues.github_token_field],
        name="github_token_field",
        default="your_github_token_field",
        prompt=f"GitHub token field. {_HOME_SECRET_HELP}",
    ),
    Parameter(
        selector=[SeedValues.codecov_token_field],
        name="codecov_token_field",
        default="your_codecov_token_field",
        prompt=f"Codecov.io token field. {_HOME_SECRET_HELP}",
    ),
    Parameter(
        selector=[SeedValues.readthedocs_token_field],
        name="readthedocs_token_field",
        default="your_readthedocs_token_field",
        prompt=f"Readthedocs.org token field. {_HOME_SECRET_HELP}",
    ),
    Parameter(
        selector=[SeedValues.pypi_token_field],
        name="pypi_token_field",
        default="your_pypi_token_field",
        prompt=f"PyPI token field. {_HOME_SECRET_HELP}",
    ),
]

# Git-visible seed files that must not enter the template.
EXCLUDE = [
    "LICENSE.txt",  # generated by hooks/post_gen_project.py
    "uv.lock",  # carries the seed's own package name; generated projects re-lock
]

# Files copied byte for byte (no variable replacement).
NO_RENDER = [
    "*/vendor/**/*.*",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-doc.txt",
    "requirements-mise.txt",
    "requirements-test.txt",
    "*.jinja",
    "*.j2",
    "*.html",
]

# Choice variables whose values send hooks or the template down different
# branches. test-template generates once per extra choice value
# (03-parameterization.md, "Choice Coverage").
CHOICE_COVERAGE = [
    "license",  # hooks/post_gen_project.py writes a different LICENSE.txt per value
]

# Files the hooks create or rewrite in a generated project. check-roundtrip
# allows them to differ from the seed.
HOOK_OUTPUTS = [
    "LICENSE.txt",  # hooks/post_gen_project.py writes it from the chosen license
]

# Seed values unique enough that any occurrence left in the template is a
# leak, scanned by check-seed-values. Generic values (license, version,
# dev_python_version) also appear legitimately elsewhere; check-roundtrip
# verifies them instead.
UNIQUE_SEED_VALUES = {
    "package_name": SeedValues.package_name,
    "package_name_slug": SeedValues.package_name_slug,
    "github_username": SeedValues.github_username,
    "author": SeedValues.author,
    "author_email": SeedValues.author_email,
    "github_token_field": SeedValues.github_token_field,
    "codecov_token_field": SeedValues.codecov_token_field,
    "readthedocs_token_field": SeedValues.readthedocs_token_field,
    "pypi_token_field": SeedValues.pypi_token_field,
}

_MAINTAINER_LINK = "links to the maintainer's own project, must stay literal"

# Unique seed values that may legally remain in the template, consumed by
# check-seed-values. Each entry: (seed value name, template-relative file, reason).
LEGAL_RESIDUES: list[tuple[str, str, str]] = [
    ("github_username", ".claude/settings.local.json.example", _MAINTAINER_LINK),
    ("github_username", ".claude/skills/pywf-oss-base/references/01-secrets.md", _MAINTAINER_LINK),
    ("github_username", ".claude/skills/pywf-oss-base/references/14-docfly.md", _MAINTAINER_LINK),
]


def get_seed_context() -> dict[str, str]:
    """
    The cookiecutter context that renders the template back into the seed.
    """
    return {
        p.name: getattr(SeedValues, p.name)
        for p in PARAMETERS
        if p.in_cookiecutter_json
    }


def add_template_version(path_json) -> None:
    """
    Record the tpl repo's own version as the private variable
    ``_template_version``: cookiecutter never prompts for it, but it is part of
    every generation's context. It goes right after the last prompted variable.
    """
    data = json.loads(path_json.read_text(encoding="utf-8"))
    result = {}
    for key, value in data.items():
        if key.startswith("_") and "_template_version" not in result:
            result["_template_version"] = cctpl.get_tpl_version()
        result[key] = value
    path_json.write_text(json.dumps(result, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    dir_stage_seed = cctpl.dir_stage / dir_seed.name
    cctpl.reset_dir(cctpl.dir_stage)
    n_files = cctpl.stage_git_visible_files(dir_seed, dir_stage_seed)
    print(f"Staged {n_files} git-visible files from {dir_seed}")

    if cctpl.dir_template.exists():
        cctpl.reset_dir(cctpl.dir_template)
        cctpl.dir_template.rmdir()
    maker = Maker(
        dir_input=dir_stage_seed,
        dir_output=cctpl.dir_template,
        parameters=PARAMETERS,
        exclude=EXCLUDE,
        no_render=NO_RENDER,
        dir_hooks=cctpl.dir_project_root / "hooks",
        verbose=False,
    )
    maker.make_template()
    add_template_version(maker.path_cookiecutter_json)
    print(f"Template written to {cctpl.dir_template}")
    return 0


if __name__ == "__main__":
    cctpl.run_task(main)
