#include "../sample0.h"
#include <stdio.h>

int main(int argc, const char **argv) {
    Options opts;

    argc = parse_options(argc, &argv, &opts);
    dump_options(&opts);

    // positionals
    if (argc != 0) {
        printf("argc: %d\n", argc);
        int i;
        for (i = 0; i < argc; i++) {
            printf("argv[%d]: %s\n", i, *(argv + i));
        }
    }
    return 0;
}
