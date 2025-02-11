#include "sample0.hpp"
#include <iostream>


cxxopts::ParseResult parse_options(int argc, const char **argv, Options* opts) {
    cxxopts::Options options("example", "Example CLI Parser using TOML");
    // define all options
    options.add_options()
        ("h,help", "show this help message and exit")
        ("input", "input file path (required)", cxxopts::value<std::string>())
        ("output", "output file path (required)", cxxopts::value<std::string>())
        ("v,verbose", "enable verbose mode (default: false)", cxxopts::value<bool>())
        ("disable", "disable something (default: false)", cxxopts::value<bool>())
        ("i,int", "just an integer number (required)", cxxopts::value<int>())
        ("f,float", "just a float number", cxxopts::value<float>()->default_value("7.0"))
    ;
    // declare positionals
    options.parse_positional("input");

    cxxopts::ParseResult result = options.parse(argc, argv);
    if (result.count("help")) {
        std::cout << options.help() << std::endl;
        std::cout << "positional arguments:\n";
        std::cout << "  input             " << "input file path (required)\n";
        std::cout << "\nExample: sample0 input.txt --output output.txt --verbose -i 1 -f 2.0" << std::endl;
        exit(0);
    }
    // Fill-up output struct
    opts->input = result["input"].as<std::string>();
    opts->output = result["output"].as<std::string>();
    opts->verbose = result["verbose"].as<bool>();
    opts->enable = !result["disable"].as<bool>(); // invert back
    opts->int_ = result["int"].as<int>();
    opts->float_ = result["float"].as<float>();
    return result;
}

void dump_options(const Options &opts) {
    std::cout << "input: " << opts.input << "\n";
    std::cout << "output: " << opts.output << "\n";
    std::cout << "verbose: " << opts.verbose << "\n";
    std::cout << "enable: " << opts.enable << "\n";
    std::cout << "int_: " << opts.int_ << "\n";
    std::cout << "float_: " << opts.float_ << "\n";
}
