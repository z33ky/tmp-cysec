#!/usr/bin/env python3

import typing
from .term import Term


class SPF:
    terms: typing.List[Term] = []

    def __str__(self) -> str:
        return "".join(map(str, self.terms))
