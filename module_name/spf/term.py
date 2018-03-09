#!/usr/bin/env python3
"""Defined :class:`Term`."""

import re
import typing
from .error import (ParsingError, UnknownTermError)


class Term:
    """A single term in SPF."""
    # note: the spec doesn't define an "unknown directive",
    # so we just match the same characters as for "unknown modifier" for this NAME_PATTERN
    NAME_PATTERN: typing.ClassVar[str] = "[a-zA-Z][a-zA-Z0-9-_.]*"

    # FIXME: RFC5234 space separation
    #        version *( 1*SP term ) *SP
    TERM_RE: typing.ClassVar[typing.Pattern[str]] = re.compile(r"([^ ]+)([ ]*)")

    # s/ParsingError/TermError/?
    _errors: typing.List[ParsingError]

    # TODO: We might not need to store this,
    #       though in the presence of errors it could be difficult to guarantee
    #       that we can recreate the string.
    string: str

    def __init__(self, term: str) -> None:
        """Create a :class:`Term`."""
        self.string = term
        self._errors = []

    def __str__(self) -> str:
        """Return the `str` from which this :class:`Term` was parsed."""
        return self.string

    @property
    def errors(self) -> typing.Iterable[ParsingError]:
        return self._errors


class UnknownTerm(Term):
    """An unknown term."""
    def __init__(self, term: str) -> None:
        super().__init__(term)
        self._errors.append(UnknownTermError(self))
