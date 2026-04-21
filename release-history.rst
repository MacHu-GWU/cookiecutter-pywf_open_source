.. _release_history:

Release and Version History
==============================================================================


Backlog (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


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
