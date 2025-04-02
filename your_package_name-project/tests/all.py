# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from your_package_name.tests import run_cov_test

    run_cov_test(
        __file__,
        "your_package_name",
        is_folder=True,
        preview=False,
    )
