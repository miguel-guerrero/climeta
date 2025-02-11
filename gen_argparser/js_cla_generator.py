"""
Generate CLI parsing code in C using c_argparse library dependency
"""

import re

from .code_generator import (
    ArgSpec,
    CodeGenerator,
    double_quote,
)
from .js_emitter import JavaScriptEmitter
from .indenter import Indenter


def get_default(arg: ArgSpec) -> str:
    """get default value for a given option"""
    type_ = arg.type_
    if arg.has_default:
        default = arg.default
        if type_ == "flag":
            return "true" if default else "false"
        if type_ == "string":
            if arg.multiple:
                return " ".join(str(item) for item in default)
            return double_quote(default)
        return default
    return "null"


def format_list(x: str) -> str:
    """format default list as expected by cxx options from .toml format"""
    lst = re.split(r" +", x)
    return "[" + (", ".join(double_quote(item) for item in lst)) + "]"


def get_jstype(type_: str) -> str:
    """translate from .toml argument type to C implemented type"""
    return {
        "string": "String",
        "flag": "Boolean",
        "int": "Number",
        "float": "Number",
    }[type_]


class JavaScriptCommandLineArgsCodeGenerator(CodeGenerator):
    """Generates JS command-line-args code for CLI parsing for node."""

    def _generate_help(self, c: JavaScriptEmitter) -> None:
        with c.func("usage", ["optionDefinitions", "rc = 0"]):
            c.emit("const usageText = commandLineUsage([{")
            c.emit('  header: "Header for help",')
            c.emit('  content: "Description for help",')
            c.emit("}, {")
            c.emit('  header: "Options",')
            c.emit("  optionList: optionDefinitions,")
            c.emit("}, {")
            c.emit('  content: "Epilog"')
            c.emit("}]);")
            c.emit("console.log(usageText);")
            c.emit("process.exit(rc);")

    def _generate_option_defaults_block(self, c: JavaScriptEmitter) -> None:
        # // Defaults for each of the options
        # const defaults = {
        #   help: false,
        #   flag: false,
        #   flag2: false,
        #   str: null,  // required
        #   number: 1,
        # };

        c.cmnt("Defaults for each of the options")
        with Indenter(c, "const defaults = {", "};"):
            for arg in self.args:
                if not arg.is_positional:
                    long = arg.clean_name
                    default = get_default(arg)
                    suffix = ""
                    if arg.type_ == "flag":
                        if default == "true":
                            default = "false"
                            suffix = " // inverted internal polarity"
                    if arg.multiple:
                        default = format_list(default)
                    c.emit(f"{long}: {default},{suffix}")

    def _generate_option_struct_block(self, c: JavaScriptEmitter) -> None:
        # const optionDefinitions = [
        #   {
        #     name: 'help',
        #     description: 'show this help message and exit',
        #     alias: 'h',
        #     type: Boolean
        #   },
        #   {
        #     name: 'flag',
        #     description: 'example of a flag',
        #     alias: 'f',
        #     type: Boolean
        #   },
        #   {
        #     name: 'str',
        #     description: 'example of a string (required)',
        #     alias: 's',
        #     type: String
        #   },
        #   {
        #     name: 'number',
        #     description: 'example of a number',
        #     alias: 'n',
        #     type: Number
        #   },
        #   {
        #     name: 'positionals',
        #     description: 'positional arguments',
        #     type: String,
        #     multiple: true,
        #     defaultOption: true,
        #   },
        # ]
        with Indenter(c, "const optionDefinitions = [", "];"):
            with Indenter(c, "{", "},"):
                c.emit("name: 'help',")
                c.emit("description: 'show this help message and exit',")
                c.emit("alias: 'h',")
                c.emit("type: Boolean")

            for arg in self.args:
                if not arg.is_positional:
                    long = arg.clean_name
                    short = arg.clean_short
                    jstype = get_jstype(arg.type_)
                    help_ = arg.help_
                    with Indenter(c, "{", "},"):
                        c.emit(f"name: '{long}',")
                        c.emit(f"description: '{help_}',")
                        if short != "":
                            c.emit(f"alias: '{short}',")
                        if arg.multiple:
                            c.emit("multiple: true,")
                        c.emit(f"type: {jstype}")

            cnt_positionals = sum(1 for arg in self.args if arg.is_positional)
            if cnt_positionals > 0:
                with Indenter(c, "{", "},"):
                    c.emit("name: 'positionals',")
                    help_ = "positional arguments (can omit --positionals) "
                    help_ += "Corresponding to:"
                    for arg in self.args:
                        if arg.is_positional:
                            pos_name = "{bold " + arg.clean_name + "}"
                            pos_help = arg.help_
                            help_ += f"\\n>> {pos_name} : {pos_help}"
                    c.emit(f"description: '{help_}',")
                    c.emit("type: String,")
                    c.emit("multiple: true,")
                    c.emit("defaultOption: true")

    def _augment_help_info(self, c: JavaScriptEmitter) -> None:
        """append default to help string"""
        # for (const opt of optionDefinitions) {
        #   const default_ = defaults[opt.name]
        #   if (typeof default_ !== "undefined") {
        #     opt.description += default_ == null ? " (required)" : ` (default ${default_})`
        #   }
        # }
        c.cmnt("append default to help string")
        with c.for_of_loop("const opt", "optionDefinitions"):
            c.emit("const default_ = defaults[opt.name];")
            with c.if_then('typeof default_ !== "undefined"'):
                c.emit(
                    "opt.description += default_ == null ?"
                    ' " (required)" : ` (default ${default_})`;'
                )

    def _generate_assing_positionals_block(self, c: JavaScriptEmitter) -> None:
        """assing positional values to Options struct named positionals"""

        # const num_positionals = (typeof opts.positionals === "undefined")
        #                       ? 0 : opts.positionals.length
        #   if (num_positionals != 2) {
        #     console.log(`Expecting 2 positional argument(s), but got ${num_positionals}`)
        #     usage(optionDefinitions, 1)
        # }
        # opts.pos1 = opts.positionals[0]
        # opts.pos2 = opts.positionals[1]
        # delete opts.positionals

        c.cmnt("Handle positionals")
        cnt_positionals = sum(1 for arg in self.args if arg.is_positional)
        c.emit(f"const exp_positionals = {cnt_positionals}")
        c.emit(
            'const num_positionals = (typeof opts.positionals === "undefined")'
            " ? 0 : opts.positionals.length;"
        )
        with c.if_then("num_positionals != exp_positionals"):
            c.emit(
                "console.log(`Expecting ${exp_positionals} positional argument(s), "
                "but got ${num_positionals}`);"
            )
            c.emit("usage(optionDefinitions, 1);")
        i = 0
        for arg in self.args:
            if arg.is_positional:
                c.emit(f"opts.{arg.dest} = opts.positionals[{i}];")
                i += 1
        c.emit("delete opts.positionals;")

    def _generate_check_choices_block(self, c: JavaScriptEmitter) -> None:
        # // check choices
        # const lang_valid = ["python", "bash"]
        # if (!lang_valid.includes(opts.lang)) {
        #       console.log("ERROR: 'lang' must be one of", lang_valid)
        #       process.exit(1)
        # }
        first = True
        for arg in self.args:
            if (choices := arg.choices) is not None:
                long = arg.clean_name
                choices_dbl_quoted = ", ".join(
                    double_quote(choice) for choice in choices
                )
                if first:
                    c.cmnt("check choices")
                    first = False
                c.emit(f"const {long}_valid = [{choices_dbl_quoted}];")
                with c.if_then(f"!{long}_valid.includes(opts.{arg.dest})"):
                    c.emit(
                        f"console.log(\"ERROR: '{long}' must be one of\", {long}_valid);"
                    )
                    c.emit("process.exit(1);")

    def _generate_name_translation_block(self, c: JavaScriptEmitter) -> None:
        """
        translate from external to internal name
        invert polarity of flag (internally all flags default to false) if
        defaulting to true externally
        """
        first = True
        for arg in self.args:
            dest = arg.dest
            long = arg.clean_name
            if dest != long:
                if first:
                    c.cmnt("translate from external to internal name")
                    first = False
                if arg.type_ == "flag" and arg.default:
                    c.emit(f"opts.{dest} = !opts.{long};  // invert")
                else:
                    c.emit(f"opts.{dest} = opts.{long};")
                c.emit(f"delete opts.{long}")

    def generate_code(self, filename_base: str) -> None:
        c = JavaScriptEmitter()

        c.cmnt("https://github.com/75lb/command-line-args")
        c.import_("command-line-args", "commandLineArgs")

        c.cmnt("https://github.com/75lb/command-line-usage")
        c.import_("command-line-usage", "commandLineUsage")

        c.new_line()

        with c.exported_func("parseArgs", []):

            self._generate_help(c)
            self._generate_option_defaults_block(c)
            self._generate_option_struct_block(c)
            self._augment_help_info(c)

            # const rawOptions = commandLineArgs(optionDefinitions)
            # // fill up with defaults the options not provided
            # const opts = {...defaults, ...rawOptions }
            # if (opts.help) {
            #   usage(optionDefinitions, 0)
            # }
            # for (const optName in opts) {
            #   if (opts[optName] == null) {
            #     console.log("Invalid or no option passed for", "--" + optName)
            #     usage(optionDefinitions, 1)
            #   }
            # }
            # return opts

            c.emit("const rawOptions = commandLineArgs(optionDefinitions);")
            c.cmnt("fill up with defaults the options not provided")
            c.emit("const opts = {...defaults, ...rawOptions };")
            with c.if_then("opts.help"):
                c.emit("usage(optionDefinitions, 0);")
            with c.for_in_loop("const optName", "opts"):
                with c.if_then("opts[optName] == null"):
                    c.emit(
                        'console.log("Invalid or no option passed for", "--" + optName);'
                    )
                    c.emit("usage(optionDefinitions, 1);")

            # translate from external to internal name with possible flag inversion
            self._generate_name_translation_block(c)

            self._generate_assing_positionals_block(c)
            self._generate_check_choices_block(c)

            c.emit("return opts;")

        self.to_file(str(c), filename_base + ".mjs")
