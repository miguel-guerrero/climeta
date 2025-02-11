"""
Generate CLI parsing code in C++ using cxxopt library dependency
"""

from .code_generator import (
    ArgSpec,
    CodeGenerator,
    double_quote,
    single_quote,
)
from .cpp_emitter import CppEmitter
from .indenter import Indenter


def get_cpp_type(type_: str, multiple: bool) -> str:
    """translate from .toml argument type to C++ implemented type including vector if needed"""
    cpp_type = {
        "string": "std::string",
        "flag": "bool",
    }.get(type_, type_)
    if multiple:
        return "std::vector<" + cpp_type + ">"
    return cpp_type


def get_default_init(arg: ArgSpec) -> str:
    """build default string to pass to default c++ method"""
    if arg.has_default and arg.type_ != "flag":
        default = arg.default
        if arg.type_ == "flag":
            default = "false"  # could be internally inverted
        if arg.multiple:
            default = ",".join(str(item) for item in default)
        return f'->default_value("{default}")'
    return ""


def get_help_str(arg: ArgSpec) -> str:
    """return help string, potentially augmented with default/required"""
    help_ = arg.help_
    if not arg.has_default:
        help_ += " (required)"
    elif arg.type_ == "flag":
        help_ += " (default: false)"
    # for other cases the underlaying lib prints default
    return help_


