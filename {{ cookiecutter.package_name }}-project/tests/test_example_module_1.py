# -*- coding: utf-8 -*-

from {{ cookiecutter.package_name }}.example_module_1 import DEFAULT_NAME
from {{ cookiecutter.package_name }}.example_module_1 import add_two
from {{ cookiecutter.package_name }}.example_module_1 import greet
from {{ cookiecutter.package_name }}.example_module_1 import Greeter

import pytest


def test_add_two():
    assert add_two(1, 2) == 3


def test_greet():
    assert greet() == f"Hello {DEFAULT_NAME}!"
    assert greet("Alice") == "Hello Alice!"


class TestGreeter:
    def test_greet(self):
        assert Greeter().greet("Bob") == "Hello Bob!"
        assert Greeter(greeting="Hi", punctuation=".").greet() == "Hi World."

    def test_greet_empty_name(self):
        with pytest.raises(ValueError):
            Greeter().greet("")


if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}.example_module_1",
        preview=False,
    )
