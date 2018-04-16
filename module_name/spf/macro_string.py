#!/usr/bin/env python3
"""Defines the :class:'MacroString'."""


import datetime
import re
import typing
from module_name.parsing_string import ParsingString
from module_name.request_context import RequestContext
from .error import (
    EmptyMacroExpandError,
    InvalidMacroExpandDelimiterError,
    InvalidMacroLiteralError,
    InvalidMacroTransformerCommandError,
    InvalidMacroTransformerError,
    SwappedMacroTransformerError,
    TrailingMacroExpandError,
    UnknownMacroLetterError,
    UnknownMacroSpecialLetterError,
)
from .term import Term


class MacroString(Term):
    """A macro-string.

    The string is expanded on initialization.
    """
    # chr(0x25) == ';'
    ALLOWED_MACRO_LITERALS: typing.Sequence[str] = (*(chr(num) for num in range(0x21, 0x7e)
                                                      if num != 0x25),)
    assert all(map(str.isprintable, ALLOWED_MACRO_LITERALS))

    MACRO_LETTERS: typing.ClassVar[typing.Mapping[str, typing.Callable[[RequestContext], str]]] = {
        's': lambda ctx: str(ctx.sender),
        'l': lambda ctx: ctx.sender.local,
        'o': lambda ctx: ctx.sender.domain.name,
        'd': lambda ctx: ctx.requested[-1].name,
        'i': lambda ctx: str(ctx.sender.domain.ip_address),
        # FIXME: 'p' should be PTR lookup instead (also: deprecated)
        'p': lambda ctx: ctx.sender.domain.name,
        'v': lambda ctx: "in-addr" if ctx.sender.domain.ip_address.version == 4 else "ip6",
        'h': lambda ctx: "(HELO/EHLO domain)",  # FIXME
        # FIXME: the following 3 are only for exp
        'c': lambda ctx: str(ctx.requester.ip_address),
        'r': lambda ctx: ctx.requester.name,
        't': lambda _ctx: str(int(datetime.datetime.now().timestamp()))
    }
    # TODO: RFC recommends avoiding %{sloh} together with mechanism directive
    # FIXME: accept any letter
    MACRO_LETTER_RE: typing.Pattern[str] = re.compile(r"{(.)([a-zA-Z0-9]*)(.*)}")
    # re.compile(fr"{{([{''.join(MACRO_LETTERS.keys())}])([0-9]*r?)([.\-+,/_=]*)}}")

    error_is_fatal = False

    def __init__(self, ctx: RequestContext, spec: str) -> None:
        """Create a :class:`MacroString`.

        `ctx` is the :class:`RequestContext` which will be used to expand the macro-string.
        `spec` is the macro-string.
        """
        super().__init__(spec)
        view = ParsingString(spec)
        self.expanded = ""

        while view:
            format_pos = str(view).find("%")
            if format_pos >= 0:
                literals = view[:format_pos]
                view.advance(format_pos)
                # literals += self._expand(ctx, view)
            else:
                literals = str(view)
                view.advance(len(literals))
                assert not view
            # FIXME: SP also valid
            if not all(char in self.ALLOWED_MACRO_LITERALS for char in literals):
                self._errors.append(InvalidMacroLiteralError(self))
            self.expanded += literals
            view = self._expand(ctx, view)

    def _expand(self, ctx: RequestContext, view: ParsingString) -> ParsingString:
        if not view:
            return view

        if view[:1] != "%":
            assert False
            return view

        view.advance(1)
        view, expanded = self._expand_letter(ctx, view, True)
        if expanded:
            return view

        letter = view[:1]
        if letter == '':
            self._errors.append(TrailingMacroExpandError(self))
            self.expanded += "%"
            return view

        view.advance(1)
        if letter == "%":
            self.expanded += "%"
        elif letter == "_":
            self.expanded += " "
        elif letter == "-":
            self.expanded += "%20"
        else:
            self._errors.append(UnknownMacroSpecialLetterError(self))
            self.error_is_fatal = True
            self.expanded += f"%{letter}"
        return view

    def _expand_letter(self, ctx: RequestContext, view: ParsingString, is_exp: bool) \
            -> typing.Tuple[ParsingString, bool]:
        match = self.MACRO_LETTER_RE.match(str(view))
        if not match:
            return view, False
        view.advance(len(match.group(0)))

        handler = self.MACRO_LETTERS.get(match.group(1), None)
        transformer, delimiters = match.group(2, 3)

        transformer_num, transformer_cmd = self._prepare_transform(transformer)

        if not all(delim in ".-+,/_=" for delim in delimiters):
            self._errors.append(InvalidMacroExpandDelimiterError(self))
            # remove letters and numbers, keep anything else
            delimiters = re.sub(r"[a-zA-Z0-9]", "", delimiters)

        if not handler:
            string = match.group(0)
            if not string:
                self._errors.append(EmptyMacroExpandError(self))
            else:
                self._errors.append(UnknownMacroLetterError(self, string[0:]))
            self.error_is_fatal = True
            expanded = f"%{string}"
        else:
            expanded = handler(ctx)
            # replace all delimiters in `expanded` by a single character for further processing
            expanded.translate(str.maketrans({c: delimiters[0] for c in delimiters[1:]}))
            delimiter = delimiters[0:]

            if transformer:
                transformed = self._transform(expanded, transformer_num, transformer_cmd, delimiter)
                if transformed is None:
                    assert self.error_is_fatal
                    expanded = f"%{match.group(0)}"
                else:
                    expanded = transformed
            elif delimiter:
                expanded.replace(delimiter, ".")

        self.expanded += expanded
        return view, True

    def _prepare_transform(self, transformer: str) -> typing.Tuple[typing.Optional[int], str]:
        if not transformer:
            return None, transformer

        split = re.split(r"(\d+)", transformer)

        if split[0]:
            # there is text preceding the number
            if len(split) == 1:
                # just text, no number
                return None, transformer

            if not split[2]:
                assert len(split) == 3
                # swapped text and number
                self._errors.append(SwappedMacroTransformerError(self))
                return int(split[1]), split[0]

            # a weird pattern; don't even try to make sense of this
            # "{cmd}{num}{*}"
            self._errors.append(InvalidMacroTransformerError(self))
            self.error_is_fatal = True
            return None, ''

        assert len(split) >= 3

        if len(split) == 3:
            return int(split[1]), split[2]

        # a weird pattern; don't even try to make sense of this
        # "{num}{cmd}{num}{*}"
        self._errors.append(InvalidMacroTransformerError(self))
        self.error_is_fatal = True
        return None, ''

    def _transform(self, string: str, transformer_num: typing.Optional[int], transformer_cmd: str,
                   delimiter: str) -> typing.Optional[str]:
        delimiter = delimiter or "."
        split = string.split(delimiter)

        split_idx = -transformer_num if transformer_num is not None else None

        if transformer_cmd == "r":
            split.reverse()
        else:
            self._errors.append(InvalidMacroTransformerCommandError(self))
            self.error_is_fatal = True
            return None

        if split_idx == 0:
            return ''

        # TODO: implementations MUST support at least transformer_num <= 127
        #       ^- warn on > 127 then
        return ".".join(split[split_idx:])
