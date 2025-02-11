#!/usr/bin/env python3
"""
Drive program to generate CLI parser generator code for different
languages

- the input is in a .toml file, with common format for all languages
"""

import argparse
import os
from gen_argparser import generate_cli_code


def main():
    """CLI for CLI parser generator"""
    parser = argparse.ArgumentParser(
        description="The description of the program",
        epilog="Example: ./climeta.py args1.toml -l bash -o sample1",
    )

    parser.add_argument(
        "input",
        type=str,
        help="Input TOML file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file(s) base WITHOUT extension, if not given it will use stdout",
        required=False,
        default="",
    )
    parser.add_argument(
        "-l",
        "--lang",
        type=str,
        help="Language for the generated code",
        required=True,
        choices=["python", "bash", "c-argparse", "cpp-cxxopts", "js-cla"],
    )

    args, unknown = parser.parse_known_args()
    if unknown:
        print(f"Unknown arguments: {unknown}")

    base_name, _extension = os.path.splitext(args.output)
    generate_cli_code(args.input, args.lang, base_name)


if __name__ == "__main__":
    main()
