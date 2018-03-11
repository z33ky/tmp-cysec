#!/usr/bin/env python3
"""Defines :class:`SPF`."""

import itertools
import typing
from .error import ParsingError
from .term import Term


class SPF:
    """An SPF policy."""
    def __init__(self, terms: typing.List[Term]) -> None:
        """Create a :class:`SPF`.

        `terms` the list of terms that this policy has.
        """
        self.terms = terms

    def __str__(self) -> str:
        """Conversion to `str`.

        Joins the `str`-representations of all terms in :attr:`terms`.
        """
        return "".join(map(str, self.terms))

    @property
    def errors(self) -> typing.Iterator[ParsingError]:
        """Retrieve an iterator over the :class:`ParsingErrors <.error.ParsingError>`.

        The iterator will iterate over the errors of each term in :attr:`terms`.
        """
        return itertools.chain(*(term.errors for term in self.terms))