class CppCxxoptsCodeGenerator(CodeGenerator):
    """Generates C++ argparse code for CLI parsing."""

    def generate_code(self, filename_base: str) -> None:
        """generate .cpp and .hpp files"""
        self.generate_c_code(filename_base)
        self.generate_h_code(filename_base)

    def _generate_check_choices_block(self, c: CppEmitter) -> None:
        """
        Generates a block of code that generates a checker
        for 'choices' arguments being one of the correct specified
        choices
        """
        # // check choices
        # std::set<std::string> input_valid{"aa", "bb"};
        # if (input_valid.find(opts->input) == input_valid.end()) {
        #     std::cout << "ERROR: input must be one of 'aa', 'bb'" << std::endl;
        #     std::cout << options.help() << std::endl;
        #     exit(1);
        # }
        c.cmnt("check choices")
        for arg in self.args:
            if arg.choices is not None:
                long = arg.clean_name
                choices_dbl_quoted = ", ".join(
                    double_quote(choice) for choice in arg.choices
                )
                choices_sgl_quoted = ", ".join(
                    single_quote(choice) for choice in arg.choices
                )
                c.emit(
                    "std::set<std::string> "
                    + long
                    + "_valid{"
                    + choices_dbl_quoted
                    + "};"
                )
                with c.if_then(
                    f"{long}_valid.find(opts->{arg.dest}) == {long}_valid.end()"
                ):
                    c.emit(
                        f"std::cout << \"ERROR: '{long}' must be one of "
                        + choices_sgl_quoted
                        + '" << std::endl;'
                    )
                    c.emit("exit(1);")

    def _generate_option_struct(self, c: CppEmitter) -> None:
        """
        generate the control structure that defines the options in the
        underlaying library
        """
        c.cmnt("define all options")
        c.emit("options.add_options()")
        with Indenter(c):
            c.emit('("h,help", "show this help message and exit")')
            for arg in self.args:
                help_ = get_help_str(arg)
                default = get_default_init(arg)
                long = arg.clean_name
                short = arg.clean_short
                if short != "":
                    short += ","
                cpp_type = get_cpp_type(arg.type_, arg.multiple)
                c.emit(
                    f'("{short}{long}", "{help_}", cxxopts::value<{cpp_type}>(){default})'
                )
        c.emit(";")

    def _generatel_help_block(
        self, c: CppEmitter, num_positionals: int
    ) -> None:
        """
        generate block that shows help
        """
        #     if (result.count("help")) {
        #       std::cout << options.help() << std::endl;
        #       ... help on positionals
        #       exit(0);
        #     }
        with Indenter(c, 'if (result.count("help")) {', "}"):
            c.emit("std::cout << options.help() << std::endl;")
            if num_positionals > 0:
                c.emit('std::cout << "positional arguments:\\n";')
                for arg in self.args:
                    if arg.is_positional:
                        padding = " " * max(0, 17 - len(arg.name))
                        c.emit(
                            f'std::cout << "  {arg.name} {padding}"'
                            + f' << "{arg.help_} (required)\\n";'
                        )
            c.emit(f'std::cout << "\\n{self.epilog}" << std::endl;')
            c.emit("exit(0);")

    def _generate_fillup_options_block(self, c: CppEmitter) -> None:
        """
        generate the code that fills-up each option from the
        resulting Option struct
        """
        #     opts->input = result["input"].as<std::string>();
        #     opts->debug = result["debug"].as<bool>();
        #     opts->bar = result["bar"].as<std::string>();
        #     opts->foo = result["foo"].as<int>();
        c.cmnt("Fill-up output struct")
        for arg in self.args:
            long = arg.clean_name
            dest = arg.dest
            cpp_type = get_cpp_type(arg.type_, arg.multiple)
            if arg.type_ == "flag" and arg.default:
                c.emit(
                    f'opts->{dest} = !result["{long}"].as<{cpp_type}>(); // invert back'
                )
            else:
                c.emit(f'opts->{dest} = result["{long}"].as<{cpp_type}>();')

    def generate_c_code(self, filename_base: str):
        """generate .c code"""
        c = CppEmitter()

        any_arg_is_choices = any(arg.choices is not None for arg in self.args)

        c.include(filename_base + ".hpp")
        c.include_sys("iostream")
        if any_arg_is_choices:
            c.include_sys("set")
        c.new_line()
        c.new_line()

        # cxxopts::ParseResult parse_options(int argc, char** argv, Options* opts) {
        #     cxxopts::Options options("test", "A brief description");
        #     // options
        #     options.add_options()
        #         ("h,help", "show this help message and exit")
        #         ("input", "input file", cxxopts::value<std::string>())
        #         ("b,bar", "Param bar", cxxopts::value<std::string>())
        #         ("d,debug", "Enable debugging", cxxopts::value<bool>()->default_value("false"))
        #         ("f,foo", "Param foo", cxxopts::value<int>()->default_value("10"))
        #     ;
        #     // positionals
        #     options.parse_positional("input");
        #     cxxopts::ParseResult result = options.parse(argc, argv);
        #     ...

        with c.func(
            "parse_options",
            ["int argc", "const char **argv", "Options* opts"],
            ret="cxxopts::ParseResult",
        ):
            c.emit(
                f'cxxopts::Options options("{self.program_name}", "{self.description}");'
            )

            self._generate_option_struct(c)

            num_positionals = sum(1 for arg in self.args if arg.is_positional)
            if num_positionals > 0:
                c.cmnt("declare positionals")
                for arg in self.args:
                    if arg.is_positional:
                        c.emit(f'options.parse_positional("{arg.name}");')

            c.new_line()
            c.emit("cxxopts::ParseResult result = options.parse(argc, argv);")
            self._generatel_help_block(c, num_positionals)
            self._generate_fillup_options_block(c)

            # if there is any 'choices' option, check here
            if any_arg_is_choices:
                self._generate_check_choices_block(c)

            c.emit("return result;")

        with c.func("dump_options", ["const Options &opts"]):
            for arg in self.args:
                dest = arg.dest
                if arg.multiple:
                    c.emit(f'std::cout << "{dest}:\\n";')
                    with c.for_list_loop("const auto& item", f"opts.{dest}"):
                        c.emit('std::cout << "  " << item << "\\n";')
                else:
                    c.emit(f'std::cout << "{dest}: " << opts.{dest} << "\\n";')

        self.to_file(str(c), filename_base + ".cpp")

    def generate_h_code(self, filename_base: str) -> None:
        """generate .hpp code"""
        c = CppEmitter()

        c.header_guard_begin(filename_base)

        c.include("cxxopts.hpp")

        c.emit("struct Options {")
        with Indenter(c):
            for arg in self.args:
                if not arg.is_positional:
                    cpp_type = get_cpp_type(arg.type_, arg.multiple)
                    c.emit(f"{cpp_type} {arg.dest};")

            c.cmnt("positionals")
            for arg in self.args:
                if arg.is_positional:
                    cpp_type = get_cpp_type(arg.type_, arg.multiple)
                    c.emit(f"{cpp_type} {arg.dest};")
        c.emit("};")

        c.new_line()
        c.emit(
            "cxxopts::ParseResult parse_options(int argc, const char** argv, Options* opts);"
        )
        c.emit("void dump_options(const Options& opts);")

        c.header_guard_end()

        self.to_file(str(c), filename_base + ".hpp")
