# Climeta (CLI - meta generator)

A Command Line Interpreter (CLI) meta generator for several languates

This tool is a Command Line Arguments (CLI) parser generator that uses a single point of definition (a `.toml` file) to generate multiple collaterals. It supports generating code for several languages, as of today:

- Python (using standard library `argparse`)
- Bash (self contained)
- C (using [argparse](https://github.com/cofyc/argparse) library)
- C++ (using [cxxopts](https://github.com/jarro2783/cxxopts) library)
- JavaScript (for `node`, using [command-line-args](https://www.npmjs.com/package/command-line-args) and [command-line-usage](https://www.npmjs.com/package/command-line-usage) packages)

The intent is to keep adding support anything that could be useful over time from a common definition to allow: 
- Moving from one language to another without having to redo the CLI parsing (e.g move from `bash` to `python` is something that happens to me frequently).
- Simplify the generation of repetitive code with consistent level of quality.
- In some cases, augment the capanilities of the underlaying used libraries to provide a consistent set of features across languages (for example show default values on help message even if the underlaying library doesn't support it).
- Get added collaterals. For example (TBD)
  - Command line auto-completion.
  - Automated GUI generation.
 
## Features supported

| Feature                       |   python    |  c-argparse | cpp-cxxopts |  bash     | js-cla   |
|-------------------------------|-------------|-------------|-------------|-----------|----------|
| positionals                   | Y           | Y           | Y           | Y         | Y        |
| short options can be collided | Y           | Y           | Y           | Y         | Y        |
| generated help                | Y           | Y           | Y           | Y         | Y        |
| enforces required arguments   | Y           | Y           | Y           | Y         | Y        |
| flags can have true default   | Y           | Y           | Y           | Y         | Y        |
| typed variables on output     | Y           | Y           | Y           | n/a       | n/a      | 
| help shows default values     | Y           | Y           | Y           | Y         | Y        |
| "choices" arguments           | Y           | Y           | Y           | Y         | Y        |
| vectors/list arguments        | Y           | -           | Y           | Y         | Y        |
| collect extra args (after --) | -           | -           | -           | Y         | -        |
| metavar for help              | Y           | -           | -           | -         | -        |
| --no flags                    | -(could)    | Y           | -           | -         | -        |
| extra external dependencies   | -           | argparse    | cxxopts     | -         | cla/clu* |

*cla/clu = `command-line-args` / `command-line-usage` npm packages

External dependencies have all permissive open source licenses.

The `.toml` file can be generated manually or through a provided web interface.

## TOML file format description

The TOML file contains a `program` section with general information to be included in the help dump, plus a per-argument section (as many arguments as needed:

Here is a brief description of the fields. Note that most fields are strings:

- program
  - `name: string`. The name of the program as to be shown in the help dump.
  - `description: string`. A description of the program for help dump.
  - `epilog: string`. Goes in the help dump after the automatically generated description of the arguments.
 
- for each argument:
  - `name: string`. If the name starts with `--` it will be considered a `long option` of the type `--option=value` (or `--option value`). If not preceded by `--` it will be considered a positional argument.
  - `type: string`. One of:
     - `"string"`
     - `"int"`
     - `"float"`
     - `"flag"` (a boolean defaulting to `"false"`)
  - `help: string`. A description of the argument (one liner style).
  - `short: Optional[string]`. If `name` starts with `--` (is a long option) you can provide a short alias version of it here (for example `"-v"` for an argument whose name was `"--verbose"`)
  - `choices: Optional[List[string]]`. If given, it will restrict the set of values the argument can take to the choices provided e.g. `choices = ["choice1", "choice2"]` would allow only those two values.
  - `dest: Optional[string]`. The name of the variable holding the result of this argument. If not given it will be assumed to be `name` without any preceding "--" if present
  - `meta: Optional[string] defaulting to name wihtout preceeding -- if any`. A name used for the generation of the argument help line. E.g. --value VALUE for default meta is shown in help dump, but if meta = "INT" the help string will present `--value INT` for the given argument.

  - `multiple: Optional[bool-string] defaulting to "false"`. A `bool-string` is a string containing `"true"` or `"false"`. If "true" the option can be given multiple times or as a slist of values (exact syntax is target language dependent)
  - `default: string`. The default value for the argument.
    - Flags (arguments of `type = "flag"`) default to `"false"`, but other types have no default predefined.
    - Positional arguments (always required) and arguments flaged as required must not have a default.
    - Default should be a string even for types like `"int"` or `"float"` (e.g. "1", "2.7").
    
## Sample TOML file

And an example (`args0.toml` used in the following section)

```markdown
[program]
name = "example"
description = "Example CLI Parser using TOML"
epilog = "Example: sample0 input.txt --output output.txt --verbose -i 1 -f 2.0"

[[arguments]]
name = "input"
type = "string"
help = "input file path"

[[arguments]]
name = "--output"
type = "string"
help = "output file path"

[[arguments]]
name = "--verbose"
short = "-v"
type = "flag"
help = "enable verbose mode"

[[arguments]]
name = "--disable"
dest = "enable"
type = "flag"
default = "true"
help = "disable something"

[[arguments]]
name = "--int"
short = "-i"
type = "int"
dest = "int_"
help = "just an integer number"

[[arguments]]
name = "--float"
short = "-f"
default = "7.0"
type = "float"
dest = "float_"
help = "just a float number"
```

## Usage example

```
$ ./gen_argparser.py args0.toml --lang bash --output sample0.sh

$ test/bash-main-sample0.sh input.txt --output output.txt --verbose -i 1 -f 2.0 -- a b c                                                               Parsed arguments:
input: input.txt
output: output.txt
verbose: 1
enable: 1
int_: 1
float_: 2.0
remaining_args:
  a
  b
  c                    
```
