---
name: pywf-oss-write-pypi-skill
description: "Generate an Agent Skill, named after the package, that documents this library's public API and command line interface, so future sessions in other projects can use the library without re-reading its source. Use when the user asks to turn this library into a Claude skill, usually after a release."
---

Generate an Agent Skill that lets future sessions use this library through its public API, without loading the source.

Read ../pywf-oss-base/SKILL.md, then:
- ../pywf-oss-base/references/08-package-files.md (`api.py` defines the public API; `cli.py` is the python-fire CLI)

## Where to write the output

Default to `~/.claude/skills/<package_name>/` (personal: usable in every project that installs the library). If the user clearly wants it project-only, use `.claude/skills/<package_name>/`. If the target directory exists, ask before overwriting.

## Step 1: Inspect the project

From `pyproject.toml` at the working-directory root, take:

- `[project].name`: `<package_name>`, which is also the skill's name.
- `[project].version`: for the skill header.
- `[project.scripts]`, if present: the CLI entry point (such as `<cli_name> = "<package_name>.cli:main"`) and its executable name, the key.

## Step 2: Walk the public API

Read `<package_name>/api.py` top to bottom: **each `from ... import X` line is one public symbol**. For each, open its defining module:

- **Constant or function:** signature, docstring, and return value.
- **Class or dataclass:** also every non-underscore method and property, each with its signature and a one-line summary, and a dataclass's fields.
- **Subpackage API** (`from .subpackage import api as subpackage`): recurse into its `api.py` with the same rules. Users refer to its symbols as `subpackage.ClassName`.

Skip every name starting with `_`. Document only the two canonical import forms:

```python
from <package_name>.api import X
import <package_name>.api as <package_name>     # then <package_name>.X
```

## Step 3: Take usage examples from `tests/`

Grep `tests/` for each public symbol. The shortest passing test that exercises it is usually the cleanest example: trim it to the essentials, never paste whole test files.

## Step 4: Inspect the CLI (only when `[project.scripts]` exists)

Read the entry-point module, and walk the whole command tree: every subcommand, flag, and default. All of it goes into `ref/cli.md`.

## Step 5: Write the skill

```
<base>/<package_name>/
├── SKILL.md
└── ref/
    ├── public-api.md
    └── cli.md          # only if the library has a CLI
```

### SKILL.md: overview, always loaded

It must suffice for common tasks **without** `ref/`, in 50 to 150 lines:

- **Frontmatter `description`:** the library name, what it does in one sentence, and its top public symbols, so the skill surfaces on matching requests.
- **Purpose:** one paragraph.
- **Import:** the two canonical forms above, nothing else.
- **Public API:** a flat list, one entry per symbol: a function or method with its typed signature and a one-line summary; a dataclass with its fields and summary, then its method and property signatures, one per line; a constant with its value or type and summary.
- **CLI** (only if any): one short paragraph. The command is usually `.venv/bin/<cli_name>`, `<cli_name> -h` lists the subcommands, and `ref/cli.md` has every argument. **Do not list subcommands here:** CLI use is rare, so its detail loads lazily.
- **More detail:** "For full API docs see `ref/public-api.md`. For full CLI args see `ref/cli.md`."

### `ref/public-api.md`: full API reference, loaded on demand

Written for an engineer **using** the library, not maintaining it. For each public symbol: the full typed signature; parameter and return semantics, with the *why* only when non-obvious (invariants, gotchas, constraints the caller must respect); and a short usage example, preferably trimmed from `tests/`. No walkthroughs of internal code.

### `ref/cli.md`: full CLI reference, loaded on demand

It loads when the user mentions the CLI, so it must make `--help` unnecessary: for each subcommand, a short description, every flag with type and default (a small table reads well), and one short example. Complete, not verbose.

## Keep it short

Every line of `SKILL.md` stays in the conversation once the skill is invoked, so it costs tokens on every use. Prefer signatures, tables, and short examples to prose; the same holds, less strictly, for the lazily loaded `ref/` files.

## Verify before finishing

For 2 or 3 representative symbols, check that the import works:

```bash
.venv/bin/python -c "from <package_name>.api import ClassName"
```

If one fails, the docs are wrong. Fix them before reporting done.
