#!/usr/bin/env node
import * as cli from '../sample0.mjs'

function main() {
  const opts = cli.parseArgs()
  console.log(opts)
}

main()
