#!/usr/bin/env python3

import ipaddress
from .error import (
        InvalidAddressError,
        WrongAddressTypeError,
)
from .term import Term

class IPAddress(Term):
    def __init__(self, address: str) -> None:
        super().__init__(address)
        try:
            self.address = ipaddress.ip_address(address)
        except ipaddress.AddressValueError as e:
            # FIXME: wrap
            self._errors.append(e)


class IP4Address(IPAddress):
    def __init__(self, address: str) -> None:
        super().__init__(address)
        if not self._errors and not isinstance(self.address, ipaddress.IPv4Address):
            self._errors.append(WrongAddressTypeError(self, "IPv4"))


class IP6Address(IPAddress):
    def __init__(self, address: str) -> None:
        super().__init__(address)
        if not self._errors and not isinstance(self.address, ipaddress.IPv6Address):
            self._errors.append(WrongAddressTypeError(self, "IPv6"))
