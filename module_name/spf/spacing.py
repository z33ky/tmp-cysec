#!/usr/bin/env python3


from .term import Term


class Spacing(Term):
    def __init__(self, space: str) -> None:
        assert space.isspace()
        super().__init__(space)
