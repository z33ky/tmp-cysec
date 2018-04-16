#!/usr/bin/env python3
"""Defines the :class:`RequestContext`."""

import ipaddress
import typing


# FIXME: move this to another module?
# pylint: disable=invalid-name
IPAddress = typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


class Domain(typing.NamedTuple):  # pylint: disable=too-few-public-methods
    """A network domain.

    Has an IP-Address and a name consisting of labels.
    """
    ip_address: IPAddress  # TODO: list of addresses?
    labels: typing.Sequence[str]

    @property
    def name(self) -> str:
        """Return the name."""
        return ".".join(self.labels)


class EMailAddress(typing.NamedTuple):  # pylint: disable=too-few-public-methods
    """An E-Mail address."""
    local: str
    domain: Domain

    def __str__(self) -> str:
        """Return the complete address as a `str`:"""
        return f"{self.local}@{self.domain.name}"


class RequestContext():  # pylint: disable=too-few-public-methods
    """The context with which we do spoof checks.

    We have
        * a :attr:`sender`, which specifies who the E-Mail comes from,
        * a :attr:`requester` that does the checks
        * a list :attr:`requested`, which lists the servers which we sent requests to
    """
    sender: EMailAddress
    requester: Domain
    requested: typing.MutableSequence[Domain]

    def __init__(self, sender: EMailAddress, requester: Domain):
        """Create a :class:`RequestContext`."""
        self.sender = sender
        self.requester = requester
        self.requested = []
