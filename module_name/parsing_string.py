#!/usr/bin/env python3
"""Defines the :class:`ParsingString`."""

import itertools
import typing


class ParsingString():
    """A `str` + cursor.

    This class contains a `str` and a cursor, which indicates how far the string has been parsed.

    The string starting from the cursor is called "partial string".
    """
    def __init__(self, string: str) -> None:
        """Create a :class:`ParsingString`."""
        self.string = string
        self.cursor = 0

    def __str__(self) -> str:
        """Return the partial string."""
        return self.string[self.cursor:]

    def __eq__(self, other: object) -> bool:
        """Compare the partial string.

        Comparison against another :class:`ParsingString` raises an :exc:`TypeError`,
        because the semantics of that can be a matter of opinion:
        Should that be a field-wise comparison, or should the `str`ified versions be compared?
        """
        if isinstance(other, ParsingString):
            # do we want field-wise equality or compare str(self) to str(other)?
            raise TypeError("Comparing ParsingStrings has ambiguous semantics "
                            "and is thus not supported.")
        return str(self) == other

    def __getitem__(self, elem: typing.Union[int, slice]) -> str:
        """Return an element/slice of the partial string."""
        if isinstance(elem, slice):
            start = elem.start
            stop = elem.stop
            if start is None:
                start = self.cursor
            else:
                start += self.cursor
            if stop is not None:
                stop += self.cursor
            elem = slice(start, stop, elem.step)
        else:
            elem += self.cursor
        return self.string[elem]

    def __bool__(self) -> bool:
        """Check if any characters remain."""
        return bool(str(self))

    def __len__(self) -> int:
        """Return the number of characters left."""
        return len(self.string) - self.cursor

    def __iter__(self) -> typing.Iterator[str]:
        """Iterate over the partial string."""
        return itertools.islice(iter(self.string), self.cursor, None)

    def advance(self, n: int) -> None:
        """Advance the cursor.

        Raises an :exc:`IndexError` if the cursor would advance past the string.
        """
        if n > len(self):
            raise IndexError(f"Tried to skip({n}), but only {len(self)} are left.")
        if n < -self.cursor:
            raise IndexError(f"Tried to skip({n}), but cursor is only at {self.cursor}.")
        self.cursor += n
