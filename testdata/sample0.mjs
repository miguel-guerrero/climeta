// https://github.com/75lb/command-line-args
import commandLineArgs from 'command-line-args';
// https://github.com/75lb/command-line-usage
import commandLineUsage from 'command-line-usage';

export function parseArgs() {
  function usage(optionDefinitions, rc = 0) {
    const usageText = commandLineUsage([{
      header: "Header for help",
      content: "Description for help",
    }, {
      header: "Options",
      optionList: optionDefinitions,
    }, {
      content: "Epilog"
    }]);
    console.log(usageText);
    process.exit(rc);
  };

  // Defaults for each of the options
  const defaults = {
    output: null,
    verbose: false,
    disable: false, // inverted internal polarity
    int: null,
    float: 7.0,
  };
  const optionDefinitions = [
    {
      name: 'help',
      description: 'show this help message and exit',
      alias: 'h',
      type: Boolean
    },
    {
      name: 'output',
      description: 'output file path',
      type: String
    },
    {
      name: 'verbose',
      description: 'enable verbose mode',
      alias: 'v',
      type: Boolean
    },
    {
      name: 'disable',
      description: 'disable something',
      type: Boolean
    },
    {
      name: 'int',
      description: 'just an integer number',
      alias: 'i',
      type: Number
    },
    {
      name: 'float',
      description: 'just a float number',
      alias: 'f',
      type: Number
    },
    {
      name: 'positionals',
      description: 'positional arguments (can omit --positionals) Corresponding to:\n>> {bold input} : input file path',
      type: String,
      multiple: true,
      defaultOption: true
    },
  ];
  // append default to help string
  for (const opt of optionDefinitions) {
    const default_ = defaults[opt.name];
    if (typeof default_ !== "undefined") {
      opt.description += default_ == null ? " (required)" : ` (default ${default_})`;
    }
  }
  const rawOptions = commandLineArgs(optionDefinitions);
  // fill up with defaults the options not provided
  const opts = {...defaults, ...rawOptions };
  if (opts.help) {
    usage(optionDefinitions, 0);
  }
  for (const optName in opts) {
    if (opts[optName] == null) {
      console.log("Invalid or no option passed for", "--" + optName);
      usage(optionDefinitions, 1);
    }
  }
  // translate from external to internal name
  opts.enable = !opts.disable;  // invert
  delete opts.disable
  opts.int_ = opts.int;
  delete opts.int
  opts.float_ = opts.float;
  delete opts.float
  // Handle positionals
  const exp_positionals = 1
  const num_positionals = (typeof opts.positionals === "undefined") ? 0 : opts.positionals.length;
  if (num_positionals != exp_positionals) {
    console.log(`Expecting ${exp_positionals} positional argument(s), but got ${num_positionals}`);
    usage(optionDefinitions, 1);
  }
  opts.input = opts.positionals[0];
  delete opts.positionals;
  return opts;
};
