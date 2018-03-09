#!/usr/bin/env python3
"""Defines :class:`Modifier`."""


import collections
import re
import typing
from .error import UnknownModifierError
from .term import Term


# FIXME: quite similar to Directive; unify?
class Modifier(Term):
    """Abstract modifier."""
    MODIFIER_RE: typing.ClassVar[typing.Pattern[str]] = re.compile(fr"({Term.NAME_PATTERN})=(.*)")

    HANDLERS: typing.ClassVar[typing.DefaultDict[str, typing.Type['Modifier']]]

    def __init__(self, match: typing.Match[str]) -> None:
        super().__init__(match.group(0))
        self.arg = match.group(2)

    @classmethod
    def parse(cls, term: str) -> typing.Optional['Modifier']:
        match = cls.MODIFIER_RE.fullmatch(term)
        if not match:
            return None

        name = match.group(1)
        return cls.HANDLERS[name](match)


class Redirect(Modifier):
    """"redirect" modifier."""
    pass


class Explanation(Modifier):
    """"exp" modifier."""
    pass


class Unknown(Modifier):
    """An unknown modifier."""
    def __init__(self, match: typing.Match[str]) -> None:
        super().__init__(match)
        self._errors.append(UnknownModifierError(self))


Modifier.HANDLERS = collections.defaultdict(lambda: Unknown,
                                            redirect=Redirect,
                                            exp=Explanation,
                                           )


if __debug__:
    def mod_name_checker() -> None:
        mod_name = re.compile(Term.NAME_PATTERN)
        for modifier in Modifier.HANDLERS.keys():
            assert mod_name.fullmatch(modifier), f"{modifier} must match {mod_name.pattern}"
    mod_name_checker()
