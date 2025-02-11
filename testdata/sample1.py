"""CLI argument parsing"""

import argparse


def parse_args() -> tuple:
    """CLI argument parsing entry point"""
    parser = argparse.ArgumentParser(
        description="The description of the program",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Goes at the end",
    )
    parser.add_argument(
        "input",
        type=str,
        help="input TOML file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="cli_args",
        help="output file",
    )
    parser.add_argument(
        "-l",
        "--lang",
        type=str,
        required=True,
        choices=['python', 'bash'],
        help="language for the generated code",
    )

    return parser.parse_known_args()  # args, unknown


if __name__ == "__main__":
    args, unknown = parse_args()
    print(f"Parsed arguments: {args}")
    if unknown:
        print(f"Unknown arguments: {unknown}")
