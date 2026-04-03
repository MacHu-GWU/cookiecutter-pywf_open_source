# -*- coding: utf-8 -*-

"""
Convert a seed repo into a project template.
"""

import shutil
import tomllib
from pathlib import Path
from cookiecutter_maker.api import Parameter, Maker
from cookiecutter_pywf_open_source.paths import path_enum

# Get the project root directory
dir_tmp = path_enum.dir_tmp
dir_seed = Path.home().joinpath(
    "Documents",
    "GitHub",
    "cookiecutter_pywf_open_source_demo-project",
)

# Extract dynamic values from the seed project
with open(dir_seed / "pyproject.toml", "rb") as f:
    _pyproject = tomllib.load(f)
with open(dir_seed / "mise.toml", "rb") as f:
    _mise_config = tomllib.load(f)


class SeedValues:
    """Concrete values in the seed project that need to be reverse-replaced."""

    # --- identity ---
    package_name = "cookiecutter_pywf_open_source_demo"
    package_name_slug = "cookiecutter-pywf-open-source-demo"
    github_username = "MacHu-GWU"

    # --- license ---
    license = "MIT"
    license_classifier = "License :: OSI Approved :: MIT License"

    # --- author ---
    author = "Sanhe Hu"
    author_email = "husanhe@gmail.com"

    # --- versioning (dynamic) ---
    version = _pyproject["project"]["version"]
    dev_python_version = _mise_config["tools"]["python"]

    # --- secret token fields ---
    github_token_field = "github.accounts.sh.users.sh.secrets.dev.value"
    codecov_token_field = "codecov_io.accounts.sh.users.sh.secrets.dev.value"
    readthedocs_token_field = "readthedocs.accounts.sh.users.sh.secrets.dev.value"


# Validate version format
_parts = SeedValues.version.split(".")
assert len(_parts) == 3 and all(v.isdigit() for v in _parts), (
    f"Invalid version: {SeedValues.version}"
)

# For backward compatibility (publish-template.py imports this)
version_to_replace = SeedValues.version

