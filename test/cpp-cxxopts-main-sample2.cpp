#include "../sample2.hpp"

int main(int argc, const char** argv)
{
    Options opts;

    parse_options(argc, argv, &opts);
    dump_options(opts);

    return 0;
}
