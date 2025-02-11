#!/bin/bash

# source the CLI parsing functions
source "$(dirname $0)"/../sample0.sh

# Example of use:
get_cli_args "$@"
dump_args
