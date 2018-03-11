#!/usr/bin/env python3
"""Defines :class:`Version`."""


import re
import typing
from .error import SPFVersionError
from .term import Term


class Version(Term):
    """An SPF version.

    Strictly speaking, this is not a term in RFC parlance,
    but it makes sense for us to treat it this way.
    """
    SPF_VERSION_RE: typing.ClassVar[typing.Pattern] = re.compile(r"v=spf1")

    def __init__(self, term: str) -> None:
        """Create a :class:`Version`.

        `term` is the version string.
        """
        super().__init__(term)
        match = self.SPF_VERSION_RE.fullmatch(term)
        if not match:
            self._errors.append(SPFVersionError(self))
