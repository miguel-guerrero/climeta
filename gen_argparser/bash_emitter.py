"""
Code emitter specialized for several Bash constructs
"""

from typing import Optional
from .emitter import Emitter
from .indenter import Indenter


class BashEmitter(Emitter):
    """implement several common Bash constructs while generating code"""

    def cmnt(self, text: str) -> None:
        """emit a single line comment"""
        self.emit("# " + text)

    def case(self, expr: str) -> Indenter:
        """generate a case statement block and its terminator"""
        return Indenter(self, f'case "{expr}" in', "esac")

    def case_pattern(
        self, pattern, suffix: Optional[str] = "", post: Optional[str] = ""
    ) -> Indenter:
        """generate a case pattern block and its terminator"""
        if suffix != "":
            suffix = " " + suffix
        return Indenter(self, f"{pattern}){suffix}", self.INDENT + post + ";;")

    def func(self, func_name: str) -> Indenter:
        """generate a function definition block and its terminator"""
        return Indenter(self, func_name + "() {", "}\n")

    def for_loop(self, var: str, lst: str) -> Indenter:
        """generate a for loop block and its terminator"""
        return Indenter(self, f"for {var} in {lst}; do", "done")

    def while_loop(self, expr: str) -> Indenter:
        """generate a while loop block and its terminator"""
        return Indenter(self, f"while [ {expr} ]; do", "done")

    def if_then(self, cond: str) -> Indenter:
        """generate a if/then/fi block and its terminator"""
        return Indenter(self, f"if [ {cond} ]; then", "fi")

    def if_then_else(self, cond: str) -> Indenter:
        """generate a if/then block, assumes elif_/else_ follows"""
        return Indenter(self, f"if [ {cond} ]; then")

    def elif_(self, cond: str) -> Indenter:
        """add an elif condition, assumes if_then_else precedes"""
        return Indenter(self, f"elif [ {cond} ]; then")

    def else_(self) -> Indenter:
        """add an else condition, assumes if_then_else or elif_ precedes"""
        return Indenter(self, "else", "fi")

    def echo_literal(self, text: str) -> None:
        """literal echo, not allowing variable interpolation"""
        self.emit(f"echo '{text}'")

    def echo(self, text: str) -> None:
        """echo allowing variable interpolation"""
        self.emit(f'echo "{text}"')

    def error(self, text: str) -> None:
        """emit an error message to stderr"""
        self.emit(f'echo "ERROR: {text}" >&2')
