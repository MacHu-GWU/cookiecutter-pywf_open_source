.. _sample-sphinx-design-gallery:

Sample Sphinx Design Gallery
==============================================================================
Every `sphinx-design <https://sphinx-design.readthedocs.io/>`_ widget this template uses, each with the pattern it is good for. Read it next to its source, ``docs/source/03-Sample-Sphinx-Design-Gallery/index.rst``, and copy what you need.


Grid of Cards
------------------------------------------------------------------------------
For landing pages and "what's in this section" overviews. Each card is clickable as a whole.

.. grid:: 1 2 2 3
    :gutter: 3

    .. grid-item-card:: :octicon:`rocket;1.5em;sd-text-primary` Quick Start
        :link: sample-rst-document
        :link-type: ref

        Every reStructuredText feature, on one page.

    .. grid-item-card:: :octicon:`book;1.5em;sd-text-info` Notebook Guide
        :link: sample-jupyter-notebook-document
        :link-type: ref

        Docs written as runnable Jupyter notebooks.

    .. grid-item-card:: :octicon:`code;1.5em;sd-text-success` API Reference
        :link: /api/{{ cookiecutter.package_name }}/__init__
        :link-type: doc

        Every public class and function.


Card with Header and Footer
------------------------------------------------------------------------------
.. card:: Greeter
    :shadow: md

    Header text
    ^^^
    Body: greets people with a configurable word.
    +++
    Footer: see :class:`~{{ cookiecutter.package_name }}.example_module_1.Greeter`.


Tabs
------------------------------------------------------------------------------
For alternatives the reader chooses between. Tabs with the same ``:sync:`` key switch together: pick ``uv`` in one set and the next set follows.

.. tab-set::

    .. tab-item:: pip
        :sync: pip

        .. code-block:: bash

            pip install {{ cookiecutter.package_name | slugify }}

    .. tab-item:: uv
        :sync: uv

        .. code-block:: bash

            uv add {{ cookiecutter.package_name | slugify }}

.. tab-set::

    .. tab-item:: pip
        :sync: pip

        .. code-block:: bash

            pip install --upgrade {{ cookiecutter.package_name | slugify }}

    .. tab-item:: uv
        :sync: uv

        .. code-block:: bash

            uv lock --upgrade-package {{ cookiecutter.package_name | slugify }}


Code Tabs
------------------------------------------------------------------------------
The same thing in several languages; each tab is labeled with its language.

.. tab-set-code::

    .. code-block:: python

        from {{ cookiecutter.package_name }}.api import greet

        greet("Alice")

    .. code-block:: bash

        python -c 'from {{ cookiecutter.package_name }}.api import greet; print(greet("Alice"))'


Dropdowns
------------------------------------------------------------------------------
For FAQs, troubleshooting, and long or optional detail.

.. dropdown:: Why does the test file name repeat the folder path?
    :icon: question
    :color: info

    pytest needs unique test module basenames: ``tests/a/test_api.py`` and ``tests/b/test_api.py`` would collide.

.. dropdown:: This one starts open
    :icon: light-bulb
    :color: success
    :open:

    Add ``:open:`` to expand a dropdown by default.


Badges
------------------------------------------------------------------------------
:bdg-success:`stable` :bdg-warning:`beta` :bdg-danger:`deprecated` :bdg-secondary-line:`optional`
:bdg-link-primary:`PyPI <https://pypi.org/project/{{ cookiecutter.package_name | slugify }}/>`
:bdg-ref-info:`see the rst sample <sample-rst-document>`

Badges in a support matrix:

.. list-table::
    :header-rows: 1

    * - Python
      - Ubuntu
      - Windows
    * - 3.11
      - :bdg-success:`tested`
      - :bdg-success:`tested`
    * - 3.14
      - :bdg-success:`tested`
      - :bdg-warning:`beta`


Buttons
------------------------------------------------------------------------------
One clear call to action, usually at the end of a guide.

.. button-ref:: sample-rst-document
    :ref-type: ref
    :color: primary
    :shadow:

    Get Started

.. button-link:: https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.package_name }}-project
    :color: secondary
    :outline:

    :octicon:`mark-github` Source


Icons
------------------------------------------------------------------------------
:octicon:`check-circle;1em;sd-text-success` done,
:octicon:`alert;1em;sd-text-warning` careful,
:material-regular:`rocket_launch;1.2em;sd-text-primary` launch.
