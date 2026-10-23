.. _release_history:

Release and Version History
==============================================================================


Backlog (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


3.0.2 (2026-10-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Seed repo changes: `3.0.2 (2026-10-23) <https://github.com/MacHu-GWU/cookiecutter_pywf_open_source_demo-project/blob/3.0.2/release-history-seed-repo.rst#302-2026-10-23>`__

**Minor Improvements**

- ``mise run check-version`` (run by ``mise run sync``) now also checks that links pinned to the seed's own version tag point at the current version, so a version bump cannot leave stale links behind. The files to check are listed in the new ``SEED_VERSION_PIN_FILES`` of the parameterization script (empty for now)

**Miscellaneous**

- The seed release instructions (the cctpl skills and the ``check-release`` message) now say to push the seed first and then run the seed's own release task(s); publishing the seed to PyPI is only part of that step when the seed is published there


3.0.1 (2026-10-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Seed repo changes: `3.0.1 (2026-10-23) <https://github.com/MacHu-GWU/cookiecutter_pywf_open_source_demo-project/blob/3.0.1/release-history-seed-repo.rst#301-2026-10-23>`__

The first template release with the shared version. There is no template ``3.0.0``: the seed's ``3.0.0`` tag was created before its changes were pushed, so the seed was released again as ``3.0.1``. The seed changelog's ``3.0.0`` section, on the same page, lists everything a generated project gets.

**Features and Improvements**

- The template and its seed repo now share one version number, so a template version also names the seed state it was generated from. The version jumps from ``2.1.0`` to ``3.0.1`` for this reason only: generating a project works exactly as with ``2.1.0``, and no variable changed
- Every release entry in this file now starts with a link to the seed repo's own changelog (``release-history-seed-repo.rst``) at the seed's tag of the same version, which lists what newly generated projects get

**Minor Improvements**

- A published version is never overwritten: ``mise run publish-template`` creates the tag and the GitHub release in one step, refuses a version that already has a tag, and links the release to its changelog entry
- New ``mise run publish-presets`` regenerates the ``preset/*`` branches from the pushed ``main``; ``publish-template`` runs it last, and it can be rerun alone, for example after changing only ``presets/*.json``
- The seed's tag of the same version records which seed commit a template version was built from; changelog entries no longer carry a ``Built from seed`` commit
- New ``mise run check-release``: before anything is pushed, checks the version is the same in the seed and in this repo, the template is current, the seed is pushed and tagged, and the changelog entry starts with the seed link
- New ``mise run check-version``, run by ``mise run sync``: the seed version is valid, documented in the seed's changelog, and never recorded in the template's own ``release-history.rst``
- New ``mise run e2e``: ``sync`` followed by ``try-template``, one command from the seed to a tested generated project

**Miscellaneous**

- ``mise run sync`` copies the seed version into this repo's ``pyproject.toml`` and ``uv.lock``; the version is never edited here
- New ``cctpl-changelog-cn`` skill writes this file, replacing ``py-changelog``; the cctpl skills describe the shared version, the seed-only files, and the new release order


2.1.0 (2026-10-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Generated projects now support a **maintainer skill family** (``maintain-<package_name>-base`` plus one invoker per repeatable job) that records the library's own architecture, invariants, design decisions, debugging recipes, and maintenance jobs, so agents (and contributors) maintaining the repo load them instead of reading a maintainer guide in the docs
- New ``pywf-oss-write-maintain-skill`` skill creates and updates that family from the code, asking before it writes a new family
- New ``18-knowledge-channels.md`` reference: which fact goes to which of the three channels (Sphinx user docs, the ``pypi-<package_name>`` API skill, the ``maintain-<package_name>`` skills)
- The generated ``CLAUDE.md`` points to the maintenance skills and says knowledge is written for agents too, never as a maintainer guide in the docs

**Minor Improvements**

- ``update_skill_index.py`` can regenerate the References index of any base skill (``--skill_dir``), and ``check_skill_family.py`` can check the maintenance family (``--prefix <maintain_prefix>``)
- ``pywf-oss-write-doc`` and related skills now describe user docs only, and hand API and maintenance knowledge to the matching skill

**Miscellaneous**

- Renumbered the ``pywf-oss-base`` references from ``18`` onward (GitHub Actions is now ``19``, through Skill Family Workflow at ``27``) to make room for the new reference


2.0.0 (2026-10-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Built from seed @ ``e988252``

**Breaking Changes**

- Removed the ``license_classifier`` variable. The generated ``pyproject.toml`` now uses an SPDX ``license`` expression (PEP 639) derived from ``license``, so drop ``license_classifier`` from any ``--extra-context`` or replay file
- The ``license`` choice ``Proprietary`` is now ``LicenseRef-Proprietary``, the valid SPDX expression written to ``pyproject.toml`` (``Proprietary`` made the generated project fail to build). Update any ``--extra-context`` or replay file that uses ``license=Proprietary``
- Generated projects now require Python 3.11+ (``requires-python = ">=3.11,<4.0"``); Python 3.10 is no longer supported

**Features and Improvements**

- New variable ``pypi_token_field`` (with a default): the generated ``mise.toml`` reads the PyPI token from ``home_secret.toml`` under this field instead of a hard-coded path
- Generated projects ship a ``pywf-oss-*`` Claude Code skill family (add module, write test, write doc, changelog, release, audit, fix CI, setup machine / repo, upgrade deps, write PyPI skill, add community skill), backed by shared references and checker scripts; it replaces the old ``py-changelog`` and ``write-agent-skill`` skills
- New ``mise run format`` and ``mise run lint`` tasks (ruff, plus a one-import-per-line check)
- Sample code and tests: ``example_module_1``, ``example_package_1`` exposed through ``api.py``, with matching tests and API reference pages
- Docs: new sphinx-design gallery page, expanded reStructuredText and notebook samples showing public imports and cross-references, and a ``.claude/launch.json`` to preview the built HTML docs on port 8765
- Clearer cookiecutter prompts, including a prompt for ``github_username``; token prompts now refer to ``home_secret.toml``

**Minor Improvements**

- mise tasks that do not need credentials now run even when a secret cannot be read (missing secrets become empty strings)
- uv and Read the Docs both use the mise-managed Python, so the docs Python version is set in one place (``mise.toml``)
- CI: upgraded GitHub Actions, cache key now uses the full resolved Python version to avoid stale caches, updated Codecov input
- Removed the ``01-Project-Overview`` and ``99-Maintainer-Guide`` sample doc pages; ``cli.py`` is excluded from generated API docs

**Miscellaneous**

- Dependency updates: pytest 9, ``httpx`` replaced with ``httpx2`` in the mise extra, newer Sphinx / Furo / nbsphinx bounds (Sphinx kept below 9)
- ``uv.lock`` is no longer shipped in the template; it is created on first ``uv`` run
- Template maintenance moved to the cctpl 2.0 workflow; ``preset/*`` branches (e.g. ``preset/sanhe``) are now regenerated from ``main`` plus ``presets/*.json`` on every release


1.0.4 (2026-04-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Added ``py-changelog`` Claude Code skill: automates updating ``release-history.rst`` before publishing a new version, driven by git history
- Added ``write-agent-skill`` Claude Code skill + reference doc (``extend-claude-with-skills.md``) to guide authoring new agent skills

**Miscellaneous**

- Updated ``uv.lock`` dependencies to latest versions


1.0.3 (2026-04-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Added ``write-agent-skill`` Claude Code skill scaffold (initial version, later extended in 1.0.4)
- Added ``01-Project-Overview`` Sphinx documentation section and ``99-Maintainer-Guide`` entry
- ``build-doc`` mise task now cleans ``docs/build`` before rebuilding to avoid stale output

**Miscellaneous**

- Updated ``uv.lock`` dependencies to latest versions


1.0.2 (2026-04-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- AI-first template: Claude Code takes over as the primary development assistant
- All tooling managed by ``mise``: Python, uv, and Claude are all ``mise``-managed
- Replaced ``make`` with ``mise tasks`` for all automation; no longer depends on ``pywf_open_source`` library for shell command wrapping
- Upgraded all dependencies to latest versions
- Updated GitHub Actions workflows to latest versions as of 2026-01


0.1.1 (2025-04-02)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First Release
- Use ``pywf_open_source as the automation engine
