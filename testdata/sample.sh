# Usage function
usage() {
    echo "Usage: $0 [options]"
    echo "  input INPUT                : Input TOML file (required)"
    echo "  -o OUTPUT, --output OUTPUT : Output file (default cli_args)"
    echo "  -l LANG, --lang LANG       : Language for the generated code (required)"
    echo "Goes at the end"
    exit 1
}

# check if a valid argument follows
check_valid_arg() {
    case "$2" in
      -*|'') echo "Error: $1 requires a value." >&2
           usage
    esac
}

# Argument parsing function
parse_args() {
    # split --a=xx -b=yy -cde into --a xx -b yy -c -d -e
    # for more unified processing later on
    local i ch arg new_args=""
    for arg in "$@"; do
        case "$arg" in
            --*=*) # convert --aa=xx into --aa xx
                right=${arg#*=}
                left=${arg%="$right"}
                new_args="$new_args $left $right" ;;
            --*)
                new_args="$new_args $arg" ;;
            -*) # convert -abc=yy into -a -b -c yy
                i=1
                while [ "$i" -lt "${#arg}" ]; do
                    ch=$(expr "$arg" : "^.\{$i\}\(.\)")
                    case "${ch}" in
                        =) rest=$(expr "$arg" : "^..\{$i\}\(.*\)")
                           new_args="$new_args $rest"; break ;;
                        *) new_args="$new_args -${ch}" ;;
                    esac
                    i=$((i+1))
                done ;;
            *)  new_args="$new_args $arg" ;;
        esac
    done
    # shellcheck disable=SC2086
    set -- $new_args

    remaining_args=""
    local positional_idx=0
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --output|-o)
                check_valid_arg "$1" "$2";
                output="$2"
                shift ;;
            --lang|-l)
                check_valid_arg "$1" "$2";
                lang="$2"
                shift ;;
            --help|-h)
                usage;;
            --) shift;
                remaining_args="$*"
                break;;
            -*) echo "Unknown option: $1" >&2; usage ;;
            *) # handle positional arguments
                if [ $positional_idx -eq 0 ]; then
                    input="$1"
                else
                    echo "Unexpected positional argument: $1" >&2
                    usage
                fi
                positional_idx=$(( positional_idx + 1 ))
        esac
        shift
    done
}

# Validate arguments
validate_args() {
    if [ -z "$input" ]; then
        echo "Error: input is required" >&2
        usage
    fi
    if [ -z "$lang" ]; then
        echo "Error: --lang is required" >&2
        usage
    fi
    if [ $(expr "|python|bash|" : ".*|$lang|") -eq 0 ]; then
        echo "Error: --lang must be one of: python, bash (got '$lang')" >&2
        usage
    fi
}

# Dump argument values for debug
dump_args() {
    echo "Parsed arguments:"
    echo "input: $input"
    echo "output: $output"
    echo "lang: $lang"
    echo "remaining_args: ${remaining_args[*]}"
}

# Main entry point, parse CLI
get_cli_args() {
    # set defaults
    output=cli_args
    parse_args "$@"
    validate_args
}

# Example of use:
get_cli_args "$@"
dump_args