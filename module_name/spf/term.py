#!/usr/bin/env python3
"""Defined :class:`Term`."""

import typing
from .error import ParsingError


class Term:
    """A single term in SPF."""
    errors: typing.List[ParsingError] = []
    # TODO: We might not need to store this,
    #       though in the presence of errors it could be difficult to guarantee
    #       that we can recreate the string.
    string: str

    def __init__(self, term: str) -> None:
        """Create a :class:`Term`."""
        self.string = term

    def __str__(self) -> str:
        """Return the `str` from which this :class:`Term` was parsed."""
        return self.string
