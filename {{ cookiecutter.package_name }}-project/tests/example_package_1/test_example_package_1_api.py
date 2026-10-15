# -*- coding: utf-8 -*-

from {{ cookiecutter.package_name }}.example_package_1 import api


def test():
    _ = api
    _ = api.multi_two


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.example_package_1.api",
        preview=False,
    )
