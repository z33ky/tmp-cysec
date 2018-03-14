#!/usr/bin/env python3

import ipaddress
import typing


# pylint: disable=invalid-name
IPAddress = typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


class Domain(typing.NamedTuple):  # pylint: disable=too-few-public-methods
    ip_address: IPAddress  # TODO: list of addresses?
    labels: typing.Sequence[str]

    @property
    def name(self) -> str:
        return ".".join(self.labels)


class Sender(typing.NamedTuple):  # pylint: disable=too-few-public-methods
    local: str
    domain: Domain

    def __str__(self) -> str:
        return f"{self.local}@{self.domain.name}"


class RequestContext(typing.NamedTuple):  # pylint: disable=too-few-public-methods
    sender: Sender
    requester: Domain
    requested: typing.MutableSequence[Domain] = []
