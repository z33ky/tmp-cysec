#!/usr/bin/env python3

import typing
from .directive import Directive
from .modifier import Modifier


class SPF:
    directives: typing.List[Directive] = []
    modifiers: typing.List[Modifier] = []
