#!/usr/bin/env python3
"""cidr-length parser."""

import re
import typing
from module_name.parsing_string import ParsingString
from .directive import Directive
from .error import (
    SPFVersionError,
    UnknownDirectiveError,
    UnknownModifierError,
    UnknownTermError,
)
from .modifier import Modifier
from .spf import SPF


ModifierHandler = typing.Callable[[ParsingString, str], Modifier]
DirectiveHandler = typing.Callable[[ParsingString, str], Directive]


class Parser():
    """Parser of a SPF string."""
    # TODO: ClassVar
    # FIXME: RFC5234 space separation
    #        version *( 1*SP term ) *SP
    TERM_RE = re.compile(r"([^ ]+)[ ]*")
    SPF_VERSION_RE = re.compile(r"v=spf1")

    MODIFIER_HANDLERS: typing.Mapping[str, ModifierHandler] = {
        'redirect': lambda view, arg: Modifier("redirect", arg),
        'exp': lambda view, arg: Modifier("exp", arg),
    }

    DIRECTIVE_HANDLERS: typing.Mapping[str, DirectiveHandler] = {
        'all': lambda view, arg: Directive("all", arg),
        'include': lambda view, arg: Directive("include", arg),
        'a': lambda view, arg: Directive("a", arg),
        'mx': lambda view, arg: Directive("mx", arg),
        'ptr': lambda view, arg: Directive("ptr", arg),
        'ip4': lambda view, arg: Directive("ip4", arg),
        'ip6': lambda view, arg: Directive("ip6", arg),
        'exists': lambda view, arg: Directive("exists", arg),
    }

    # note: the spec doesn't define an "unknown directive",
    # so we just also match the same characters as for "unknown modifier"
    MOD_NAME = "[a-zA-Z][a-zA-Z0-9-_.]*"
    DIRECTIVE_RE = re.compile(fr"({MOD_NAME})(?::(.*))?")
    MODIFIER_RE = re.compile(fr"({MOD_NAME})=(.*)")

    def parse(self, spf_string: str) -> SPF:
        view = ParsingString(spf_string)

        # strictly speaking, version|term
        def next_term_gen() -> typing.Generator[typing.Tuple[ParsingString, str], None, None]:
            match = self.TERM_RE.match(str(view))
            while match:
                yield view, match.group(1)
                view.advance(len(match.group(0)))
                match = self.TERM_RE.match(str(view))

        next_term = next_term_gen()
        # FIXME: GeneratorStop
        view, term = next(next_term)
        match = self.SPF_VERSION_RE.fullmatch(term)
        if not match:
            raise SPFVersionError(view)

        spf = SPF()
        for view, term in next_term:
            directive = self._parse_directive(view, term)
            if directive:
                spf.directives.append(directive)
                continue
            modifier = self._parse_modifier(view, term)
            if modifier:
                spf.modifiers.append(modifier)
                continue
            raise UnknownTermError(view, term)

        return spf

    # quite similar to _parse_modifier; unify?
    def _parse_directive(self, view: ParsingString, term: str) -> typing.Optional[Directive]:
        match = self.DIRECTIVE_RE.fullmatch(term)
        if not match:
            return None

        name, arg = match.group(1, 2)
        parser = self.DIRECTIVE_HANDLERS.get(name, None)
        if parser is None:
            raise UnknownDirectiveError(view, name, arg)

        return parser(view, arg)

    def _parse_modifier(self, view: ParsingString, term: str) -> typing.Optional[Modifier]:
        match = self.MODIFIER_RE.fullmatch(term)
        if not match:
            return None

        name, arg = match.group(1, 2)
        parser = self.MODIFIER_HANDLERS.get(name, None)
        if parser is None:
            raise UnknownModifierError(view, name, arg)

        return parser(view, arg)


if __debug__:
    def mod_name_checker() -> None:
        mod_name = re.compile(Parser.MOD_NAME)
        for directive in Parser.DIRECTIVE_HANDLERS.keys():
            assert mod_name.fullmatch(directive), f"{directive} must match {mod_name.pattern}"
        for modifier in Parser.MODIFIER_HANDLERS.keys():
            assert mod_name.fullmatch(modifier), f"{modifier} must match {mod_name.pattern}"
    mod_name_checker()
