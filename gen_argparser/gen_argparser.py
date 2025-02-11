"""
Common functions to drive CLI code generation from toml def file
"""

import tomllib
from .python_generator import PythonCodeGenerator
from .bash_generator import BashCodeGenerator
from .c_argparse_generator import CArgparseCodeGenerator
from .cpp_cxxopts_generator import CppCxxoptsCodeGenerator
from .js_cla_generator import JavaScriptCommandLineArgsCodeGenerator


def parse_cli_spec(file_path: str) -> dict:
    """Parse the CLI specification from a TOML file."""
    with open(file_path, "rb") as f:
        config = tomllib.load(f)

    # Return the parsed configuration
    return config


def generate_cli_code(file_path: str, language: str, output: str) -> None:
    """Generates CLI parsing code for the specified language."""
    config = parse_cli_spec(file_path)

    # Choose the appropriate code generator
    if language == "python":
        generator = PythonCodeGenerator(config)
    elif language == "bash":
        generator = BashCodeGenerator(config)
    elif language == "c-argparse":
        generator = CArgparseCodeGenerator(config)
    elif language == "cpp-cxxopts":
        generator = CppCxxoptsCodeGenerator(config)
    elif language == "js-cla":
        generator = JavaScriptCommandLineArgsCodeGenerator(config)
    else:
        raise ValueError(f"Unsupported language: {language}")

    # Generate and print the code
    generator.generate_code(output)
