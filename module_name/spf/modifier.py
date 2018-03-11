#!/usr/bin/env python3
"""Defines :class:`Modifier`."""


import collections
import re
import typing
from .error import (
    ParsingError,
    TermError,
    UnknownModifierError,
)
from .term import Term


# TODO: refine
class ModifierArgumentError(TermError):
    def __init__(self, directive: 'Modifier') -> None:
        super().__init__(directive)


# FIXME: quite similar to Directive; unify?
class Modifier(Term):
    """Abstract modifier."""
    MODIFIER_RE: typing.ClassVar[typing.Pattern[str]] = re.compile(fr"({Term.NAME_PATTERN})=(.*)")

    MODIFIER_NAMES: typing.ClassVar[typing.FrozenSet[str]] = frozenset(('redirect', 'exp'))

    def __init__(self, match: typing.Match[str]) -> None:
        super().__init__(match.group(0))
        self.name = match.group(1)
        if self.name not in self.MODIFIER_NAMES:
            self._errors.append(ModifierArgumentError(self))
        self.arg = match.group(2)
        if not self.arg:
            self._errors.append(ModifierArgumentError(self))

    @classmethod
    def parse(cls, term: str) -> typing.Optional['Modifier']:
        match = cls.MODIFIER_RE.fullmatch(term)
        return cls(match) if match else None


if __debug__:
    def mod_name_checker() -> None:
        mod_name = re.compile(Term.NAME_PATTERN)
        for modifier in Modifier.MODIFIER_NAMES:
            assert mod_name.fullmatch(modifier), f"{modifier} must match {mod_name.pattern}"
    mod_name_checker()
