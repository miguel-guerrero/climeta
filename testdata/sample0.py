"""CLI argument parsing"""

import argparse


def parse_args() -> tuple:
    """CLI argument parsing entry point"""
    parser = argparse.ArgumentParser(
        description="Example CLI Parser using TOML",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Example: sample0 input.txt --output output.txt --verbose -i 1 -f 2.0",
    )
    parser.add_argument(
        "input",
        type=str,
        help="input file path",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="output file path",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable verbose mode",
    )
    parser.add_argument(
        "--disable",
        action="store_false",
        dest="enable",
        help="disable something",
    )
    parser.add_argument(
        "-i",
        "--int",
        type=int,
        dest="int_",
        required=True,
        help="just an integer number",
    )
    parser.add_argument(
        "-f",
        "--float",
        type=float,
        dest="float_",
        default=7.0,
        help="just a float number",
    )

    return parser.parse_known_args()  # args, unknown


if __name__ == "__main__":
    args, unknown = parse_args()
    print(f"Parsed arguments: {args}")
    if unknown:
        print(f"Unknown arguments: {unknown}")
