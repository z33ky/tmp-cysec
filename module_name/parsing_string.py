#!/usr/bin/env python3
"""A string view."""

import itertools
import typing


class ParsingString():
    def __init__(self, string: str) -> None:
        self.string = string
        self.offset = 0

    def __str__(self) -> str:
        return self.string[self.offset:]

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, ParsingString):
            # do we want field-wise equality or compare str(self) to str(other)?
            raise TypeError("Comparing ParsingStrings has ambiguous semantics "
                            "and is thus not supported.")
        return str(self) == other

    def __getitem__(self, elem: typing.Union[int, slice]) -> str:
        if isinstance(elem, slice):
            start = elem.start
            stop = elem.stop
            if start is None:
                start = self.offset
            else:
                start += self.offset
            if stop is not None:
                stop += self.offset
            elem = slice(start, stop, elem.step)
        else:
            elem += self.offset
        return self.string[elem]

    def __bool__(self) -> bool:
        return bool(str(self))

    def __len__(self) -> int:
        return len(self.string) - self.offset

    def __iter__(self) -> typing.Iterator[str]:
        return itertools.islice(iter(self.string), self.offset, None)

    def skip(self, n: int) -> None:
        if n > len(self):
            raise IndexError(f"Tried to skip({n}), but only {len(self)} are left.")
        if n < -self.offset:
            raise IndexError(f"Tried to skip({n}), but offset is only {self.offset}.")
        self.offset += n
