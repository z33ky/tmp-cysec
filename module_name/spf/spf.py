#!/usr/bin/env python3

import itertools
import typing
from .error import ParsingError
from .term import Term


class SPF:
    def __init__(self, terms: typing.List[Term]) -> None:
        self.terms = terms

    def __str__(self) -> str:
        return "".join(map(str, self.terms))

    @property
    def errors(self) -> typing.Iterator[ParsingError]:
        return itertools.chain(*(term.errors for term in self.terms))
