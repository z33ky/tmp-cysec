#!/usr/bin/env python3
"""Defines :class:`Directive`."""


import itertools
import re
import typing
from module_name.request_context import RequestContext
from .error import (
    ParsingError,
    TermError,
    UnknownDirectiveError,
)
from .macro_string import MacroString
from .string import String
from .term import Term
from .cidr_length import (
    CidrLengths,
    IP4CidrLengthParser,
    IP6CidrLengthParser,
    DualCidrLengthParser,
)


def parse_domain_spec_and_cidr_length(ctx: RequestContext, spec: str) -> typing.Sequence[Term]:
    """Parse a domain-spec and cidr-length.

    Both are optionally present.
    """
    # FIXME: no "/" in domain-spec, yes?
    spec, *cidr = spec.split("/", 1)
    terms = []
    if spec:
        terms = terms.append(MacroString(ctx, spec))
    if cidr:
        assert len(cidr) == 1
        terms.append(IP4CidrLengthParser.parse("/" + cidr[0]))
    # FIXME: this will parse "a:" the same way as "a/", i.e. both as a domain-spec,
    #        though the latter is a cidr-length
    return terms or [MacroString(ctx, "")]


def parse_domain_spec(ctx: RequestContext, spec: str) -> typing.Sequence[MacroString]:
    """Parse a domain-spec."""
    return [MacroString(ctx, spec)]


def parse_ip4_network(_ctx: RequestContext, address: str) -> typing.Sequence[String]:
    """Parse an ip4-network."""
    return [String(address)]


def parse_ip6_network(_ctx: RequestContext, address: str) -> typing.Sequence[String]:
    """Parse an ip6-network."""
    return [String(address)]


def parse_dual_cidr_length(_ctx: RequestContext, cidr: str) -> typing.Sequence[CidrLengths]:
    return [DualCidrLengthParser.parse(cidr)]


def parse_ip4_cidr_length(_ctx: RequestContext, cidr: str) -> typing.Sequence[CidrLengths]:
    return [IP4CidrLengthParser.parse(cidr)]


def parse_ip6_cidr_length(_ctx: RequestContext, cidr: str) -> typing.Sequence[CidrLengths]:
    return [IP6CidrLengthParser.parse(cidr)]


class Argument(typing.NamedTuple):  # pylint: disable=too-few-public-methods
    """Argument meta-data.

    Defines how arguments are parsed.
    """
    parse: typing.Callable[[RequestContext, str], typing.Sequence[Term]]
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
        'a': Argument(parse_domain_spec_and_cidr_length, False),
        'mx': Argument(parse_domain_spec_and_cidr_length, False),
        'ptr': Argument(parse_domain_spec, False),
        'ip4': Argument(parse_ip4_cidr_length, True),
        'ip6': Argument(parse_ip6_cidr_length, True),
        'exist': Argument(parse_domain_spec, True),
    }
    # TODO: domains with trailing dots SHOULD NOT be published (section 7.3)

    arg: typing.Sequence[Term] = []

    def __init__(self, ctx: RequestContext, match: typing.Match[str]) -> None:
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
            self.arg = arg_type.parse(ctx, arg)

    @classmethod
    def parse(cls, ctx: RequestContext, term: str) -> typing.Optional['Directive']:
        """Try to parse a :class:`Directive` from `str`.

        `term` the string to parse.

        Returns `None` if the term doesn't look like a :class:`Directive`.
        """
        match = cls.DIRECTIVE_RE.fullmatch(term)
        return cls(ctx, match) if match else None

    @property
    def errors(self) -> typing.Iterable[ParsingError]:
        """Errors that occurred while parsing this :class:`Directive`."""
        if self.arg:
            arg_errors = (arg.errors for arg in self.arg)
        else:
            arg_errors = ()  # iter(())
        return itertools.chain(super().errors, *arg_errors)


if __debug__:
    def mod_name_checker() -> None:
        """Validate the directive names in :attr:`Directive.ARGUMENTS`."""
        mod_name = re.compile(Term.NAME_PATTERN)
        for directive in Directive.ARGUMENTS.keys():
            assert mod_name.fullmatch(directive), f"{directive} must match {mod_name.pattern}"
    mod_name_checker()
