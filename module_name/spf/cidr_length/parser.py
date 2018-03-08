#!/usr/bin/env python3
"""cidr-length parser."""

# import re
import typing
from module_name.spf.error import ParsingError
from module_name.parsing_string import ParsingString
from .cidr_lengths import CidrLengths
from .error import (
    EmptyError,
    InvalidCharacterError,
    InvalidDualSeparatorError,
    InvalidRangeError,
    InvalidStartError,
    JunkedEndError,
    ZeroPaddingError,
)


class Parser():
    """Parser of a cidr-length string."""
    # IP4_CIDR_RE: typing.ClassVar[typing.Pattern] = re.compile(r"/(0|[1-9]\d?)")
    # IP6_CIDR_RE: typing.ClassVar[typing.Pattern] = re.compile(r"/(0|[1-9]\d{0-2})")

    def __init__(self, ip4: bool, ip6: bool) -> None:
        """Create a :class:`CidrLength`.

        `ip4` and `ip6` specify which kinds of CIDR-lengths this :class:`Parser` parses.
        """
        assert ip4 or ip6
        self.ip4 = ip4
        self.ip6 = ip6

    def parse(self, length: str) -> CidrLengths:
        """Parse a cidr-length.

        `length` is the cidr-length string to parse.

        Returns a :class:`CidrLengths`.
        """
        view = ParsingString(length)
        cidr = CidrLengths(length)

        if self.ip4:
            kind = "ip4-cidr-length" if not self.ip6 else "dual-cidr-length"
            view, cidr.ip4 = self._parse(cidr.errors, kind, "ip4-cidr-length", view)
            if cidr.ip4 is not None:
                assert cidr.ip4 >= 0
                if cidr.ip4 > 32:
                    cidr.errors.append(InvalidRangeError(view, "ip4-cidr-length", (0, 32),
                                                         cidr.ip4))
                    cidr.ip4 = 32
                if not view:
                    return cidr
                if self.ip6:
                    sep = str(view).find("/")
                    if sep > 0:
                        cidr.errors.append(InvalidDualSeparatorError(view))
                    # TODO: should we handle this here or let the following code take care of it?
                    elif False or sep < 0:
                        cidr.errors.append(JunkedEndError(view, "ip4-cidr-length"))
                        return cidr
                    view.advance(sep + 1)
            if view and not self.ip6:
                cidr.errors.append(JunkedEndError(view, "ip4-cidr-length"))
                return cidr

        if self.ip6:
            view, cidr.ip6 = self._parse(cidr.errors, "ip6-cidr-length", "ip6-cidr-length", view)
            if cidr.ip6 is not None:
                assert cidr.ip6 >= 0
                if cidr.ip6 > 128:
                    cidr.errors.append(InvalidRangeError(view, "ip6-cidr-length", (0, 128),
                                                         cidr.ip6))
                    cidr.ip6 = 128
                if view:
                    cidr.errors.append(JunkedEndError(view, "ip6-cidr-length"))

        return cidr

    @staticmethod
    def _parse(errors: typing.List[ParsingError], parsing_kind: str, specific_kind: str,
               view: ParsingString) -> typing.Tuple[ParsingString, typing.Optional[int]]:
        """Parse a domain-spec.

        `errors` is a `list` to which errors will be appended.
        `parsing_kind` specifies which CIDR type the parser is for.
        `specific_kind` specifies which CIDR type we are attempting to parse.
        `view` is the string to parse.

        Returns a tuple (

            * updated `view`
            * parsed CIDR length (or `None`)

        ).

        Raises a :exc:`CidrLengthParsingError` when parsing fails.
        """
        # attempt to strip the leading "/"
        if not view:
            errors.append(EmptyError(view, parsing_kind))
            return view, None
        start = str(view).find("/")
        if start != 0:
            if start < 0:
                # if we didn't find a separator, look for a number
                start = next((i for i, c in enumerate(view) if c.isdigit()), len(view)) -1
            errors.append(InvalidStartError(view, parsing_kind))
        view.advance(start + 1)
        if not view:
            errors.append(EmptyError(view, parsing_kind))
            return view, None

        sep = str(view).find("/")
        # an empty string is allowed when when the caller looks for different kinds,
        # i.e. parsing_kind is "dual" and specific_kind is "ip4"
        if sep == 0 and parsing_kind == specific_kind:
            view.advance(1)
            return view, None

        # find the first digit-character
        first_digit_idx = next((i for i, c in enumerate(view) if c.isdigit()), -1)
        if first_digit_idx != 0:
            errors.append(InvalidCharacterError(view, parsing_kind))
            if first_digit_idx < 0:
                # no digits at all -> return None
                advance = sep
                if advance < 0:
                    # only junk, skip everything
                    advance = len(view)
                view.advance(advance)
                return view, None
            view.advance(first_digit_idx)

        assert view[0].isdigit()

        # find the first non-digit-character
        first_non_digit_idx = next((i for i, c in enumerate(view) if not c.isdigit()),
                                   len(view))
        number = int(view[:first_non_digit_idx])

        if view[0] == "0" and first_non_digit_idx > 1:
            errors.append(ZeroPaddingError(view, specific_kind))

        view.advance(first_non_digit_idx)
        return view, number


# pylint: disable=bad-whitespace
IP4_PARSER  = Parser(True , False)  # noqa: E221, E202, E203
IP6_PARSER  = Parser(False, True )  # noqa: E221, E202, E203
DUAL_PARSER = Parser(True , True )  # noqa: E221, E202, E203
