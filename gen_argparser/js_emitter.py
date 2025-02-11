"""
Code emitter specialized for several JavaScript constructs
"""

from typing import List
from .emitter import Emitter
from .indenter import Indenter


class JavaScriptEmitter(Emitter):
    """implement several common JavaScript constructs while generating code"""

    INDENT = "  "

    def cmnt(self, text: str) -> None:
        """emit a single line comment"""
        self.emit("// " + text)

    def func(self, name: str, args: List[str]) -> None:
        """generate a function definition, indent inner block"""
        return Indenter(self, f"function {name}({', '.join(args)}) {{", "};\n")

    def exported_func(self, name: str, args: List[str]) -> None:
        """generate an exported function definition, indent inner block"""
        return Indenter(
            self, f"export function {name}({', '.join(args)}) {{", "};\n"
        )

    def import_(self, filename: str, func: str) -> None:
        """generate an import statement"""
        self.emit(f"import {func} from '{filename}';")

    def import_as(self, filename: str, as_name: str) -> None:
        """generate an import as statement"""
        self.emit(f"import * as {as_name} from '{filename}';")

    def echo_literal(self, text: str) -> None:
        """literal echo, not allowing variable interpolation"""
        self.emit(f"console.log('{text}');")

    def for_in_loop(self, var: str, lst: str) -> Indenter:
        """generate a for in loop block and its terminator"""
        return Indenter(self, f"for ({var} in {lst}) {{", "}")

    def for_of_loop(self, var: str, lst: str) -> Indenter:
        """generate a for of loop block and its terminator"""
        return Indenter(self, f"for ({var} of {lst}) {{", "}")

    def if_then(self, cond: str) -> Indenter:
        """generate an if block and its terminator"""
        return Indenter(self, f"if ({cond}) {{", "}")
