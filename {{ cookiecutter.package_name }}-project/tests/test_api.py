# -*- coding: utf-8 -*-

from {{ cookiecutter.package_name }} import api


def test():
    _ = api


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.api",
        preview=False,
    )
