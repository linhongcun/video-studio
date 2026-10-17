const path = require('node:path');
const fs = require('node:fs');
const {buildSync} = require('esbuild');
const output = path.resolve('out/ep02-verify.cjs');
try {
  buildSync({
    entryPoints: ['scripts/verify-storyboard.tsx'],
    bundle: true,
    platform: 'node',
    packages: 'external',
    outfile: output,
    logLevel: 'error',
  });
  require(output);
} finally {
  fs.rmSync(output, {force: true});
}
