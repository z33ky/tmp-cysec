#!/usr/bin/env python3
"""Defines :class:`Spacing`."""


from .term import Term


class Spacing(Term):
    """Space characters.

    This isn't really a term, but it makes handling easier for us.
    Storing this allows us to re-create the original SPF string 1:1.
    """
    def __init__(self, space: str) -> None:
        """Create a :class:`Spacing`.

        `space` is the spacing string.
        """
        assert space.isspace()
        super().__init__(space)
