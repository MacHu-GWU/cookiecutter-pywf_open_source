# cookiecutter_maker public API reference (v1.1.0)

Import: `from cookiecutter_maker.api import Maker, Parameter`. All fields are type-checked on construction; wrong types (e.g. a str where a list is expected, `"false"` for a bool) raise `ValueError`.

## `Parameter` (dataclass)

```python
Parameter(
    selector: list[str],
    name: str,
    default: Any | None = None,
    choice: list[Any] = [],
    prompt: str | dict | None = None,
    custom_placeholder: str | None = None,
    in_cookiecutter_json: bool = True,
    include: list[str] = [],
    exclude: list[str] = [],
)
```

- `selector` — broadest context first, value last. Only `selector[0]` is searched; inside each match every occurrence of the **last** selector becomes the placeholder. Each item must be a substring of the previous one; `selector[0]` can't be empty. Plain, case-sensitive substring match (`acme_tools` also hits `acme_tools_extra`); selectors may span lines.
- `name` — non-empty; placeholder is `{{ cookiecutter.<name> }}`.
- `default` / `choice` — exactly one required when `in_cookiecutter_json=True`. `choice[0]` is the default.
- `prompt` — written to `__prompts__` of `cookiecutter.json`; a dict gives choice labels.
- `custom_placeholder` — replaces the last selector (keeping the context) instead of the default token, e.g. `{{ cookiecutter.package_name | slugify }}`. Pair with `in_cookiecutter_json=False` for derived values.
- `include` / `exclude` — gitignore-style patterns (relative to `dir_input`) limiting which files' **content** this parameter touches. File/dir **names** always use all parameters. Exclude wins. If a longer selector is excluded from a file, a shorter one may still match inside it.

Methods / properties:

- `Parameter.from_dict(data: dict) -> Parameter` — classmethod; `ValueError` on non-dict, unknown keys (typos) or missing required keys.
- `placeholder: str` — what `selector[0]` becomes, e.g. `'version = "{{ cookiecutter.version }}"'`.
- `path_matcher` — matcher built from `include` / `exclude`.
- `is_applied_to(path: str) -> bool` — whether the parameter applies to the content of a `/`-separated relative path.
- `to_cookiecutter_key_value() -> tuple[str, Any]` — `(name, choice)` if choice set, else `(name, default)`.

## `Maker` (dataclass)

```python
Maker(
    dir_input: Path | str,
    dir_output: Path | str,
    parameters: list[Parameter],
    include: list[str] = [],
    exclude: list[str] = [],
    no_render: list[str] = [],
    dir_hooks: Path | str | None = None,
    verbose: bool = True,
    overwrite: bool = False,
)
```

- Output layout: `dir_output/cookiecutter.json`, `dir_output/hooks/` (if `dir_hooks`), `dir_output/<parameterized name of dir_input>/...`.
- **The name of `dir_input` must contain at least one `selector[0]`** (cookiecutter needs a variable in the project folder name), else `ValueError`. `dir_input="."` uses the real folder name.
- Patterns use `.gitignore` syntax (pathspec `GitIgnoreSpecPattern`) against the path relative to `dir_input` with `/`. Directories are matched with a trailing `/`, so `build/` works.
- `exclude` — matched files and dirs dropped; excluded dirs not walked. Wins over `include`.
- `include` — if non-empty, only matched **files** kept; dirs not filtered by it, and only dirs containing kept files are created.
- `no_render` — copied byte for byte (names still parameterized). Every byte-copied file (no_render or not valid UTF-8) is listed by exact template path in `_copy_without_render`.
- `overwrite=True` deletes `dir_output` first, but only if it is empty or contains `cookiecutter.json`, and is not `dir_input`, a parent of it, or a dir containing `dir_hooks`; otherwise `ValueError`. With `overwrite=False` an existing `dir_output` raises `FileExistsError`.
- Constructor raises `ValueError` on duplicate `selector[0]` or duplicate `name` (among params in `cookiecutter.json`).
- `dir_output` inside `dir_input` is skipped automatically.

Text processing: existing Jinja2 syntax (`{{`, `}}`, `{%`, `{#`, including `{}}` and braces around a value like `${acme_tools}`) is escaped with `{% raw %}` and all parameters are replaced, in a single pass; longest match wins regardless of order; replacements are never re-replaced. Text is written with LF endings and `cookiecutter.json` sets `"_new_lines": "\n"`.

Methods / properties:

- `Maker.from_dict(data: dict) -> Maker` — classmethod; same structure as `cookiecutter-maker.json`. Path strings become `Path` as-is (relative paths NOT resolved). `parameters` must be a list of dicts or `Parameter`. Rejects unknown/missing keys.
- `make_template() -> None` — readiness check, optional delete of old output, convert seed, write `cookiecutter.json`, copy hooks.
- `readiness_check() -> None` — raises `FileNotFoundError` (missing `dir_input`/`dir_hooks`), `FileExistsError`, or `ValueError` (no selector in seed folder name, unsafe overwrite) before writing anything.
- `write_cookiecutter_json() -> None` — writes params in definition order, `__prompts__`, `_copy_without_render`, `_new_lines`.
- `copy_hooks() -> None` — copies `dir_hooks` to `<dir_output>/hooks` if set.
- `dir_template: Path` — `dir_output / <parameterized dir_input name>`.
- `path_cookiecutter_json: Path` — `dir_output / "cookiecutter.json"`.
- `path_matcher` — matcher built from `include` / `exclude` / `no_render`.

## Related helper (not in `api.py`)

`cookiecutter_maker.config.load_maker(config=None, cwd=None, **overrides) -> Maker` — what `cookiecutter-maker make` does: reads `config` (or `./cookiecutter-maker.json`), resolves its relative paths against the config file's directory, applies non-`None` overrides (paths relative to `cwd`, list fields replace), returns a `Maker`. With `overwrite`, refuses when the config file is inside `dir_output`. Referenced by the `api.py` docstring.

## Key scenarios

Basic template from Python (seed folder name contains `acme_tools`):

```python
from cookiecutter_maker.api import Maker, Parameter

Maker(
    dir_input="acme_tools-project",
    dir_output="template",
    parameters=[
        Parameter(selector=["acme_tools"], name="package_name", default="acme_tools",
                  prompt="Python package name, in snake case"),
        # context-scoped: only the project version, not dependency pins
        Parameter(selector=['version = "0.1.0"', "0.1.0"], name="version", default="0.1.0"),
        Parameter(selector=['license = "MIT"', "MIT"], name="license",
                  choice=["MIT", "Apache-2.0", "Proprietary"]),
    ],
    exclude=[".git", ".venv", "__pycache__", "*.pyc", "build/", "dist/"],
    overwrite=True,
).make_template()
```

Derived variable, file-scoped parameter, verbatim files, hooks:

```python
Maker(
    dir_input="my_package-project",
    dir_output="tmp",
    parameters=[
        Parameter(selector=["my_package"], name="package_name", default="my_package"),
        Parameter(selector=["my-package"], name="package_name_slug",
                  custom_placeholder="{{ cookiecutter.package_name | slugify }}",
                  in_cookiecutter_json=False),
        Parameter(selector=["0.1.1"], name="version", default="0.1.1",
                  include=["pyproject.toml", "*/_version.py"]),
    ],
    no_render=["*.jinja", "*/vendor/"],
    dir_hooks="hooks",
).make_template()
```

From a config file (what the CLI does):

```python
from cookiecutter_maker.config import load_maker
load_maker(config="cookiecutter-maker.json", overwrite=True).make_template()   # paths resolved
```
