#!/usr/bin/env python3
"""Defines :class:`Directive`."""


import collections
import re
import typing
from .error import UnknownDirectiveError
from .term import Term


# FIXME: quite similar to Modifier; unify?
class Directive(Term):
    """Abstract directive."""
    DIRECTIVE_RE: typing.ClassVar[typing.Pattern[str]] = \
        re.compile(fr"({Term.NAME_PATTERN})(?::(.*))?")

    HANDLERS: typing.ClassVar[typing.DefaultDict[str, typing.Type['Directive']]]

    def __init__(self, match: typing.Match[str]) -> None:
        super().__init__(match.group(0))
        self.arg = match.group(2)

    @classmethod
    def parse(cls, term: str) -> typing.Optional['Directive']:
        match = cls.DIRECTIVE_RE.fullmatch(term)
        if not match:
            return None

        name = match.group(1)
        return cls.HANDLERS[name](match)


class All(Directive):
    """"all" directive."""
    pass


class Include(Directive):
    """"include" directive."""
    pass


class Address(Directive):
    """"a" directive."""
    pass


class MailExchange(Directive):
    """"mx" directive."""
    pass


class Pointer(Directive):
    """"ptr" directive."""
    pass


class IP4Address(Directive):
    """"ip4" directive."""
    pass


class IP6Address(Directive):
    """"ip6" directive."""
    pass


class Exists(Directive):
    """"exists" directive."""
    pass


class Unknown(Directive):
    """An unknown directive."""
    def __init__(self, match: typing.Match[str]) -> None:
        super().__init__(match)
        self._errors.append(UnknownDirectiveError(self))


Directive.HANDLERS = collections.defaultdict(lambda: Unknown,
                                             all=All,
                                             include=Include,
                                             a=Address,
                                             mx=MailExchange,
                                             ptr=Pointer,
                                             ip4=IP4Address,
                                             ip6=IP6Address,
                                             exists=Exists,
                                            )


if __debug__:
    def mod_name_checker() -> None:
        mod_name = re.compile(Term.NAME_PATTERN)
        for directive in Directive.HANDLERS.keys():
            assert mod_name.fullmatch(directive), f"{directive} must match {mod_name.pattern}"
    mod_name_checker()
