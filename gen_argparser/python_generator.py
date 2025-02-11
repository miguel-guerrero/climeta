"""
Generate CLI parsing code in python using argparse built-in module import
"""

from .code_generator import (
    ArgSpec,
    CodeGenerator,
    double_quote,
)
from .emitter import Emitter
from .indenter import Indenter


def get_default(arg: ArgSpec):
    """get default value for a given option"""
    assert arg.has_default
    if arg.multiple or arg.type_ != "string":
        return arg.default
    return double_quote(arg.default)


def python_type(type_: str) -> str:
    """convert from .toml to python type"""
    if type_ == "string":
        return "str"
    return type_


def format_list(lst: list) -> str:
    """format default list as expected by cxx options from .toml format"""
    return "[" + (", ".join(double_quote(item) for item in lst)) + "]"


class PythonCodeGenerator(CodeGenerator):
    """Generates Python argparse code for CLI parsing."""

    def generate_code(self, filename_base: str) -> None:
        """generate .py file"""
        c = Emitter()

        c.emit('"""CLI argument parsing"""')
        c.new_line()
        c.emit("import argparse\n")
        c.new_line()

        # Import and argparse setup
        c.emit("def parse_args() -> tuple:")
        with Indenter(c):
            c.emit('"""CLI argument parsing entry point"""')
            with Indenter(c, "parser = argparse.ArgumentParser(", ")"):
                c.emit(f'description="{self.description}",')
                c.emit(
                    "formatter_class=argparse.ArgumentDefaultsHelpFormatter,"
                )
                c.emit(f'epilog="{self.epilog}",')

            # Process each argument
            for arg in self.args:
                opts = []

                # short option
                if arg.short != "":
                    opts.append(double_quote(arg.short))

                # long option or positional
                opts.append(double_quote(arg.name))

                # type
                if arg.type_ == "flag":
                    flag_action = (
                        "store_false" if arg.default else "store_true"
                    )
                    opts.append(f'action="{flag_action}"')
                else:
                    opts.append(f"type={python_type(arg.type_)}")

                # destination
                if arg.dest != arg.clean_name:
                    opts.append(f'dest="{arg.dest}"')

                # default
                if arg.has_default:
                    if arg.type_ != "flag":
                        opts.append(f"default={get_default(arg)}")
                elif not arg.is_positional:
                    opts.append("required=True")

                # metavar
                if arg.has_metavar:
                    opts.append(f'metavar="{arg.metavar}"')

                # nargs
                if arg.multiple:
                    opts.append('nargs="+"')

                # choices
                if arg.choices is not None:
                    opts.append(f"choices={arg.choices}")

                # help
                opts.append(f'help="{arg.help_}"')

                with Indenter(c, "parser.add_argument(", ")"):
                    for opt in opts:
                        c.emit(f"{opt},")

            # Parse args, including retaining arguments after "--"
            c.new_line()
            c.emit("return parser.parse_known_args()  # args, unknown")
        c.new_line()
        c.new_line()

        c.emit('if __name__ == "__main__":')
        with Indenter(c):
            c.emit("args, unknown = parse_args()")
            c.emit('print(f"Parsed arguments: {args}")')
            c.emit("if unknown:")
            with Indenter(c):
                c.emit('print(f"Unknown arguments: {unknown}")\n')

        self.to_file(str(c), filename_base + ".py")
