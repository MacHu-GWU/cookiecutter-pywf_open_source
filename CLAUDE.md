# CLAUDE.md

## Project Overview

This is a **cookiecutter project template** (`cookiecutter-pywf_open_source`) for generating Python open source library projects. It is maintained using a "reverse engineering" approach: a real seed project is converted into a cookiecutter template via an automated script.

- **This repo** (template): `$HOME/GitHub/cookiecutter-pywf_open_source`
- **Seed repo** (concrete project): `$HOME/GitHub/cookiecutter_pywf_open_source_demo-project`
- **Generated template dir**: `{{ cookiecutter.package_name }}-project/`

## Key Tasks (mise)

- `mise run make-template` — Converts the seed project into a cookiecutter template. Reads the seed repo, replaces concrete values with cookiecutter placeholders, outputs to `tmp/`. Script: `.mise/tasks/make-template.py`
- `mise run publish-template` — Publishes the template: copies from `tmp/` to the template dir, commits and pushes to `main`, merges into other branches (e.g. `sanhe`), and creates/updates a GitHub release. Script: `.mise/tasks/publish-template.py`

## Workflow

1. Make changes in the seed project (`$HOME/GitHub/cookiecutter_pywf_open_source_demo-project`)
2. Run `mise run make-template` to regenerate the template
3. Review the generated template in `tmp/`
4. Run `mise run publish-template` to commit, push, merge branches, and create a GitHub release

## Python Environment

- Virtual environment: `.venv/bin/python`

## Important Directories

- `hooks/` — Cookiecutter hooks (post-gen scripts)
- `{{ cookiecutter.package_name }}-project/` — The generated template directory (do not edit manually; regenerate via `s01`)
- `tmp/` — Temporary output from `s01` (gitignored intermediate output)
