#include "sample0.h"
#include "argparse.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <math.h>


void reset_options(Options* opts) {
    opts->input = NULL;
    opts->output = NULL;
    opts->verbose = 0;
    opts->enable = 0; // inverted internal polarity
    opts->int_ = INT_MIN;
    opts->float_ = 7.0;
}

int parse_options(int argc, const char ***argv, Options* opts) {
    static const char *const usages[] = {
        "basic [options] positionals [[--] args]",
        "basic [options] positionals ",
        NULL,
    };
    reset_options(opts);
    struct argparse_option options[] = {
        OPT_HELP(),
        OPT_STRING('\0', "output", &opts->output, "output file path (required)", NULL, 0, 0),
        OPT_BOOLEAN('v', "verbose", &opts->verbose, "enable verbose mode (default 0)", NULL, 0, 0),
        OPT_BOOLEAN('\0', "disable", &opts->enable, "disable something (default 0)", NULL, 0, 0),
        OPT_INTEGER('i', "int", &opts->int_, "just an integer number (required)", NULL, 0, 0),
        OPT_FLOAT('f', "float", &opts->float_, "just a float number (default 7.0)", NULL, 0, 0),
        OPT_END(),
    };
    struct argparse argparse;
    argparse_init(&argparse, options, usages, 0);
    argparse_describe(&argparse, 
        "\nExample CLI Parser using TOML",
        "\nPositional arguments:"
        "\n    input                 input file path\n"
        "\nExample: sample0 input.txt --output output.txt --verbose -i 1 -f 2.0"
    );
    argc = argparse_parse(&argparse, argc, *argv);
    // positionals
    if (argc >= 1) {
        opts->input = (*argv)[0];
        (*argv)++; argc--;
    } else {
        printf("ERROR: expecting positional argument 'input'\n");
        argparse_usage(&argparse);
        exit(1);
    }
    opts->enable = 1 - opts->enable;  // invert back
    // check if --output has been given
    if (opts->output == NULL) {
        printf("ERROR: expecting required argument '--output'\n");
        argparse_usage(&argparse);
        exit(1);
    }
    // check if --int has been given
    if (opts->int_ == INT_MIN) {
        printf("ERROR: expecting required argument '--int'\n");
        argparse_usage(&argparse);
        exit(1);
    }
    return argc;
}

void dump_options(Options *opts) {
    printf("input: %s\n", opts->input);
    printf("output: %s\n", opts->output);
    printf("verbose: %d\n", opts->verbose);
    printf("enable: %d\n", opts->enable);
    printf("int_: %d\n", opts->int_);
    printf("float_: %f\n", opts->float_);
}
