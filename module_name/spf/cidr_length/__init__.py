#!/usr/bin/env python3
# flake8: noqa: F401
"""cidr-length parsing."""

from .error import (
    EmptyError,
    InvalidCharacterError,
    InvalidDualSeparatorError,
    InvalidRangeError,
    InvalidStartError,
    JunkedEndError,
    ZeroPaddingError,
    ParsingError,
)
from .parser import (
    IP4_PARSER as IP4CidrLengthParser,
    IP6_PARSER as IP6CidrLengthParser,
    DUAL_PARSER as DualCidrLengthParser,
)
