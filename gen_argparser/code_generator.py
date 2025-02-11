"""
Few utilities to get fields from toml option dictionary
"""

import json
from typing import List, Optional
import re


class ArgSpec:
    """internally stores an argumen definition as defined by .toml file"""

    def __init__(self, arg: dict):
        self.name: str = arg["name"]
        if self.name.strip().startswith("-") and not self.name.strip().startswith("--"):
            raise RuntimeError(f"name cannot start with a single -, found {self.name}")
        self.clean_name: str = self.name.lstrip("--")
        self.type_: str = arg["type"]
        assert self.type_ in ["flag", "string", "int", "float"]
        self.help_: str = arg["help"]
        short = arg.get("short")
        self.short: str = "" if short is None else short
        self.clean_short = "" if short is None else short.lstrip("-")
        self.dest: str = arg.get("dest", self.clean_name)
        self.multiple: bool = arg.get("multiple", "false") == "true"
        self.has_metavar = arg.get("metavar") is not None
        self.metavar: str = arg.get("metavar", self.clean_name).upper()
        if (choices := arg.get("choices")) is not None:
            self.choices = re.split(r", *", choices)
        else:
            self.choices = None

        if self.type_ == "flag" and self.multiple:
            raise RuntimeError("multiple not supported for flags")

        default = arg.get("default")
        default_known = (
            default is not None or self.type_ == "flag"
        )  # flags are False implicitly

        # required could be specified even for a -- argument
        explicit_required = arg.get("required", "false") == "true"

        self.is_positional = not self.name.startswith("--")
        self.is_required = self.is_positional or explicit_required or not default_known
        self.has_default = not self.is_required

        if not self.has_default:
            self.default = None
            return

        if self.multiple:
            self.default = [
                normalize_default(item, self.type_)
                for item in re.split(r" +", default)
            ]
        else:
            self.default = normalize_default(default, self.type_)

    def get_opt_string(self) -> str:
        """return help string for the option"""
        if self.short == "":
            return f"{self.name} {self.metavar}"
        return ", ".join(
            [f"{self.short} {self.metavar}", f"{self.name} {self.metavar}"]
        )


def normalize_default(default: str, type_: str):
    """default value after cleanups and with propper type"""
    if type_ == "flag":
        assert default in [None, "true", "false"]
        return default == "true"

    assert default is not None
    if type_ == "int":
        return int(default, 0)

    if type_ == "float":
        return float(default)

    assert type_ == "string"
    return default


def double_quote(s: str) -> str:
    """just return input double quoted"""
    return '"' + str(s) + '"'


def single_quote(s: str) -> str:
    """just return input single quoted"""
    return "'" + str(s) + "'"


def _join_transformed_list(lst: list, func: callable, sep: str) -> str:
    return sep.join(func(item) for item in lst)


def double_quote_list(lst: list, sep: str = ", ") -> str:
    """just return input list with each item double quoted"""
    return _join_transformed_list(lst, double_quote, sep)


def single_quote_list(lst: list, sep: str = ", ") -> str:
    """just return input list with each item single quoted"""
    return _join_transformed_list(lst, single_quote, sep)


class CodeGenerator:
    """Base class for code generators."""

    def __init__(self, config: dict):
        self.program_name = config["program"]["name"]
        self.description = config["program"]["description"]
        self.epilog = config["program"].get("epilog", "")
        self.arguments = config["arguments"]
        self.args = [ArgSpec(arg) for arg in config["arguments"]]

    def to_file(self, code: str, filename: str) -> None:
        """dump string to file"""
        if filename in ["-", ""]:
            print(code)
            return
        with open(filename, "w", encoding="utf-8") as fout:
            fout.write(code)

    def generate_code(self, filename_base: str) -> None:
        """Abstract method to generate code. To be implemented by subclasses."""
        raise NotImplementedError(
            "Subclasses must implement generate_code method"
        )
