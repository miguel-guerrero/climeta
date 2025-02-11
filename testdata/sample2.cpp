#include "sample2.hpp"
#include <iostream>
#include <set>


cxxopts::ParseResult parse_options(int argc, const char **argv, Options* opts) {
    cxxopts::Options options("Example program", "The description of the program");
    // define all options
    options.add_options()
        ("h,help", "show this help message and exit")
        ("input", "input TOML file (required)", cxxopts::value<std::string>())
        ("o,output", "output file", cxxopts::value<std::string>()->default_value("cli_args"))
        ("l,lang", "language for the generated code (required)", cxxopts::value<std::string>())
        ("f,files", "pass any number of files", cxxopts::value<std::vector<std::string>>()->default_value("a.txt,b.txt"))
    ;
    // declare positionals
    options.parse_positional("input");

    cxxopts::ParseResult result = options.parse(argc, argv);
    if (result.count("help")) {
        std::cout << options.help() << std::endl;
        std::cout << "positional arguments:\n";
        std::cout << "  input             " << "input TOML file (required)\n";
        std::cout << "\nGoes at the end" << std::endl;
        exit(0);
    }
    // Fill-up output struct
    opts->input = result["input"].as<std::string>();
    opts->output = result["output"].as<std::string>();
    opts->lang = result["lang"].as<std::string>();
    opts->files = result["files"].as<std::vector<std::string>>();
    // check choices
    std::set<std::string> lang_valid{"python", "bash"};
    if (lang_valid.find(opts->lang) == lang_valid.end()) {
        std::cout << "ERROR: 'lang' must be one of 'python', 'bash'" << std::endl;
        exit(1);
    }
    return result;
}

void dump_options(const Options &opts) {
    std::cout << "input: " << opts.input << "\n";
    std::cout << "output: " << opts.output << "\n";
    std::cout << "lang: " << opts.lang << "\n";
    std::cout << "files:\n";
    for (const auto& item : opts.files) {
        std::cout << "  " << item << "\n";
    }
}
