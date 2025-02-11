"""
Code emitter specialized for several C++ constructs
derives from C emitter
"""

from .c_emitter import CEmitter
from .indenter import Indenter


class CppEmitter(CEmitter):
    """implement several common C++ constructs while generating code"""

    def header_guard_begin(self, _filename_base: str) -> None:
        self.emit("#pragma once")
        self.new_line()

    def header_guard_end(self) -> None:
        pass

    def for_list_loop(self, var: str, lst: str) -> Indenter:
        """generate a for loop block and its terminator"""
        return Indenter(self, f"for ({var} : {lst}) {{", "}")
