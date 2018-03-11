#!/usr/bin/env python3
"""Defines :class:`Directive`."""


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
    """Parse a domain-spec."""
    # TODO
    return String(spec)


def parse_ip4_network(address: str) -> String:
    """Parse an ip4-network."""
    return String(address)


def parse_ip6_network(address: str) -> String:
    """Parse an ip6-network."""
    return String(address)


class Argument(typing.NamedTuple):  # pylint: disable=too-few-public-methods
    """Argument meta-data.

    Defines how arguments are parsed.
    """
    parse: typing.Callable[[str], Term]
    mandatory: bool


# TODO: refine
class DirectiveArgumentError(TermError):
    """Errors while parsing :class:`Directive` arguments."""
    def __init__(self, directive: 'Directive') -> None:
        """Create a :class:`DirectiveArgumentError`.

        `directive` is the :class:`Directive` in which this error occurs.
        """
        super().__init__(directive)


# FIXME: quite similar to Modifier; unify?
class Directive(Term):
    """A directive.

    The type of directive is stored in :attr:`name`.
    The potentially optional argument(s) are stored in :attr:`arg`.
    """
    DIRECTIVE_RE: typing.ClassVar[typing.Pattern[str]] = \
        re.compile(fr"({Term.NAME_PATTERN})(?:([:/])(.*))?")

    # arguments for the various directives
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
        """Create a :class:`Directive`.

        `match` is the match from :attr:`DIRECTIVE_RE`.
        """
        super().__init__(match.group(0))
        self.name = match.group(1)

        arg_type = self.ARGUMENTS.get(self.name, None)
        if arg_type is None:
            self._errors.append(UnknownDirectiveError(self))
            return

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
        """Try to parse a :class:`Directive` from `str`.

        `term` the string to parse.

        Returns `None` if the term doesn't look like a :class:`Directive`.
        """
        match = cls.DIRECTIVE_RE.fullmatch(term)
        return cls(match) if match else None

    @property
    def errors(self) -> typing.Iterable[ParsingError]:
        """Errors that occurred while parsing this :class:`Directive`."""
        if self.arg is not None:
            arg_errors = self.arg.errors
        else:
            arg_errors = iter(())
        return itertools.chain(super().errors, arg_errors)


if __debug__:
    def mod_name_checker() -> None:
        """Validate the directive names in :attr:`Directive.ARGUMENTS`."""
        mod_name = re.compile(Term.NAME_PATTERN)
        for directive in Directive.ARGUMENTS.keys():
            assert mod_name.fullmatch(directive), f"{directive} must match {mod_name.pattern}"
    mod_name_checker()
