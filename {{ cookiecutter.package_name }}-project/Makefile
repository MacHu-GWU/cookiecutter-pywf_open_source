# -*- coding: utf-8 -*-

help: ## ** Show this help message
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'


venv-create: ## ** Create Virtual Environment
	~/.pyenv/shims/python ./bin/s01_1_venv_create.py


venv-remove: ## ** Remove Virtual Environment
	~/.pyenv/shims/python ./bin/s01_2_venv_remove.py


poetry-lock: ## Resolve dependencies using poetry, update poetry.lock file
	~/.pyenv/shims/python ./bin/s02_0_poetry_lock.py


install-root: ## Install Package itself without any dependencies
	~/.pyenv/shims/python ./bin/s02_1_install_only_root.py


install: ## ** Install main dependencies and Package itself
	~/.pyenv/shims/python ./bin/s02_2_install.py


install-dev: ## Install Development Dependencies
	~/.pyenv/shims/python ./bin/s02_3_install_dev.py


install-test: ## Install Test Dependencies
	~/.pyenv/shims/python ./bin/s02_4_install_test.py


install-doc: ## Install Document Dependencies
	~/.pyenv/shims/python ./bin/s02_5_install_doc.py


install-automation: ## Install Dependencies for Automation Script
	~/.pyenv/shims/python ./bin/s02_6_install_automation.py


install-all: ## Install All Dependencies
	~/.pyenv/shims/python ./bin/s02_7_install_all.py


poetry-export: ## Export dependencies to requirements.txt
	~/.pyenv/shims/python ./bin/s02_8_poetry_export.py


test: install install-test test-only ## ** Run test


test-only: ## Run test without checking test dependencies
	~/.pyenv/shims/python ./bin/s03_1_run_unit_test.py


cov: install install-test cov-only ## ** Run code coverage test


cov-only: ## Run code coverage test without checking test dependencies
	~/.pyenv/shims/python ./bin/s03_2_run_cov_test.py


int: install install-test int-only ## ** Run integration test


int-only: ## Run integration test without checking test dependencies
	~/.pyenv/shims/python ./bin/s03_3_run_int_test.py


view-cov: ## View code coverage test report
	~/.pyenv/shims/python ./bin/s03_3_view_cov_result.py


build-doc: install install-doc ## Build documentation website locally
	~/.pyenv/shims/python ./bin/s04_1_build_doc.py


view-doc: ## View documentation website locally
	~/.pyenv/shims/python ./bin/s04_2_view_doc.py


nb-to-md: ## Convert Notebook to Markdown
	~/.pyenv/shims/python ./bin/s04_3_nb_to_md.py


build: ## Build Python library distribution package
	~/.pyenv/shims/python ./bin/s05_1_build_package.py


publish: build ## Publish Python library to Public PyPI
	~/.pyenv/shims/python ./bin/s05_2_publish_package.py


release: ## Create Github Release using current version
	~/.pyenv/shims/python ./bin/s05_3_create_release.py


setup-codecov: ## Setup Codecov Upload token in GitHub Action Secrets
	~/.pyenv/shims/python ./bin/s06_1_setup_codecov.py


setup-rtd: ## Create ReadTheDocs Project
	~/.pyenv/shims/python ./bin/s06_2_setup_readthedocs.py