# Create a Maker instance to convert the project into a template
maker = Maker(
    # The input concrete project directory - the seed project you want to templatize
    dir_input=dir_seed,
    # The output template directory - where the generated template will be placed
    dir_output=dir_tmp,
    # Define parameters that will be customizable in the generated template
    parameters=[
        Parameter(
            selector=[SeedValues.package_name],
            name="package_name",
            default="your_package_name",
            prompt="Your Python package name, in snake case (e.g. my_package)",
        ),
        Parameter(
            selector=[SeedValues.package_name_slug],
            name="package_name_slug",
            default="your-package-name",
            custom_placeholder="{{ cookiecutter.package_name | slugify }}",
            in_cookiecutter_json=False,
        ),
        Parameter(
            selector=[SeedValues.github_username],
            name="github_username",
            default="your_github_username",
        ),
        Parameter(
            selector=[f'license = "{SeedValues.license}"', SeedValues.license],
            name="license",
            choice=[
                "MIT",
                "AGPL-3.0-or-later",
                "Proprietary",
            ],
            prompt="Pick an open source license for pyproject.toml file, see https://choosealicense.com/ for details",
        ),
        Parameter(
            selector=[f'__license__ = "{SeedValues.license}"', SeedValues.license],
            name="license",
            choice=[
                "MIT",
                "AGPL-3.0-or-later",
                "Proprietary",
            ],
            prompt="Pick an open source license for pyproject.toml file, see https://choosealicense.com/ for details",
        ),
        Parameter(
            selector=[SeedValues.license_classifier],
            name="license_classifier",
            default=[
                "License :: OSI Approved :: MIT License",
                "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
                "License :: Other/Proprietary License",
            ],
            prompt="Pick a license classifier, this has to match the previous one",
        ),
        Parameter(
            selector=[SeedValues.author],
            name="author",
            default="Firstname Lastname",
            prompt="Author name for pyproject.toml file",
        ),
        Parameter(
            selector=[SeedValues.author_email],
            name="author_email",
            default="firstname.lastname@email.com",
            prompt="Author email for pyproject.toml file",
        ),
        Parameter(
            selector=[
                f'version = "{SeedValues.version}"',
                SeedValues.version,
            ],
            name="version",
            default="0.1.1",
            prompt="Semantic Version, in {major}.{minor}.{micro} (e.g. 0.1.1)",
        ),
        Parameter(
            selector=[
                f'__version__ = "{SeedValues.version}"',
                SeedValues.version,
            ],
            name="version",
            default="0.1.1",
            prompt="Semantic Version, in {major}.{minor}.{micro} (e.g. 0.1.1)",
        ),
        Parameter(
            selector=[
                f'python = "{SeedValues.dev_python_version}"',
                SeedValues.dev_python_version,
            ],
            name="dev_python_version",
            default=SeedValues.dev_python_version,
            prompt=f"Python version for local development, in {{major}}.{{minor}} (e.g. {SeedValues.dev_python_version})",
        ),
        Parameter(
            selector=[SeedValues.github_token_field],
            name="github_token_field",
            default="your_github_token_field",
            prompt="GitHub token field, Read https://github.com/MacHu-GWU/home_secret_toml-project to learn how to set up your GitHub token using home_secret.json",
        ),
        Parameter(
            selector=[SeedValues.codecov_token_field],
            name="codecov_token_field",
            default="your_codecov_token_field",
            prompt="Codecov.io token field, Read https://github.com/MacHu-GWU/home_secret_toml-project to learn how to set up your GitHub token using home_secret.json",
        ),
        Parameter(
            selector=[SeedValues.readthedocs_token_field],
            name="readthedocs_token_field",
            default="your_readthedocs_token_field",
            prompt="Readthedocs.org token field, Read https://github.com/MacHu-GWU/home_secret_toml-project to learn how to set up your GitHub token using home_secret.json",
        ),
    ],
    # Define which files/directories to include in the template
    # Empty list means include everything not explicitly excluded
    # You can use patterns like "**/*.py" to include all Python files
    # The rule is 'explicit exclude' > 'explicit include' > 'default include'
    include=[],
    # define what to exclude in the input directory
    # Define which files/directories to exclude from the template
    exclude=[
        # dir
        ".git",  # Git repository data
        ".venv",  # Virtual environment
        ".pytest_cache",  # Test cache
        ".idea",  # PyCharm stuff
        "build",  # Build artifacts
        "dist",  # Distribution packages
        "htmlcov",  # HTML coverage reports
        "__pycache__",  # Python cache files
        "tmp",
        # file
        ".claude/claude-code-messages.md",
        ".claude/settings.local.json",
        ".coverage",  # Coverage data
        ".pyc",  # Compiled Python files
        "LICENSE.txt",  # License file, we will generate this later
    ],
    # Files that should be copied without rendering (processing)
    # Useful for files that contain syntax that conflicts with Jinja2
    # For example, template files that already use {{ }} syntax
    no_render=[
        # dir
        "*/vendor/**/*.*",
        # file
        "uv.lock",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-doc.txt",
        "requirements-mise.txt",
        "requirements-test.txt",
        # template file
        "*.jinja",  # Jinja template files
        "*.j2",  # Alternative Jinja extension
        "*.html",  # HTML files with {{ }} syntax
    ],
    dir_hooks=path_enum.dir_project_root.joinpath("hooks"),
    # Print detailed information during processing
    verbose=True,
)

if __name__ == "__main__":
    # Clean up any existing temporary directory
    if dir_tmp.exists():
        shutil.rmtree(dir_tmp)

    # Execute the template generation process
    maker.make_template()

    print("\n" + "=" * 80)
    print("Template generation complete!")
    print(f"The template is available at: {dir_tmp}")
    print("\nTo create a new project from this template, run:")
    print(f"    cookiecutter {dir_tmp}")
    print("=" * 80 + "\n")
