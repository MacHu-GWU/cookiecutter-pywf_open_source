# -*- coding: utf-8 -*-

from your_package_name import api


def test():
    _ = api


if __name__ == "__main__":
    from your_package_name.tests import run_cov_test

    run_cov_test(
        __file__,
        "your_package_name.api",
        preview=False,
    )
