#include "sample1.h"
#include "argparse.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <math.h>


void reset_options(Options* opts) {
    opts->input = NULL;
    opts->output = "cli_args";
    opts->lang = NULL;
}

static int set_includes(const char* words[], const char* test_word) {
    while (*words != NULL) {
        if (strcmp(*words++, test_word) == 0) {
            return 1;
        }
    }
    return 0;
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
        OPT_STRING('o', "output", &opts->output, "output file (default 'cli_args')", NULL, 0, 0),
        OPT_STRING('l', "lang", &opts->lang, "language for the generated code (required)", NULL, 0, 0),
        OPT_END(),
    };
    struct argparse argparse;
    argparse_init(&argparse, options, usages, 0);
    argparse_describe(&argparse, 
        "\nThe description of the program",
        "\nPositional arguments:"
        "\n    input                 input TOML file\n"
        "\nGoes at the end"
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
    // check if --lang has been given
    if (opts->lang == NULL) {
        printf("ERROR: expecting required argument '--lang'\n");
        argparse_usage(&argparse);
        exit(1);
    }
    // check choices
    const char *lang_valid[] = {"python", "bash", NULL};
    if (!set_includes(lang_valid, opts->lang)) {
        printf("ERROR: 'lang' must be one of 'python', 'bash'\n");
        exit(1);
    }
    return argc;
}

void dump_options(Options *opts) {
    printf("input: %s\n", opts->input);
    printf("output: %s\n", opts->output);
    printf("lang: %s\n", opts->lang);
}
