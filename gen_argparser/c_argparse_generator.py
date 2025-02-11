"""
Generate CLI parsing code in C using c_argparse library dependency
"""

from .code_generator import (
    ArgSpec,
    CodeGenerator,
    double_quote,
    double_quote_list,
    single_quote_list,
)
from .c_emitter import CEmitter
from .indenter import Indenter


def get_default(arg: ArgSpec) -> str:
    """get default value for a given option"""
    if arg.has_default:
        if arg.type_ == "flag":
            return "1" if arg.default else "0"
        if arg.type_ == "string":
            return double_quote(arg.default)
        return str(arg.default)
    return {
        "string": "NULL",
        "int": "INT_MIN",
        "float": "NAN",
    }[arg.type_]


def get_printf_type(type_: str) -> str:
    """get printf style %x string for a given type"""
    return {
        "string": "s",
        "int": "d",
        "float": "f",
        "flag": "d",
    }[type_]


def ungiven_default(type_: str) -> str:
    """return the value used as sentinel to detect the value was not given"""
    # check it has been given
    return {
        "string": "NULL",
        "int": "INT_MIN",
        "float": "NAN",
    }[type_]


def get_ctype(type_: str) -> str:
    """translate from .toml argument type to C implemented type"""
    return {
        "string": "const char *",
        "flag": "int",
    }.get(type_, type_)


def get_opt_type(type_: str) -> str:
    """map from type to option macro name"""
    return {
        "flag": "OPT_BOOLEAN",
        "int": "OPT_INTEGER",
        "float": "OPT_FLOAT",
        "string": "OPT_STRING",
    }[type_]


def get_help_suffix(arg: ArgSpec) -> str:
    """
    Generates a suffix for user provided help line to
    indicate if the argument is required or its default
    value
    """
    if arg.is_required:
        return "(required)"

    if arg.type_ == "flag":
        default = "0"
    else:
        default = get_default(arg)
        default = default.replace('"', "'")
    return f"(default {default})"


