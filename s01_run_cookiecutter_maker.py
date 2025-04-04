# -*- coding: utf-8 -*-

"""
Convert a seed repo into a project template.
"""

import shutil
from pathlib import Path
from cookiecutter_maker.api import Parameter, Maker

# Get the current directory and create a temporary directory for output
dir_here: Path = Path(__file__).absolute().parent
dir_tmp = dir_here.joinpath("tmp")

# Create a Maker instance to convert the project into a template
maker = Maker(
    # The input concrete project directory - the seed project you want to templatize
    dir_input=Path.home().joinpath(
        "Documents",
        "GitHub",
        "cookiecutter_pywf_open_source_demo-project",
    ),
    # The output template directory - where the generated template will be placed
    dir_output=dir_tmp,
    # Define parameters that will be customizable in the generated template
    parameters=[
        Parameter(
            selector=["cookiecutter_pywf_open_source_demo"],
            name="package_name",
            default="your_package_name",
            prompt="Your Python package name, in snake case (e.g. my_package)",
        ),
        Parameter(
            selector=["cookiecutter-pywf-open-source-demo"],
            name="package_name_slug",
            default="your-package-name",
            custom_placeholder="{{ cookiecutter.package_name | slugify }}",
            in_cookiecutter_json=False,
        ),
        Parameter(
            selector=["MacHu-GWU"],
            name="github_username",
            default="your_github_username",
        ),
        Parameter(
            selector=['license = "MIT"', "MIT"],
            name="license",
            choice=[
                "MIT",
                "AGPL-3.0-or-later",
                "Proprietary",
            ],
            prompt="Pick an open source license for pyproject.toml file, see https://choosealicense.com/ for details",
        ),
        Parameter(
            selector=["License :: OSI Approved :: MIT License"],
            name="license_classifier",
            default=[
                "License :: OSI Approved :: MIT License",
                "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
                "License :: Other/Proprietary License",
            ],
            prompt="Pick a license classifier, this has to match the previous one",
        ),
        Parameter(
            selector=["Sanhe Hu"],
            name="author",
            default="Firstname Lastname",
            prompt="Author name for pyproject.toml file",
        ),
        Parameter(
            selector=["husanhe@gmail.com"],
            name="author_email",
            default="firstname.lastname@email.com",
            prompt="Author email for pyproject.toml file",
        ),
        Parameter(
            selector=[
                'version = "0.1.1"',
                "0.1.1",
            ],
            name="version",
            default="0.1.1",
            prompt="Semantic Version, in {major}.{minor}.{micro} (e.g. 0.1.1)",
        ),
        Parameter(
            selector=['dev_python = "3.11.8"', "3.11.8"],
            name="dev_python_version",
            default="3.11.8",
            prompt="Python version for local development, in {major}.{minor}.{micro} (e.g. 3.11.8)",
        ),
        Parameter(
            selector=["sanhe-dev"],
            name="token_name",
            default="your_github_codecov_rtd_token_name",
            prompt=(
                "Your GitHub token, codecov token and readthedocs token name (better to be the same name), "
                "if you want to automatically setup CI/CD for your project"
            ),
        ),
        Parameter(
            selector=['readthedocs_username = "machugwu"', "machugwu"],
            name="readthedocs_username",
            default="your_readthedocs_username",
            prompt="Your readthedocs.org username, if you want to host your documentation website on readthedocs.org",
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
        ".poetry",
        "tmp",
        "bin/pywf_open_source",
        "docs/source/cookiecutter_pywf_open_source_demo",
        # file
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
        "poetry.lock",
        "requirements.txt",
        "requirements-automation.txt",
        "requirements-dev.txt",
        "requirements-doc.txt",
        "requirements-test.txt",
        "requirements-poetry.txt",
        # template file
        "*.jinja",  # Jinja template files
        "*.j2",  # Alternative Jinja extension
        "*.html",  # HTML files with {{ }} syntax
    ],
    dir_hooks=dir_here.joinpath("hooks"),
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
