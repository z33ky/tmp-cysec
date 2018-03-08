#!/usr/bin/env python3
"""Defined :class:`CidrLengths`."""


import typing
from module_name.spf.term import Term


class CidrLengths(Term):
    """CIDR lengths.

    These represent the latter part of a CIDR (Class Inter-Domain Routing) from which the
    network mask can be derived.
    """

    ip4: typing.Optional[int] = None
    ip6: typing.Optional[int] = None
