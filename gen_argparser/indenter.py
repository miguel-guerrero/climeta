"""
A context manager to indent/deindent blocks automatically


    with Indenter(indentee):
        ...

    indentee must contain an 'indent_level' attribute

"""

from typing import Optional


class Indenter:
    """Class to keep indentation levels"""

    def __init__(
        self,
        emitter: "Emitter",
        pre_text: Optional[str] = None,  # to emit before indenting block
        post_text: Optional[str] = None,  # to emit after we finish block
    ):
        self.emitter = emitter
        self.pre_text = pre_text
        self.post_text = post_text

    def __enter__(self) -> None:
        """emit pre_text and indent"""
        if self.pre_text is not None:
            self.emitter.emit(self.pre_text)
        self.emitter.indent_level += 1

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """deindent and emit post_text"""
        self.emitter.indent_level -= 1
        if self.post_text is not None:
            self.emitter.emit(self.post_text)
