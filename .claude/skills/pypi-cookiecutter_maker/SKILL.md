---
name: pypi-cookiecutter_maker
description: Python library cookiecutter_maker, the reverse of cookiecutter. It converts a concrete seed project into a cookiecutter template by replacing chosen strings in folder names, file names and file contents with cookiecutter variables, optionally only in a given context or in given files, filters files with gitignore style include, exclude and no_render patterns, escapes existing Jinja2 syntax, and writes cookiecutter.json with defaults, choices and prompts. Public API is Maker and Parameter, plus the cookiecutter-maker command line tool with make, init and version commands driven by a cookiecutter-maker.json config file. Generated for `cookiecutter_maker` version `1.1.0`. Higher installed versions should generally be compatible, lower versions may still work but correctness is not guaranteed.
---

# cookiecutter_maker

Turn a working project (the "seed") into a cookiecutter template. Each `Parameter` maps a concrete string (e.g. `acme_tools`) to `{{ cookiecutter.<name> }}`; `Maker` walks the seed directory, replaces parameters in names and contents, filters files, and writes the template plus `cookiecutter.json`.

## Import

```python
from cookiecutter_maker.api import Maker, Parameter
import cookiecutter_maker.api as cookiecutter_maker   # then cookiecutter_maker.Maker
```

## Public API

- `Maker` — dataclass holding seed dir, output dir, parameters and file filters; `make_template()` generates the template.
- `Parameter` — dataclass mapping a selector string (optionally in context, optionally only in some files) to a cookiecutter variable, with default or choice.

## CLI

Command is typically `.venv/bin/cookiecutter-maker` (needs the `cli` extra, `pip install "cookiecutter-maker[cli]"`). Run `cookiecutter-maker --help` for help. Full args live in `ref/cli.md`.

## More detail

For signatures, semantics and key examples see `ref/public-api.md`. For full CLI args and the config file format see `ref/cli.md`.
