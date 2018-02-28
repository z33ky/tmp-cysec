#!/usr/bin/env python3
"""cidr-length parser."""

# import re
import typing
from module_name.parsing_string import ParsingString
from .error import (
    EmptyError,
    InvalidCharacterError,
    InvalidDualSeparatorError,
    InvalidRangeError,
    InvalidStartError,
    JunkedEndError,
    PaddingError,
)


class Parser():
    """TODO"""
    # IP4_CIDR_RE: typing.ClassVar[typing.Pattern] = re.compile(r"/(0|[1-9]\d?)")
    # IP6_CIDR_RE: typing.ClassVar[typing.Pattern] = re.compile(r"/(0|[1-9]\d{0-2})")

    def __init__(self, ip4: bool, ip6: bool) -> None:
        """Create a :class:`CidrLength`.

        `ip4` and `ip6` specify which kinds of CIDR-lengths this :class:`CidrLength` parses.
        """
        self.ip4 = ip4
        self.ip6 = ip6
        # assert self.ip4 or self.ip6

    def parse(self, length: str) -> typing.Tuple[typing.Optional[int], typing.Optional[int]]:
        """Parse a cidr-length.

        `length` is the cidr-length string to parse.

        Returns a tuple (

            * IPv4 CIDR length
            * IPv6 CIDR length

        ).

        Raises a :exc:`CidrLengthParsingError` when parsing fails.
        """
        view = ParsingString(length)

        ip4length = None
        if self.ip4:
            kind = "ip4-cidr-length" if not self.ip6 else "dual-cidr-length"
            view, ip4length = self._parse(kind, view, self.ip6)
            if ip4length is not None:
                if not 0 <= ip4length <= 32:
                    raise InvalidRangeError(view, "ip4-cidr-length", (0, 32), ip4length)
                if not view:
                    return ip4length, None
                if self.ip6:
                    if view[0] == "/":
                        view.skip(1)
                    else:
                        raise InvalidDualSeparatorError(view)
            if view and not self.ip6:
                raise JunkedEndError(view, "ip4-cidr-length")

        ip6length = None
        if self.ip6:
            view, ip6length = self._parse("ip6-cidr-length", view, False)
            assert ip6length
            if not 0 <= ip6length <= 128:
                raise InvalidRangeError(view, "ip6-cidr-length", (0, 128), ip6length)
            if view:
                raise JunkedEndError(view, "ip6-cidr-length")

        # assert ip4length or ip6length
        return ip4length, ip6length

    @staticmethod
    def _parse(kind: str, view: ParsingString, tok_continue: bool) \
            -> typing.Tuple[ParsingString, typing.Optional[int]]:
        """Parse a domain-spec.

        `kind` specifies which CIDR type we are attempting to parse.
        `view` is the string to parse.
        `tok_continue` specifies whether an empty string is allowed when the continuation-token "/"
                       is encountered.

        Returns a tuple (

            * updated `view`
            * parsed CIDR length (or `None`)

        ).

        Raises a :exc:`CidrLengthParsingError` when parsing fails.
        """
        # attempt to strip the leading "/"
        if not view:
            raise EmptyError(view, kind)
        if view[0] != "/":
            raise InvalidStartError(view, kind)
        view.skip(1)
        if not view:
            raise EmptyError(view, kind)

        if view[0] == "0":
            view.skip(1)
            # we now know the specific kind
            # FIXME: assuming tok_continue only on ip4-cidr-length
            if tok_continue:
                kind = "ip4-cidr-length"
            else:
                kind = "ip6-cidr-length"

            if not view or view[0].isspace():
                return view, 0

            if view[0].isdigit():
                # unskip the "0"
                view.skip(-1)
                raise PaddingError(view, kind)
            else:
                raise InvalidDualSeparatorError(view)
        elif view[0].isdigit():
            # non-0 number
            # find the first non-digit-character
            first_non_digit_idx = next((i for i, c in enumerate(view) if not c.isdigit()),
                                       len(view))
            length = int(view[:first_non_digit_idx])
            view.skip(first_non_digit_idx)
            return view, length
        elif view[0] == "/" and tok_continue:
            return view, None
        else:
            raise InvalidCharacterError(view, kind)


# pylint: disable=bad-whitespace
IP4_PARSER  = Parser(True , False)  # noqa: E221, E202, E203
IP6_PARSER  = Parser(False, True )  # noqa: E221, E202, E203
DUAL_PARSER = Parser(True , True )  # noqa: E221, E202, E203