class CArgparseCodeGenerator(CodeGenerator):
    """Generates C argparse code for CLI parsing."""

    def generate_code(self, filename_base: str) -> None:
        """generate .c and .h files"""
        self.generate_c_code(filename_base)
        self.generate_h_code(filename_base)

    def _generate_reset_options(self, c: CEmitter) -> None:
        """generate reset_options() function which sets a
        default for all options or a sentinel if they don't have
        one"""
        # void reset_options(Options* opts) {
        #     opts->force = 0;
        #     opts->test = 0;
        #     opts->int_num = 0;
        #     opts->flt_num = 0.f;
        #     opts->path = NULL;
        #     opts->positional = NULL;
        # }
        with c.func("reset_options", ["Options* opts"]):
            for arg in self.args:
                default = get_default(arg)
                suffix = ""
                if arg.type_ == "flag":
                    if default == "1":
                        default = "0"
                        suffix = " // inverted internal polarity"
                c.emit(f"opts->{arg.dest} = {default};{suffix}")

    def _generate_set_includes(self, c: CEmitter) -> None:
        """
        Generates function to check if a string is in an
        array of strings, used for 'choices' arguments only
        """
        # static int set_includes(const char* words[], const char* test_word) {
        #   while (*words != NULL) {
        #       if (strcmp(*words++, test_word) == 0) {
        #           return 1;
        #       }
        #   }
        #   return 0;
        # }
        with c.static_func(
            "set_includes",
            ["const char* words[]", "const char* test_word"],
            ret="int",
        ):
            with c.while_loop("*words != NULL"):
                with c.if_then("strcmp(*words++, test_word) == 0"):
                    c.emit("return 1;")
            c.emit("return 0;")

    def _generate_option_struct(self, c: CEmitter) -> None:
        """
        generate the control structure that defines the options in the
        underlaying library
        """
        #     struct argparse_option options[] = {
        #         OPT_HELP(),
        #         OPT_GROUP("Basic options"),
        #         OPT_BOOLEAN('f', "force", &opts->force, "force to do", NULL, 0, 0),
        #         OPT_BOOLEAN('t', "test", &opts->test, "test only", NULL, 0, 0),
        #         OPT_STRING('p', "path", &opts->path, "path to read", NULL, 0, 0),
        #         OPT_INTEGER('i', "int", &opts->int_num, "selected integer", NULL, 0, 0),
        #         OPT_FLOAT('s', "float", &opts->flt_num, "selected float", NULL, 0, 0),
        #         OPT_END(),
        #     };
        with Indenter(c, "struct argparse_option options[] = {", "};"):
            c.emit("OPT_HELP(),")
            # Process each argument
            for arg in self.args:
                if arg.is_positional:
                    continue
                if arg.multiple:
                    raise RuntimeError(
                        "c_argparse_generator does not support 'multiple' yet"
                    )
                short = arg.clean_short if arg.clean_short != "" else "\\0"
                long = arg.clean_name
                help_ = arg.help_ + " " + get_help_suffix(arg)
                c.emit(
                    f"{get_opt_type(arg.type_)}('{short}', \"{long}\", "
                    f'&opts->{arg.dest}, "{help_}", NULL, 0, 0),'
                )
            c.emit("OPT_END(),")

    def _generatel_help_block(self, c: CEmitter) -> None:
        """generate help, append positional help at the end"""
        c.emit("argparse_describe(&argparse, ")
        num_positionals = sum(1 for arg in self.args if arg.is_positional)
        with Indenter(c):
            c.emit(f'"\\n{self.description}",')
            if num_positionals > 0:
                c.emit('"\\nPositional arguments:"')
                for arg in self.args:
                    if arg.is_positional:
                        long = arg.clean_name
                        help_ = arg.help_
                        padding = " " * max(1, 22 - len(long))
                        c.emit(f'"\\n    {long}{padding}{help_}\\n"')

            c.emit(f'"\\n{self.epilog}"')
        c.emit(");")

    def _generate_check_choices_block(self, c: CEmitter) -> None:
        """
        Generates a block of code that generates a checker
        for 'choices' arguments being one of the correct specified
        choices
        """
        # // check choices
        # const char *lang_valid[] = {"python", "bash", NULL};
        # if (!set_includes(lang_valid, opts->lang)) {
        #     printf("ERROR: 'lang' must be one of 'python', 'bash'\n");
        #     exit(1);
        # }
        c.cmnt("check choices")
        for arg in self.args:
            if (choices := arg.choices) is not None:
                long = arg.clean_name
                c.emit(
                    f"const char *{long}_valid[] = "
                    + f"{{{double_quote_list(choices)}, NULL}};"
                )
                with c.if_then(
                    f"!set_includes({long}_valid, opts->{arg.dest})"
                ):
                    c.emit(
                        f"printf(\"ERROR: '{long}' must be one of "
                        f'{single_quote_list(choices)}\\n");'
                    )
                    c.emit("exit(1);")

    def _generate_assing_positionals_block(self, c: CEmitter) -> None:
        """assign argv positional values to Options struct named positionals"""
        c.cmnt("positionals")
        for arg in self.args:
            if not arg.is_positional:
                continue

            long = arg.clean_name

            c.emit("if (argc >= 1) {")
            c.emit(f"    opts->{long} = (*argv)[0];")
            c.emit("    (*argv)++; argc--;")
            c.emit("} else {")
            c.emit(
                f"    printf(\"ERROR: expecting positional argument '{long}'\\n\");"
            )
            c.emit("    argparse_usage(&argparse);")
            c.emit("    exit(1);")
            c.emit("}")

    def _generate_flag_inverter_block(self, c: CEmitter) -> None:
        """
        for flags that are internally inverted (the ones that default to true
        externally), invert back the value for the user. We use internally inverted
        flags because the underlaying library only supports flags that default to
        false
        """
        for arg in self.args:
            if not arg.is_positional:
                if arg.type_ == "flag" and get_default(arg) != "0":
                    # when flag default is true, we invert the meaning
                    c.emit(
                        f"opts->{arg.dest} = 1 - opts->{arg.dest};  // invert back"
                    )

    def _generate_check_missing_args_block(self, c: CEmitter) -> None:
        """
        for option arguments that are required, check if the value was
        provided
        """
        for arg in self.args:
            if not arg.is_positional and not arg.has_default:
                # check it has been given
                cond = f"opts->{arg.dest} == {ungiven_default(arg.type_)}"
                c.cmnt(f"check if {arg.name} has been given")
                with c.if_then(cond):
                    c.emit(
                        f"printf(\"ERROR: expecting required argument '{arg.name}'\\n\");"
                    )
                    c.emit("argparse_usage(&argparse);")
                    c.emit("exit(1);")

    def _generate_dump_options(self, c: CEmitter) -> None:
        with c.func("dump_options", ["Options *opts"]):
            for arg in self.args:
                dest = arg.dest
                perc = get_printf_type(arg.type_)
                c.emit(f'printf("{dest}: %{perc}\\n", opts->{dest});')

    def generate_c_code(self, filename_base: str):
        """generate .c code"""
        c = CEmitter()

        c.include(filename_base + ".h")
        c.include("argparse.h")
        c.include_sys("stdio.h", "stdlib.h", "string.h", "limits.h", "math.h")
        c.emit("\n")

        self._generate_reset_options(c)

        any_arg_is_choices = any(arg.choices is not None for arg in self.args)
        if any_arg_is_choices:
            self._generate_set_includes(c)

        with c.func(
            "parse_options",
            ["int argc", "const char ***argv", "Options* opts"],
            ret="int",
        ):
            # int parse_options(int argc, const char ***argv, Options* opts) {
            #     static const char *const usages[] = {
            #         "basic [options] positionals [[--] args]",
            #         "basic [options] positionals ",
            #         NULL,
            #     };
            #     reset_options(opts);
            with Indenter(c, "static const char *const usages[] = {", "};"):
                c.emit('"basic [options] positionals [[--] args]",')
                c.emit('"basic [options] positionals ",')
                c.emit("NULL,")
            c.emit("reset_options(opts);")

            self._generate_option_struct(c)

            c.emit("struct argparse argparse;")
            c.emit("argparse_init(&argparse, options, usages, 0);")

            # generate help, append positional help at the end
            self._generatel_help_block(c)

            c.emit("argc = argparse_parse(&argparse, argc, *argv);")

            self._generate_assing_positionals_block(c)
            self._generate_flag_inverter_block(c)
            self._generate_check_missing_args_block(c)

            # if there is any 'choices' option, check here
            if any_arg_is_choices:
                self._generate_check_choices_block(c)

            c.emit("return argc;")

        self._generate_dump_options(c)

        self.to_file(str(c), filename_base + ".c")

    def generate_h_code(self, filename_base: str) -> None:
        """generate .h file"""
        c = CEmitter()

        c.header_guard_begin(filename_base)

        c.emit("typedef struct {")
        with Indenter(c):
            for arg in self.args:
                if not arg.is_positional:
                    c.emit(f"{get_ctype(arg.type_)} {arg.dest};")

            c.cmnt("positionals")
            for arg in self.args:
                if arg.is_positional:
                    c.emit(f"{get_ctype(arg.type_)} {arg.dest};")
        c.emit("} Options;")

        c.extern_c_begin()
        c.emit("void reset_options(Options* opts);")
        c.emit(
            "int parse_options(int argc, const char ***argv, Options* opts);"
        )
        c.emit("void dump_options(Options *opts);")
        c.extern_c_end()

        c.header_guard_end()

        self.to_file(str(c), filename_base + ".h")
