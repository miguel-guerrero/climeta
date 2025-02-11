"""
Base cleass for code emitters for different languages
"""


class Emitter:
    """base class for several emitters"""

    INDENT = "    "

    def __init__(self):
        self.code = []
        self.indent_level = 0

    def emit(self, arg: str) -> None:
        """emit a line of code"""
        ind = self.INDENT * self.indent_level
        self.code.append(ind + arg)

    def emit_noindent(self, arg: str) -> None:
        """emit a line of code ignoring indentation"""
        self.code.append(arg)

    def __str__(self) -> str:
        """convert emitted code to string"""
        return "\n".join(self.code)

    def indent(self) -> None:
        """increase indent level"""
        self.indent_level += 1

    def deindent(self) -> None:
        """decrease indent level"""
        self.indent_level -= 1

    def new_line(self) -> None:
        """emit a new line"""
        self.emit_noindent("")
