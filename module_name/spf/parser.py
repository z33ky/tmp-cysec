#!/usr/bin/env python3
"""cidr-length parser."""

import typing
from module_name.parsing_string import ParsingString
from module_name.request_context import RequestContext
from .directive import Directive
from .modifier import Modifier
from .spacing import Spacing
from .spf import SPF
from .term import (Term, UnknownTerm)
from .version import Version


ModifierHandler = typing.Callable[[ParsingString, str], Modifier]
DirectiveHandler = typing.Callable[[ParsingString, str], Directive]


class Parser():
    """Parser of a SPF string."""

    # strictly speaking, version|term
    @staticmethod
    def term_iter(string: str, terms: typing.MutableSequence[Term]) \
            -> typing.Generator[str, None, None]:
        """Iterate over terms in `string`.

        This yields each term as a `str`.

        `string` is the string to parse.
        `terms` is a list of :class:`Terms <.term.Term>` to which the
        :class:`Spacings <.spacing.Spacing>` will be appended.
        """
        match = Term.TERM_RE.match(string)
        view = ParsingString(string)
        while match:
            yield match.group(1)
            if match.group(2):
                terms.append(Spacing(match.group(2)))
            view.advance(len(match.group(0)))
            match = Term.TERM_RE.match(str(view))
        # TODO: if view: error

    @classmethod
    def parse(cls, ctx: RequestContext, string: str) -> SPF:
        """Parse `string` to :class:`SPF`.

        `string` is the string to parse.
        """
        terms: typing.List[Term] = []

        term_iter = cls.term_iter(string, terms)
        term = next(term_iter, None)
        if term is None:
            return SPF([UnknownTerm(string)])
        # TODO: If the version isn't present we might want to check if it's something else instead.
        #       Note that the version does have to come first though.
        terms.append(Version(term))

        for term in term_iter:
            directive = Modifier.parse(term)
            if directive:
                terms.append(directive)
                continue
            modifier = Directive.parse(ctx, term)
            if modifier:
                terms.append(modifier)
                continue
            terms.append(UnknownTerm(term))

        return SPF(terms)
