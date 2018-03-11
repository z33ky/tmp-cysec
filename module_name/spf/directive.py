#!/usr/bin/env python3
"""Defines :class:`Directive`."""


import collections
import itertools
import re
import typing
from .error import (
    ParsingError,
    TermError,
    UnknownDirectiveError,
)
from .string import String
from .term import Term
from .cidr_length import (
    IP4CidrLengthParser,
    IP6CidrLengthParser,
    DualCidrLengthParser,
)


def parse_domain_spec(spec: str) -> String:
    # TODO
    return String(spec)


def parse_ip4_address(address: str) -> String:
    # TODO
    return String(address)


def parse_ip6_address(address: str) -> String:
    # TODO
    return String(address)


class Argument(typing.NamedTuple):
    parse: typing.Callable[[str], Term]
    mandatory: bool


# TODO: refine
class DirectiveArgumentError(TermError):
    def __init__(self, directive: 'Directive') -> None:
        super().__init__(directive)


# FIXME: quite similar to Modifier; unify?
class Directive(Term):
    """Abstract directive."""
    DIRECTIVE_RE: typing.ClassVar[typing.Pattern[str]] = \
            re.compile(fr"({Term.NAME_PATTERN})(?:([:/])(.*))?")

    ARGUMENTS: typing.Mapping[str, typing.Optional[Argument]] = {
        'all': None,
        'include': Argument(parse_domain_spec, True),
        'a': Argument(DualCidrLengthParser.parse, False),
        'mx': Argument(DualCidrLengthParser.parse, False),
        'ptr': Argument(parse_domain_spec, False),
        'ip4': Argument(IP4CidrLengthParser.parse, True),
        'ip6': Argument(IP6CidrLengthParser.parse, True),
        'exist': Argument(parse_domain_spec, True),
    }

    arg: typing.Optional[Term] = None

    def __init__(self, match: typing.Match[str]) -> None:
        super().__init__(match.group(0))
        self.name = match.group(1)
        arg_type = self.ARGUMENTS.get(self.name, None)
        if arg_type is None:
            self._errors.append(UnknownDirectiveError(self))
        else:
            arg_delim, arg = match.group(2, 3)
            if bool(arg) is not bool(arg_delim):
                self._errors.append(DirectiveArgumentError(self))
            elif arg_type is None:
                if arg:
                    self._errors.append(DirectiveArgumentError(self))
            elif not arg:
                if arg_type.mandatory:
                    self._errors.append(DirectiveArgumentError(self))
            else:
                # TODO: check arg_delim
                self.arg = arg_type.parse(arg)

    @classmethod
    def parse(cls, term: str) -> typing.Optional['Directive']:
        match = cls.DIRECTIVE_RE.fullmatch(term)
        return cls(match) if match else None

    @property
    def errors(self) -> typing.Iterable[ParsingError]:
        if self.arg is not None:
            arg_errors = self.arg.errors
        else:
            arg_errors = iter(())
        return itertools.chain(super().errors, arg_errors)


if __debug__:
    def mod_name_checker() -> None:
        mod_name = re.compile(Term.NAME_PATTERN)
        for directive in Directive.ARGUMENTS.keys():
            assert mod_name.fullmatch(directive), f"{directive} must match {mod_name.pattern}"
    mod_name_checker()
