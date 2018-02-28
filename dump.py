#!/usr/bin/env python3
"""Dump."""

import enum
import sys
import typing
from module_name.spf import cidr_length


# test...

def main() -> None:
    try:
        cidr_type = input("CIDR type? (ip4, ip6, dual) ")
        cidr = {
            'ip4' : cidr_length.IP4CidrLengthParser,  # noqa: E203
            'ip6' : cidr_length.IP6CidrLengthParser,  # noqa: E203
            'dual': cidr_length.DualCidrLengthParser,
        }[cidr_type]
        cidr.parse(input("cidr-length string: "))
    except cidr_length.JunkedEndError as e:
        print(f"{e.kind} has junk at end.\n"
              f"input: {e.view.string}\n"
              f"       {' ' * e.view.cursor}^{'~' * (len(e.view) - 1)}",
              file=sys.stderr)
        sys.exit(1)
    except cidr_length.EmptyError as e:
        print(f"{e.kind} must not be empty.\n"
              f"input: {e.view.string}\n"
              f"       {' ' * e.view.cursor}^",
              file=sys.stderr)
        sys.exit(1)
    except cidr_length.InvalidStartError as e:
        print(f"{e.kind} must start with \"{e.start}\".\n"
              f"input: {e.view.string}\n"
              f"       {' ' * e.view.cursor}^",
              file=sys.stderr)
        sys.exit(1)
    except cidr_length.InvalidRangeError as e:
        str_from, str_to = e.token_range
        value_len = str_to - str_from
        print(f"{e.kind} must be in {e.valid_range_str}, but is \"{e.value}\".\n"
              f"input: {e.view.string}\n"
              f"       {' ' * str_from}^{'~' * (value_len - 1)}",
              file=sys.stderr)
        sys.exit(1)
    except cidr_length.InvalidDualSeparatorError as e:
        print(f"Expected dual-cidr-length separator \"{e.separator}\" or NUL, "
              f"found \"{e.invalid_char}\".\n"
              f"input: {e.view.string}\n"
              f"       {' ' * e.view.cursor}^",
              file=sys.stderr)
        sys.exit(1)
    except cidr_length.InvalidCharacterError as e:
        print(f"Invalid character \"{e.invalid_char}\" in {e.kind}.\n"
              f"input: {e.view.string}\n"
              f"       {' ' * e.view.cursor}^",
              file=sys.stderr)
        sys.exit(1)
    except cidr_length.PaddingError as e:
        print(f"{e.kind} must not be 0-padded.\n"
              f"input: {e.view.string}\n"
              f"       {' ' * e.view.cursor}^{'~' * (e.pad_amount - 1)}",
              file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()


# dump...

QUALIFIERS = {
    '+': "pass",
    '-': "fail",
    '~': "softfail",
    '?': "neutral",
}


class SpfArg(enum.Enum):
    """Remove me."""
    Optional  = 0
    Mandatory = 1


class Cidr(enum.Enum):
    """Remove me."""
    IPv4 = 0
    IPv6 = 1
    Dual = 2


class DomainSpec():
    """TODO"""
    # FIXME: use proper domain type, not str
    def parse(self, spec: str, domain: str) -> None:
        """Parse a domain-spec.

        `spec` is the domain-spec string.
        `domain` is the current domain for which the SPF record is parsed.
        """
        raise NotImplementedError()


class SpfMechanism():
    """TODO"""
    name: str
    arg: typing.Optional[SpfArg]
    cidr: typing.Optional[Cidr]

    # def __init__(self, name: str, *, mandatory_args: typing.Tuple[SpfArg] = (),
    #              optional_args: typing.Tuple[SpfArg] = ()) -> None:
    def __init__(self, name: str, arg: typing.Optional[SpfArg] = None,
                 cidr: typing.Optional[Cidr] = None) -> None:
        """TODO"""
        if cidr is not None:
            assert arg is not None
        self.name = name
        self.arg = arg
        self.cidr = cidr

    def parse(self, string: str) -> None:
        """TODO"""
        raise NotImplementedError()


SPF_MECHANISMS = {mech.name: mech for mech in (
    SpfMechanism('all'),
    SpfMechanism('include', SpfArg.Mandatory),
    SpfMechanism('a', SpfArg.Optional, Cidr.Dual),
    SpfMechanism('mx', SpfArg.Optional, Cidr.Dual),
    SpfMechanism('ptr', SpfArg.Optional),
    SpfMechanism('ip4', SpfArg.Mandatory, Cidr.IPv4),
    SpfMechanism('ip6', SpfArg.Mandatory, Cidr.IPv6),
    SpfMechanism('exist', SpfArg.Mandatory),
)}
