# CLAUDE.md

## Project Overview

This is a **cookiecutter project template** (`cookiecutter-pywf_open_source`) for generating Python open source library projects. It is maintained using a "reverse engineering" approach: a real seed project is converted into a cookiecutter template via an automated script.

- **This repo** (template): `$HOME/GitHub/cookiecutter-pywf_open_source`
- **Seed repo** (concrete project): `$HOME/GitHub/cookiecutter_pywf_open_source_demo-project`
- **Generated template dir**: `{{ cookiecutter.package_name }}-project/`

## Maintenance Workflow (5-Step Process)

**IMPORTANT:** Always make changes in the **Seed project** first, never edit the template directly.

### Step 1: `mise run make-template`
**Purpose:** Convert the seed project into a cookiecutter template

- Reads the seed project from `$HOME/GitHub/cookiecutter_pywf_open_source_demo-project`
- Replaces concrete values (e.g., `cookiecutter_pywf_open_source_demo`) with placeholders (e.g., `{{ cookiecutter.package_name }}`)
- Outputs the generated template to `tmp/` directory
- Script: `.mise/tasks/make_template.py`

**What to do:** Review the generated template in `tmp/` to ensure it looks correct.

### Step 2: `mise run check-seed-values`
**Purpose:** Verify no seed project values leaked into the template

- Scans the generated template in `tmp/` for residual seed project values
- Checks for strings like `cookiecutter_pywf_open_source_demo`, `MacHu-GWU`, etc.
- Reports any values that should have been replaced but weren't
- Script: `.mise/tasks/check_seed_values.py`

**What to do:** If errors are found, fix the `make_template.py` script to handle those cases.

### Step 3: `mise run test-template`
**Purpose:** Test that the template can generate a project

- Runs cookiecutter with default values: `cookiecutter tmp --no-input`
- Generates a test project in `tmp/output/`
- Verifies the template syntax is valid and can produce a project
- Outputs the location of the generated test project

**What to do:** Inspect `tmp/output/` to ensure the generated project looks correct.

### Step 4: `mise run check-output`
**Purpose:** Verify all cookiecutter placeholders were resolved

- Scans the generated output in `tmp/output/` for unresolved placeholders
- Checks for strings like `{{ cookiecutter.xxx }}` or `{% ... %}`
- Reports any placeholders that weren't properly substituted
- Script: `.mise/tasks/check_output.py`

**What to do:** If errors are found, fix the template or `cookiecutter.json` defaults.

### Step 5: `mise run publish-template` ⚠️ USE WITH CAUTION
**Purpose:** Publish the template to GitHub

**This task performs DESTRUCTIVE operations:**
1. Copies template from `tmp/` to `{{ cookiecutter.package_name }}-project/`
2. Commits all changes with message: "update template"
3. Pushes to `main` branch
4. Merges `main` into special branches (e.g., `sanhe`)
5. Creates/updates a GitHub release

**⚠️ WARNING:** This task:
- Automatically commits and pushes to remote
- Creates public releases
- Cannot be easily undone

**What to do:**
- Only run after verifying steps 1-4 passed
- Ensure you're ready to publish these changes
- Consider manually reviewing the diff before running

Script: `.mise/tasks/publish_template.py`

## Quick Commands

**One-liner (use with caution):**
```bash
mise run all  # Runs all 5 steps sequentially
```

**Recommended workflow (step-by-step verification):**
```bash
# 1. Make changes in seed project first
cd $HOME/GitHub/cookiecutter_pywf_open_source_demo-project
# ... make your changes ...

# 2. Return to template repo
cd $HOME/GitHub/cookiecutter-pywf_open_source

# 3. Generate and verify (safe operations)
mise run make-template
mise run check-seed-values
mise run test-template
mise run check-output

# 4. Review the generated files manually
# Check tmp/ and tmp/output/ directories

# 5. Only if everything looks good
mise run publish-template  # ⚠️ DESTRUCTIVE - pushes to GitHub
```

## Environment

- Python: Managed by mise (see `mise.toml`)
- Virtual environment: `.venv/bin/python`
- Dependencies: Installed via `uv sync --all-extras`

## Important Directories

- `hooks/` — Cookiecutter hooks (post-generation scripts)
- `{{ cookiecutter.package_name }}-project/` — The template directory (auto-generated, do not edit manually)
- `tmp/` — Temporary output directory (gitignored)
  - `tmp/` — Generated template (after step 1)
  - `tmp/output/` — Test project output (after step 3)
- `.mise/tasks/` — Automation scripts for template maintenance
