# Usage function
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "The description of the program"
    echo ""
    echo "positional arguments:"
    echo "  input INPUT                : input TOML file (required)"
    echo ""
    echo "options:"
    echo '  -h, --help                 : show this help message and exit'
    echo '  -o OUTPUT, --output OUTPUT : output file (default "cli_args")'
    echo '  -l LANG, --lang LANG       : language for the generated code (required)'
    echo ""
    echo "Goes at the end"
    exit "$1"
}

# check if a valid argument follows
check_valid_arg() {
    case "$2" in
        -*|'')
            echo "ERROR: $1 requires a value." >&2
            usage 1
            ;;
    esac
}

# Argument parsing function
parse_args() {
    # split --a=xx -b=yy -cde into --a xx -b yy -c -d -e
    # for more unified processing later on
    local i ch arg
    local -a new_args
    for arg in "$@"; do
        case "$arg" in
            --*=*) # convert --aa=xx into --aa xx
                right=${arg#*=}  # remove up to first =
                left=${arg%="$right"}  # remove right hand side
                new_args+=("$left" "$right")
                ;;
            --*)
                new_args+=("$arg")
                ;;
            -*) # convert -abc=yy into -a -b -c yy
                i=1
                while [ "$i" -lt "${#arg}" ]; do
                    # Get character at position i (0 based)
                    ch=$(expr "$arg" : "^.\{$i\}\(.\)")
                    case "${ch}" in
                        =) rest=$(expr "$arg" : "^..\{$i\}\(.*\)")
                           new_args+=("$rest"); break ;;
                        *) new_args+=("-${ch}") ;;
                    esac
                    i=$((i+1))
                done
                ;;
            *)
                new_args+=("$arg")
                ;;
        esac
    done
    set -- "${new_args[@]}"

    remaining_args=""
    local positional_idx=0
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --output|-o)
                check_valid_arg "$1" "$2"
                output="$2"
                shift;;
            --lang|-l)
                check_valid_arg "$1" "$2"
                lang="$2"
                shift;;
            --help|-h)
                usage 0
                ;;
            --)
                shift
                remaining_args="$*"
                break
                ;;
            -*)
                echo "ERROR: Unknown option: $1" >&2
                usage 1
                ;;
            *) # handle positional arguments
                if [ $positional_idx -eq 0 ]; then
                    input="$1"
                else
                    echo "ERROR: Unexpected positional argument: $1" >&2
                    usage 1
                fi
                positional_idx=$(( positional_idx + 1 ))
                ;;
        esac
        shift
    done
}

# Validate arguments
validate_args() {
    if [ -z "$input" ]; then
        echo "ERROR: input is required" >&2
        usage 1
    fi
    if [ -z "$lang" ]; then
        echo "ERROR: --lang is required" >&2
        usage 1
    fi
    local match
    match=$(expr "|python|bash|" : ".*|$lang|")
    if [ "$match" -eq 0 ]; then
        echo "ERROR: --lang must be one of: python, bash (got '$lang')" >&2
        usage 1
    fi
}

# Dump argument values for debug
dump_args() {
    echo "Parsed arguments:"
    echo "input: $input"
    echo "output: $output"
    echo "lang: $lang"
    echo "remaining_args:"
    for arg in $remaining_args; do
        echo "  $arg"
    done
}

# Main entry point, parse CLI
get_cli_args() {
    # set defaults
    output="cli_args"
    parse_args "$@"
    validate_args
}

# Example of use:
# get_cli_args "$@"
# dump_args