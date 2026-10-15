# -*- coding: utf-8 -*-

from {{ cookiecutter.package_name }} import api


def test():
    _ = api
    _ = api.DEFAULT_NAME
    _ = api.add_two
    _ = api.greet
    _ = api.Greeter
    _ = api.example_package_1
    _ = api.example_package_1.multi_two


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.api",
        preview=False,
    )
