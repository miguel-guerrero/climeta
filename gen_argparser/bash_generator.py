"""
Generate CLI parsing code in bash
"""

from .code_generator import (
    ArgSpec,
    CodeGenerator,
    double_quote,
)
from .bash_emitter import BashEmitter


def formatted_init_default(arg: ArgSpec) -> str:
    """get default value for an option"""
    assert arg.has_default

    def format_one(value) -> str:
        if arg.type_ == "flag":
            value = "1" if value else "0"
        return double_quote(value)

    if arg.multiple:
        return double_quote(" ".join(str(item) for item in arg.default))
    return format_one(arg.default)


def help_default(arg: ArgSpec) -> str:
    """default formatted for help string"""

    if not arg.has_default:
        return "required"

    def format_one(value) -> str:
        if arg.type_ == "flag":
            value = "1" if value else "0"
        return double_quote(value)

    if arg.multiple:
        return "default " + " ".join(format_one(item) for item in arg.default)
    return "default " + format_one(arg.default)


class BashCodeGenerator(CodeGenerator):
    """Generates Bash code for CLI parsing."""

    def _generate_usage(self, c: BashEmitter) -> None:
        """generate the usage() function"""
        c.cmnt("Usage function")
        with c.func("usage"):
            c.echo("Usage: $0 [options]")
            c.echo("")
            c.echo(self.description)
            c.echo("")
            left_side_help = ["-h, --help"]
            right_side_help = ["show this help message and exit"]
            for arg in self.args:
                default = help_default(arg)
                opt_str = arg.get_opt_string()
                left_side_help.append(opt_str)
                right_side_help.append(f"{arg.help_} ({default})")

            left_size = 1 + max(len(txt) for txt in left_side_help)

            c.echo("positional arguments:")
            for left_side, right_side in zip(left_side_help, right_side_help):
                if not left_side.startswith("-"):
                    padded_left_help = left_side + " " * (
                        left_size - len(left_side)
                    )
                    c.echo(f"  {padded_left_help}: {right_side}")

            c.echo("")
            c.echo("options:")
            for left_side, right_side in zip(left_side_help, right_side_help):
                if left_side.startswith("-"):
                    padded_left_help = left_side + " " * (
                        left_size - len(left_side)
                    )
                    c.echo_literal(f"  {padded_left_help}: {right_side}")

            if self.epilog:
                c.echo("")
                c.echo(self.epilog)
            c.emit('exit "$1"')

    def _generate_arg_checker(self, c: BashEmitter) -> None:
        """To check if a valid argument follows"""
        c.cmnt("check if a valid argument follows")
        with c.func("check_valid_arg"):
            with c.case("$2"):
                with c.case_pattern("-*|''"):
                    c.error("$1 requires a value.")
                    c.emit("usage 1")

    def _generate_dump_args(self, c: BashEmitter) -> None:
        """dump_args function"""
        c.cmnt("Dump argument values for debug")
        with c.func("dump_args"):
            c.echo("Parsed arguments:")
            for arg in self.args:
                if arg.multiple:
                    c.echo(f"{arg.dest}:")
                    with c.for_loop("arg", "${" + arg.dest + "}"):
                        c.echo("  $arg")
                else:
                    c.echo(f"{arg.dest}: ${arg.dest}")
            c.echo("remaining_args:")
            with c.for_loop("arg", "$remaining_args"):
                c.echo("  $arg")

    def _generate_arg_validator(self, c: BashEmitter) -> None:
        """Validate arguments"""
        c.cmnt("Validate arguments")
        first = True
        with c.func("validate_args"):
            for arg in self.args:
                if arg.is_required:
                    with c.if_then(f'-z "${arg.dest}"'):
                        c.error(f"{arg.name} is required")
                        c.emit("usage 1")
                if arg.choices is not None:
                    if first:
                        c.emit("local match")
                        first = False
                    pattern = "|".join(arg.choices)
                    choices_str = ", ".join(arg.choices)
                    c.emit(f'match=$(expr "|{pattern}|" : ".*|${arg.dest}|")')
                    with c.if_then('"$match" -eq 0'):
                        c.error(
                            f"{arg.name} must be one of: {choices_str} (got '${arg.dest}')"
                        )
                        c.emit("usage 1")

    def _generate_get_cli(self, c: BashEmitter) -> None:
        """Main entry point function"""
        c.cmnt("Main entry point, parse CLI")
        with c.func("get_cli_args"):
            # set defaults
            c.cmnt("set defaults")
            for arg in self.args:
                if not arg.is_required:
                    default_value = formatted_init_default(arg)
                    c.emit(f"{arg.dest}={default_value}")
            c.emit('parse_args "$@"')
            c.emit("validate_args")

    def _generate_getopts_emulation(self, c: BashEmitter) -> None:
        """this portion performs similar functionality to getopt/getopts"""
        c.cmnt("split --a=xx -b=yy -cde into --a xx -b yy -c -d -e")
        c.cmnt("for more unified processing later on")
        c.emit("local i ch arg")
        c.emit("local -a new_args")

        with c.for_loop("arg", '"$@"'):
            with c.case("$arg"):
                with c.case_pattern("--*=*", "# convert --aa=xx into --aa xx"):
                    c.emit("right=${arg#*=}  # remove up to first =")
                    c.emit('left=${arg%="$right"}  # remove right hand side')
                    c.emit('new_args+=("$left" "$right")')
                with c.case_pattern("--*"):
                    c.emit('new_args+=("$arg")')
                with c.case_pattern(
                    "-*", "# convert -abc=yy into -a -b -c yy"
                ):
                    c.emit("i=1")
                    with c.while_loop('"$i" -lt "${#arg}"'):
                        c.cmnt("Get character at position i (0 based)")
                        c.emit(r'ch=$(expr "$arg" : "^.\{$i\}\(.\)")')
                        with c.case("${ch}"):
                            c.emit(
                                r'=) rest=$(expr "$arg" : "^..\{$i\}\(.*\)")'
                            )
                            c.emit('   new_args+=("$rest"); break ;;')
                            c.emit('*) new_args+=("-${ch}") ;;')
                        c.emit("i=$((i+1))")
                with c.case_pattern("*"):
                    c.emit('new_args+=("$arg")')

        c.emit('set -- "${new_args[@]}"\n')
        # main per argument processing code
        c.emit('remaining_args=""')
        c.emit("local positional_idx=0")

    def _generate_parsing_loop(self, c: BashEmitter) -> None:
        """generate main processing argument loop"""
        with c.while_loop('"$#" -gt 0'):
            with c.case("$1"):
                # process -- and - options
                for arg in self.args:
                    if not arg.is_positional:  # non-positional arguments
                        pattern = (
                            f"{arg.name}|{arg.short}"
                            if arg.short != ""
                            else arg.name
                        )
                        if arg.type_ == "flag":
                            val = 0 if arg.default else 1
                            with c.case_pattern(pattern):  # handle flags
                                c.emit(f'{arg.dest}="{val}"')
                        else:
                            # Handle options that require a value
                            with c.case_pattern(
                                pattern, post="shift"
                            ):  # handle flags
                                c.emit('check_valid_arg "$1" "$2"')
                                c.emit(f'{arg.dest}="$2"')

                # boiler plate to handle help, -- and unkown options
                with c.case_pattern("--help|-h"):
                    c.emit("usage 0")
                with c.case_pattern("--"):
                    c.emit("shift")
                    c.emit('remaining_args="$*"')
                    c.emit("break")
                with c.case_pattern("-*"):
                    c.error("Unknown option: $1")
                    c.emit("usage 1")

                # handle positional arguments
                pos_idx = 0
                with c.case_pattern("*", "# handle positional arguments"):
                    for arg in self.args:
                        if arg.is_positional:
                            if pos_idx == 0:
                                with c.if_then_else("$positional_idx -eq 0"):
                                    c.emit(f'{arg.dest}="$1"')
                            else:
                                with c.elif_("$positional_idx -eq {pos_idx}"):
                                    c.emit(f'{arg.dest}="$1"')
                            pos_idx += 1
                    if pos_idx > 0:  # if there was any positional
                        with c.else_():
                            c.error("Unexpected positional argument: $1")
                            c.emit("usage 1")
                        c.emit("positional_idx=$(( positional_idx + 1 ))")
                    else:  # there was no positional expected
                        c.error("Unexpected positional argument: $1")
                        c.emit("usage 1")
            c.emit("shift")

    def generate_code(self, filename_base: str) -> None:
        c = BashEmitter()

        self._generate_usage(c)
        self._generate_arg_checker(c)

        # Main argument parsing function
        c.cmnt("Argument parsing function")
        with c.func("parse_args"):
            # this portion performs similar functionality to getopt/getopts
            # in the sense that it splits collapsed options and replaces =
            # in --arg=value into --arg value to simplify later processing
            self._generate_getopts_emulation(c)
            # parsing loop with simplified command line
            self._generate_parsing_loop(c)

        # Validate arguments
        self._generate_arg_validator(c)

        # dump_args function
        self._generate_dump_args(c)

        # Main function
        self._generate_get_cli(c)

        # Example: call get_cli_args function
        c.cmnt("Example of use:")
        c.cmnt('get_cli_args "$@"')
        c.cmnt("dump_args")

        self.to_file(str(c), filename_base + ".sh")
