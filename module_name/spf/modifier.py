#!/usr/bin/env python3
"""Defines :class:`Modifier`."""


import re
import typing
from .error import (
    TermError,
    UnknownModifierError,
)
from .term import Term


# TODO: refine
class ModifierArgumentError(TermError):
    """Errors while parsing :class:`Modifier` arguments."""
    def __init__(self, directive: 'Modifier') -> None:
        super().__init__(directive)


# FIXME: quite similar to Directive; unify?
class Modifier(Term):
    """A modifier.

    The type of directive is stored in :attr:`name`.
    The argument is stored in :attr:`arg`.
    """
    MODIFIER_RE: typing.ClassVar[typing.Pattern[str]] = re.compile(fr"({Term.NAME_PATTERN})=(.*)")

    MODIFIER_NAMES: typing.ClassVar[typing.FrozenSet[str]] = frozenset(('redirect', 'exp'))

    def __init__(self, match: typing.Match[str]) -> None:
        """Create a :class:`Directive`.

        `match` is the match from :attr:`MODIFIER_RE`.
        """
        super().__init__(match.group(0))
        self.name = match.group(1)
        if self.name not in self.MODIFIER_NAMES:
            self._errors.append(UnknownModifierError(self))
        self.arg = match.group(2)
        if not self.arg:
            self._errors.append(ModifierArgumentError(self))

    @classmethod
    def parse(cls, term: str) -> typing.Optional['Modifier']:
        """Try to parse a :class:`Modifier` from `str`.

        `term` the string to parse.

        Returns `None` if the term doesn't look like a :class:`Modifier`.
        """
        match = cls.MODIFIER_RE.fullmatch(term)
        return cls(match) if match else None


if __debug__:
    def mod_name_checker() -> None:
        """Validate the entries in :attr:`Modifier.MODIFIER_NAMES`."""
        mod_name = re.compile(Term.NAME_PATTERN)
        for modifier in Modifier.MODIFIER_NAMES:
            assert mod_name.fullmatch(modifier), f"{modifier} must match {mod_name.pattern}"
    mod_name_checker()
