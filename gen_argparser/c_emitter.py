"""
Code emitter specialized for several C constructs
"""

from typing import List
from .emitter import Emitter
from .indenter import Indenter


class CEmitter(Emitter):
    """implement several common C constructs while generating code"""

    def cmnt(self, text: str) -> None:
        """emit a single line comment"""
        self.emit("// " + text)

    def extern_c_begin(self) -> None:
        """emit a extern C block guarded by if __cplusplus"""
        self.new_line()
        self.emit("#ifdef __cplusplus")
        self.emit('extern "C" {')
        self.emit("#endif")
        self.new_line()

    def extern_c_end(self) -> None:
        """close a extern C block guarded by if __cplusplus"""
        self.new_line()
        self.emit("#ifdef __cplusplus")
        self.emit("}")
        self.emit("#endif")
        self.new_line()

    def header_guard_begin(self, filename_base: str) -> None:
        """generate a header guard C style"""
        self.emit(f"#ifndef __{filename_base}_h__")
        self.emit(f"#define __{filename_base}_h__")
        self.new_line()

    def header_guard_end(self) -> None:
        """close a header guard"""
        self.emit("#endif")

    def func(self, name: str, args: List[str], ret: str = "void") -> None:
        """generate a function definition, indent inner block"""
        return Indenter(self, f"{ret} {name}({', '.join(args)}) {{", "}\n")

    def static_func(
        self, name: str, args: List[str], ret: str = "void"
    ) -> None:
        """generate a static function definition, indent inner block"""
        return Indenter(
            self, f"static {ret} {name}({', '.join(args)}) {{", "}\n"
        )

    def include(self, *filenames) -> None:
        """generate a include statement"""
        for filename in filenames:
            self.emit(f'#include "{filename}"')

    def include_sys(self, *filenames) -> None:
        """generate a system include statement"""
        for filename in filenames:
            self.emit(f"#include <{filename}>")

    def if_then(self, cond: str) -> Indenter:
        """generate an if block and its terminator"""
        return Indenter(self, f"if ({cond}) {{", "}")

    def while_loop(self, cond: str) -> Indenter:
        """generate a while loop block and its terminator"""
        return Indenter(self, f"while ({cond}) {{", "}")
