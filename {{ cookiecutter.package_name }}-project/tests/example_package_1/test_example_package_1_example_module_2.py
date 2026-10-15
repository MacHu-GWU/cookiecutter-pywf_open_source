# -*- coding: utf-8 -*-

from {{ cookiecutter.package_name }}.example_package_1.example_module_2 import (
    multi_two,
)


def test_multi_two():
    assert multi_two(2, 3) == 6


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.example_package_1.example_module_2",
        preview=False,
    )
