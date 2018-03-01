#!/usr/bin/env python3
"""SPF parsing errors."""


from module_name.parsing_string import ParsingString


class ParsingError(RuntimeError):
    """Errors while parsing SPF."""
    pass


class SPFVersionError(ParsingError):
    def __init__(self, view: ParsingString) -> None:
        super().__init__()
        self.view = view


class UnknownTermError(ParsingError):
    def __init__(self, view: ParsingString, term: str) -> None:
        super().__init__()
        self.view = view
        self.term = term


class UnknownDirectiveError(ParsingError):
    def __init__(self, view: ParsingString, name: str, arg: str) -> None:
        super().__init__()
        self.view = view
        self.name = name
        self.arg = arg

    @property
    def term(self) -> str:
        if self.arg is None:
            return self.name
        return f"{self.name}:{self.arg}"


class UnknownModifierError(ParsingError):
    def __init__(self, view: ParsingString, name: str, arg: str) -> None:
        super().__init__()
        self.view = view
        self.name = name
        self.arg = arg

    @property
    def term(self) -> str:
        return f"{self.name}={self.arg}"
