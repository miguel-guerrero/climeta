#pragma once

#include "cxxopts.hpp"
struct Options {
    std::string output;
    std::string lang;
    // positionals
    std::string input;
};

cxxopts::ParseResult parse_options(int argc, const char** argv, Options* opts);
void dump_options(const Options& opts);