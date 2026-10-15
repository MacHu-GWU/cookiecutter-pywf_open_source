# -*- coding: utf-8 -*-

"""
Data passed to the ``.. jinja:: doc_data`` directive in the docs
(see ``jinja_contexts`` in ``docs/source/conf.py``).
"""

from .. import api

#: One row per public name of ``api.py``: the name and the first line of its docstring.
public_api = [
    {
        "name": name,
        "summary": (getattr(api, name).__doc__ or "").strip().splitlines()[0],
    }
    for name in ["add_two", "greet", "Greeter"]
]

doc_data = {
    "public_api": public_api,
}
