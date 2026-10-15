# -*- coding: utf-8 -*-

"""
Facts that belong to this tpl repo + seed repo pair, for the generic task code.

Everything else under ``.mise/tasks/`` works for any pair, except the
parameterization declarations in ``make_template.py``. When this family is
forked to another pair (/cctpl-fork-cn), this file is rewritten as a whole.

Where every pair-specific fact lives:
``.claude/skills/cctpl-base-cn/references/02-repo-layout.md``, "Where Facts Live".
"""

# --- GitHub coordinates of the tpl repo (publish, verify, README)
GITHUB_OWNER = "MacHu-GWU"
GITHUB_REPO = "cookiecutter-pywf_open_source"

# --- the template dir: the project folder name inside the template
TEMPLATE_DIR_NAME = "{{ cookiecutter.package_name }}-project"

# --- generated projects (06-verification.md, L4, L5 and Local Trial)

# The cookiecutter variable holding the Python version a generated project uses.
PYTHON_VERSION_VARIABLE = "dev_python_version"

# How L4 / L5 install a generated project and run its tests, without mise.
# Run in the project dir after "uv venv --python <version>".
INSTALL_COMMAND = ["uv", "sync", "--all-extras"]
TEST_COMMAND = [".venv/bin/pytest", "tests", "-q"]

# The generated project's own mise tasks that the Local Trial runs, in order.
PROJECT_TASKS = ["venv-create", "inst", "cov", "build-doc"]
