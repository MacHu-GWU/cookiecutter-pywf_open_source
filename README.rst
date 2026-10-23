.. This file is the source of README.rst. Do not edit README.rst by hand:
   apply-template (mise run sync) renders it from this file.

.. image:: https://img.shields.io/badge/Release_History!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/cookiecutter-pywf_open_source/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/cookiecutter-pywf_open_source


``cookiecutter-pywf_open_source``
==============================================================================


Overview
------------------------------------------------------------------------------
This template provides a ready-to-use structure for Python open source library projects. It generates a complete development environment that allows you to start coding immediately and publish to `PyPI <https://pypi.org/>`_ with minimal setup.

**Key Features:**

- **Modern tooling**: Uses `mise-en-place <https://mise.jdx.dev/>`_ for task management and `uv <https://docs.astral.sh/uv/>`_ for fast Python package management
- **Complete CI/CD**: Pre-configured GitHub Actions, CodeCov, and ReadTheDocs integration
- **Developer-friendly**: Simple commands like ``mise run test`` or ``mise run cov`` replace complex pytest invocations
- **Documentation ready**: Sphinx documentation setup with auto-generation scripts
- **AI ready**: Ships Claude Code skills that know the project's toolchain and workflows


Disclaimer
------------------------------------------------------------------------------
The best practices implemented in this repository reflect my personal experience from developing `over 150 open source Python libraries <https://pypi.org/user/machugwu/>`_, 200+ proof-of-concept initiatives, 100+ enterprise-grade applications, and 50+ production systems. This workflow enables me to publish a new Python library to PyPI within an hour of conception. While these practices have proven effective for me, please use them at your own discretion.


Usage
------------------------------------------------------------------------------
Enter the following command to use the latest template version:

.. code-block:: bash

    pip install "cookiecutter>=2.6.0,<3.0.0" && cookiecutter https://github.com/MacHu-GWU/cookiecutter-pywf_open_source

To use a specific released version (see the `full list of releases <https://github.com/MacHu-GWU/cookiecutter-pywf_open_source/releases>`_):

.. code-block:: bash

    cookiecutter https://github.com/MacHu-GWU/cookiecutter-pywf_open_source --checkout tags/${version}

For example, to use ``3.0.2``, the latest version:

.. code-block:: bash

    cookiecutter https://github.com/MacHu-GWU/cookiecutter-pywf_open_source --checkout tags/3.0.2

You'll then be prompted to provide the following information (defaults in parentheses):

.. code-block:: bash

    [1/11] Your Python package name, in snake case (e.g. my_package) (your_package_name): your_package_name
    [2/11] Your GitHub username, the owner of the new repo (your_github_username): your_github_username
    [3/11] Pick a license, as an SPDX expression for pyproject.toml, see https://choosealicense.com/ for details
      1 - MIT
      2 - AGPL-3.0-or-later
      3 - LicenseRef-Proprietary
      Choose from [1/2/3] (1): 1
    [4/11] Author name for pyproject.toml (Firstname Lastname): Firstname Lastname
    [5/11] Author email for pyproject.toml (firstname.lastname@email.com): firstname.lastname@email.com
    [6/11] Semantic Version, in {major}.{minor}.{micro} (e.g. 0.1.1) (0.1.1): 0.1.1
    [7/11] Python version for local development, in {major}.{minor} (e.g. 3.12) (3.12): 3.12
    [8/11] GitHub token field. Read https://github.com/MacHu-GWU/home_secret_toml-project to learn how to set up your tokens using home_secret.toml (your_github_token_field): your_github_token_field
    [9/11] Codecov.io token field. Read https://github.com/MacHu-GWU/home_secret_toml-project to learn how to set up your tokens using home_secret.toml (your_codecov_token_field): your_codecov_token_field
    [10/11] Readthedocs.org token field. Read https://github.com/MacHu-GWU/home_secret_toml-project to learn how to set up your tokens using home_secret.toml (your_readthedocs_token_field): your_readthedocs_token_field
    [11/11] PyPI token field. Read https://github.com/MacHu-GWU/home_secret_toml-project to learn how to set up your tokens using home_secret.toml (your_pypi_token_field): your_pypi_token_field

This will generate a repository structure similar to `cookiecutter_pywf_open_source_demo-project <https://github.com/MacHu-GWU/cookiecutter_pywf_open_source_demo-project>`_.

Once generated, navigate to your project directory and explore the available automation tasks:

.. code-block:: bash

    cd your_package_name-project
    mise tasks ls  # List all available tasks


Project Maintainer Note
------------------------------------------------------------------------------
**Project Architecture:**

- **Seed Repository**: `cookiecutter_pywf_open_source_demo-project <https://github.com/MacHu-GWU/cookiecutter_pywf_open_source_demo-project>`_ - A concrete, runnable project used as the source for template generation
- **Cookiecutter Template**: `cookiecutter-pywf_open_source <https://github.com/MacHu-GWU/cookiecutter-pywf_open_source>`_ - This repository

**Maintenance Workflow:**

This template is maintained using a "reverse engineering" approach, driven by Claude Code skills (``.claude/skills/cctpl-*-cn``):

1. Make changes in the Seed project (``cookiecutter_pywf_open_source_demo-project``)
2. In the Seed, bump the version and record the changes in its own ``release-history-seed-repo.rst``. The Seed and this template share one version number, and the Seed's ``pyproject.toml`` is its only source
3. Run ``mise run e2e``: it converts the Seed into a template, checks it, applies it to this repo (version included), then generates a project and runs its tests and docs build
4. Commit and push the Seed, then tag it with ``mise run publish`` and ``mise run release`` in the Seed
5. Run ``/cctpl-release-cn`` to write this repo's changelog section, which links to the Seed's section of the same version, then ``mise run publish-template`` to publish the template to GitHub. A published version is never overwritten
6. Run ``/cctpl-verify-cn`` to verify the published template

**Toolchain:**

- **mise-en-place**: Task runner and tool version manager
- **uv**: Fast Python package installer and resolver
- **cookiecutter-maker**: Reverse-engineering tool that converts concrete projects into templates

For the full maintenance specification, see `cctpl-base-cn <./.claude/skills/cctpl-base-cn/SKILL.md>`_.
