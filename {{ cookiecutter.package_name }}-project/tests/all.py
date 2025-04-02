# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from {{ cookiecutter.package_name }}.tests import run_cov_test

    run_cov_test(
        __file__,
        "{{ cookiecutter.package_name }}",
        is_folder=True,
        preview=False,
    )
