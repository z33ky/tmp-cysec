#!/usr/bin/env python3
"""SPF parsing errors."""


import typing
if typing.TYPE_CHECKING:
    # mypy has no issues with cyclic imports
    # pylint: disable=cyclic-import,unused-import
    from .directive import Directive  # noqa: F401
    from .macro_string import MacroString  # noqa: F401
    from .modifier import Modifier  # noqa: F401
    from .term import Term  # noqa: F401
    from .version import Version  # noqa: F401


class ParsingError(RuntimeError):
    """Errors while parsing SPF."""
    pass


class TermError(ParsingError):
    """Errors while parsing SPF terms."""
    def __init__(self, term: 'Term') -> None:
        super().__init__()
        self.term = term


class SPFVersionError(TermError):
    """Invalid SPF version."""
    def __init__(self, version: 'Version') -> None:
        super().__init__(version)


class UnknownTermError(TermError):
    """An unknown term was encountered."""
    pass


class UnknownDirectiveError(UnknownTermError):
    """An unknown directive was encountered."""
    def __init__(self, directive: 'Directive') -> None:
        super().__init__(directive)


class UnknownModifierError(UnknownTermError):
    """An unknown modifier was encountered."""
    def __init__(self, modifier: 'Modifier') -> None:
        super().__init__(modifier)


class UnknownMacroLetterError(ParsingError):
    def __init__(self, macro: 'MacroString', letter: str) -> None:
        super().__init__()
        self.macro = macro
        self.letter = letter


class UnknownMacroSpecialLetterError(ParsingError):
    def __init__(self, macro: 'MacroString') -> None:
        super().__init__()
        self.macro = macro


class InvalidMacroLiteralError(ParsingError):
    def __init__(self, macro: 'MacroString') -> None:
        super().__init__()
        self.macro = macro


class TrailingMacroExpandError(ParsingError):
    def __init__(self, macro: 'MacroString') -> None:
        super().__init__()
        self.macro = macro


class EmptyMacroExpandError(ParsingError):
    def __init__(self, macro: 'MacroString') -> None:
        super().__init__()
        self.macro = macro


class InvalidMacroExpandDelimiterError(ParsingError):
    def __init__(self, macro: 'MacroString') -> None:
        super().__init__()
        self.macro = macro


class InvalidMacroTransformerError(ParsingError):
    def __init__(self, macro: 'MacroString') -> None:
        super().__init__()
        self.macro = macro


class SwappedMacroTransformerError(InvalidMacroTransformerError):
    def __init__(self, macro: 'MacroString') -> None:
        super().__init__(macro)
        self.macro = macro


class InvalidMacroTransformerCommandError(InvalidMacroTransformerError):
    def __init__(self, macro: 'MacroString') -> None:
        super().__init__(macro)
        self.macro = macro
