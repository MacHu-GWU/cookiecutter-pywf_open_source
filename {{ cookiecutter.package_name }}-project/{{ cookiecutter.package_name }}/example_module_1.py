# -*- coding: utf-8 -*-

"""
Example module used by the sample docs pages to demonstrate every kind of
cross-reference target: a constant, a function, a class, a method, and an
attribute.
"""

from __future__ import annotations

import dataclasses

#: Name used by :func:`greet` and :class:`Greeter` when no name is given.
DEFAULT_NAME = "World"


def add_two(a: int, b: int) -> int:
    """
    Return the sum of ``a`` and ``b``.
    """
    return a + b


def greet(name: str = DEFAULT_NAME) -> str:
    """
    Return a greeting for ``name``.

    :param name: who to greet; defaults to :attr:`DEFAULT_NAME`.
    """
    return f"Hello {name}!"


@dataclasses.dataclass
class Greeter:
    """
    Greets people with a configurable greeting word.

    Fields are kept one per line, fenced by ``# fmt: off`` / ``# fmt: on``.
    The trailing ``#:`` comment documents a field, so it can be cross-referenced
    with ``:attr:``.
    """

    # fmt: off
    greeting: str = dataclasses.field(default="Hello")  #: Word put in front of the name, such as ``"Hello"`` or ``"Hi"``.
    punctuation: str = dataclasses.field(default="!")  #: Mark put at the end of the greeting, such as ``"!"`` or ``"."``.
    # fmt: on

    def greet(self, name: str = DEFAULT_NAME) -> str:
        """
        Return the greeting for ``name``.

        :raises ValueError: if ``name`` is empty.
        """
        if not name:
            raise ValueError("name must not be empty")
        return f"{self.greeting} {name}{self.punctuation}"
