# -*- coding: utf-8 -*-

"""
Reject inputs the generated project cannot work with, before anything is written.
"""

import sys

# The generated project pins requires-python, its classifiers and its CI matrix
# to these versions; mise.toml must use one of them.
SUPPORTED_PYTHON_VERSIONS = ["3.11", "3.12", "3.13", "3.14"]

dev_python_version = "{{ cookiecutter.dev_python_version }}"

if dev_python_version not in SUPPORTED_PYTHON_VERSIONS:
    print(
        f"ERROR: dev_python_version must be one of "
        f"{', '.join(SUPPORTED_PYTHON_VERSIONS)}, got {dev_python_version!r}."
    )
    sys.exit(1)
