#!/usr/bin/env python3
"""cidr-length parsing errors."""

import copy
import typing
from module_name.spf.error import ParsingError as SPFParsingError
from module_name.parsing_string import ParsingString


class ParsingError(SPFParsingError):
    """Errors while parsing cidr-lengths in SPF."""
    def __init__(self, view: ParsingString, kind: str) -> None:
        """Create a :class:`ParsingError`.

        `view` is the :class:`ParsingString` when the error occurred.
        `kind` specifies the type of cidr-length string (e.g. "ip4-cidr-length").
        """
        super().__init__()
        self.view = copy.copy(view)
        self.kind = kind


class JunkedEndError(ParsingError):
    """Junk at end of cidr-length."""
    pass


class EmptyError(ParsingError):
    """An empty cidr-length."""
    pass


class InvalidRangeError(ParsingError):
    """Invalid number range for cidr-lengths."""
    def __init__(self, view: ParsingString, kind: str, valid_range: typing.Tuple[int, int],
                 value: int) -> None:
        """Create a :class:`InvalidRangeError`.

        `view` and `kind` are the same as for :meth:`ParsingError.__init__`.
        `valid_range` specifies the allowed range.
        `value` is the value that was read.
        """
        assert value < valid_range[0] or value > valid_range[1]
        super().__init__(view, kind)
        self.valid_range = valid_range
        self.value = value

    @property
    def valid_range_str(self) -> str:
        """A `str`ified :attr:`valid_range`."""
        return f"[{self.valid_range[0]}..{self.valid_range[1]}]"

    @property
    def token_range(self) -> typing.Tuple[int, int]:
        """A `str`ified :attr:`valid_range`."""
        value_len = len(str(self.value))
        tok_to = self.view.cursor
        tok_from = tok_to - value_len
        return tok_from, tok_to


class InvalidCharacterError(ParsingError):
    """Invalid character in cidr-length."""
    @property
    def invalid_char(self) -> str:
        """The invalid character that induced the error."""
        return self.view[0]


class InvalidStartError(InvalidCharacterError):
    """Junk at end of cidr-length."""
    start: typing.ClassVar[str] = "/"


class InvalidDualSeparatorError(InvalidCharacterError):
    """Invalid character in dual-cidr-length after ip4-cidr-length."""
    separator: typing.ClassVar[str] = "/"

    def __init__(self, view: ParsingString) -> None:
        """Create a :class:`InvalidRangeError`.

        `view` is the same as for :meth:`ParsingError.__init__`.
        """
        super().__init__(view, "dual-cidr-length")


class ZeroPaddingError(ParsingError):
    """Zero-padding is not allowed in cidr-lenghts."""
    @property
    def pad_amount(self) -> int:
        """The amount of 0-padding observed."""
        # find first non-0 character, or last if all 0's
        num_pad = next((i for i, c in enumerate(self.view) if c != "0"), len(self.view) - 1)
        assert num_pad != 0
        return num_pad
