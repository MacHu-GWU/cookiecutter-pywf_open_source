.. image:: https://img.shields.io/badge/Release_History!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/cookiecutter-pywf_open_source/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/pywf_open_source-pyproject


``cookiecutter-pywf_open_source``
==============================================================================


Overview
------------------------------------------------------------------------------
This template provides a ready-to-use structure for Python open source library projects. It generates a complete development environment that allows you to start coding immediately and publish to `PyPI <https://pypi.org/>`_. with minimal setup.

The template uses `pywf_open_source <https://github.com/MacHu-GWU/pywf_open_source-project>`_ as its automation engine, eliminating the cognitive overhead of remembering complex commands like ``poetry install --extras ...`` or ``pytest -s --tb=native --cov=your_package_name --cov-report term-missing tests``.

A standout feature is the built-in AI coding assistant that creates a knowledge base from your documentation, source code, and other specified files. Unlike solutions requiring vector store databases, you can simply drag and drop files to start interacting with an AI that understands your coding, testing, and documentation style. No need for Cursor, Windsurf, or API tokens - just specify which file, module, function, or class you want to work with, and it's ready to assist.


Disclaimer
------------------------------------------------------------------------------
The best practices implemented in this repository reflect my personal experience from developing `over 150 open source Python libraries <https://pypi.org/user/machugwu/>`_, 200+ proof-of-concept initiatives, 100+ enterprise-grade applications, and 50+ production systems. This workflow enables me to publish a new Python library to PyPI within an hour of conception. While these practices have proven effective for me, please use them at your own discretion.


Usage
------------------------------------------------------------------------------
Enter the following command to use the latest template version:

.. code-block:: bash

    pip install "cookiecutter>=2.6.0,<3.0.0" && cookiecutter https://github.com/MacHu-GWU/cookiecutter-pywf_open_source

To use a specific released version (see the `full list of release at here <https://github.com/MacHu-GWU/cookiecutter-pywf_open_source/releases>`_).

.. code-block:: bash

    cookiecutter https://github.com/MacHu-GWU/cookiecutter-pywf_open_source --checkout tags/${version}

For example, to use ``0.1.2`` (the latest as of 2025-05-30):

.. code-block:: bash

    cookiecutter https://github.com/MacHu-GWU/cookiecutter-pywf_open_source --checkout tags/0.1.2

You'll then be prompted to provide the following information:

.. code-block:: bash

    [1/10] Your Python package name, in snake case (e.g. my_package) (your_package_name): my_awesome_package
    [2/10] github_username (your_github_username): my_github_username
    [3/10] Pick an open source license for pyproject.toml file, see https://choosealicense.com/ for details
      1 - MIT
      2 - AGPL-3.0-or-later
      3 - Proprietary
      Choose from [1/2/3] (1): 1
    [4/10] Pick a license classifier, this has to match the previous one
      1 - License :: OSI Approved :: MIT License
      2 - License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)
      3 - License :: Other/Proprietary License
      Choose from [1/2/3] (1): 1
    [5/10] Author name for pyproject.toml file (Firstname Lastname): John Doe
    [6/10] Author email for pyproject.toml file (firstname.lastname@email.com): john.doe@email.com
    [7/10] Semantic Version, in {major}.{minor}.{micro} (e.g. 0.1.1) (0.1.1): 0.1.1
    [8/10] Python version for local development, in {major}.{minor}.{micro} (e.g. 3.11.8) (3.11.8): 3.11.8
    [9/11] GitHub token field, Read https://github.com/MacHu-GWU/home_secret-project to learn how to set up your GitHub token using home_secret.json (your_github_token_field): my_github_token
    [10/11] Codecov.io token field, Read https://github.com/MacHu-GWU/home_secret-project to learn how to set up your GitHub token using home_secret.json (your_codecov_token_field): my_codecov_token
    [11/11] Readthedocs.org token field, Read https://github.com/MacHu-GWU/home_secret-project to learn how to set up your GitHub token using home_secret.json (your_readthedocs_token_field): my_readthedocs_token

This will generate a repository structure similar to `cookiecutter_pywf_open_source_demo-project <https://github.com/MacHu-GWU/cookiecutter_pywf_open_source_demo-project>`_.


Variations
------------------------------------------------------------------------------
For my personal open source Python projects, I use a custom branch:

.. code-block:: bash

    cookiecutter https://github.com/MacHu-GWU/cookiecutter-pywf_open_source --checkout sanhe


Project Maintainer Note
------------------------------------------------------------------------------
this project follows the best practice mentioned in `THIS DOCUMENT <https://dev-exp-share.readthedocs.io/en/latest/search.html?q=Creating+Reusable+Project+Templates%3A+From+Concept+to+Implementation&check_keywords=yes&area=default>`_.

- **Seed Repository**: `cookiecutter_pywf_open_source_demo-project <https://github.com/MacHu-GWU/cookiecutter_pywf_open_source_demo-project>`_
- **Automation Library**: `pywf_open_source-project <https://github.com/MacHu-GWU/pywf_open_source-project>`_
- **Cookiecutter Template**: `cookiecutter-pywf_open_source <https://github.com/MacHu-GWU/cookiecutter-pywf_open_source>`_
